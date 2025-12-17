from flask import Flask, render_template , request, flash ,redirect
import pymysql
from flask_login import LoginManager, login_user , logout_user, login_required
from dynaconf import Dynaconf

app = Flask(__name__)

config = Dynaconf(settings_file=["settings.toml"])


app.secret_key = config.secret_key

login_manager = LoginManager( app )

class User:
    is_authenticated = True
    is_active = True
    is_anonymous = False

    def __init__(self, result):
        self.id = result['ID']
        self.name = result['Name']
        self.email = result['Email']
        self.address = result['Address']
    
    def get_id(self):
        return str(self.id)
    @login_manager.user_loader
    def load_user(user_id):
        connection = conncet_db()

        cursor = connection.cursor()

        cursor.execute("SELECT * FROM `User` WHERE `ID` = %s", (user_id))

        result = cursor.fetchone()

        connection.close()

        if result is None:
            return None
        
        return User(result)


def conncet_db():
    conn = pymysql.connect(
        host="db.steamcenter.tech",
        user="lpustam",
        password=config.password,
        database="lpustam_marqen",
        autocommit=True,
        cursorclass=pymysql.cursors.DictCursor
    )

    return conn


@app.route("/")
def index():
    return render_template("homepage.html.jinja")

@app.route("/register", methods = ['POST', 'GET'])
def register():
    if request.method == 'POST':

        name =request.form ["name"]

        email = request.form ["email"]

        password = request.form ["password"]

        confirm_password = request.form ['confirm_password']

        address = request.form ['address']

        if password != confirm_password:
            flash("passowrd doesn't match")
        elif len(password) < 6:
            flash("password is too short")
        else:
            connection = conncet_db()

            cursor = connection.cursor()
        try:
            cursor.execute(
            """
            INSERT INTO `User` ( `Name`, `Password`,`Email`,`Address`)
            VALUES (%s, %s, %s, %s)
            """, (name, password, email, address))
        except pymysql.err.IntegrityError:
            flash("email already exists")
        else:  
            return redirect ("/login")
        
    return render_template("register.html.jinja")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        connection = conncet_db()

        cursor = connection.cursor()

        cursor.execute( "SELECT * FROM `User` WHERE `Email` = %s " , (email)) 

        result = cursor.fetchone()

        connection.close()

        if result is None:
            flash("No user found")
        elif password != result['Password']:
            flash("Incorrect password")
        else:
            login_user(User ( result ) )
            return redirect ("/browse")
        

    return render_template("login.html.jinja")

@app.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("Successfully logged out")
    return redirect ("/login")


@app.route("/browse")
def browse():
    connection = conncet_db()

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM `Product` ")

    result = cursor.fetchall()

    connection.close()

    return render_template("browse.html.jinja", products=result)

@app.route("/product/<product_id>")
def product_page(product_id):

    connection = conncet_db()

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM `Product` WHERE `ID` = %s", (product_id))

    result = cursor.fetchone()

    connection.close()

    
    return render_template("product.html.jinja", product = result)
