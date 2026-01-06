from flask import Flask, render_template , request, flash ,redirect, abort
import pymysql
from flask_login import LoginManager, login_user , logout_user, login_required, current_user
from dynaconf import Dynaconf

app = Flask(__name__)

config = Dynaconf(settings_file=["settings.toml"])


app.secret_key = config.secret_key

login_manager = LoginManager( app )
login_manager.login_view = '/login'

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
        connection = connect_db()

        cursor = connection.cursor()

        cursor.execute("SELECT * FROM `User` WHERE `ID` = %s", (user_id))

        result = cursor.fetchone()

        connection.close()

        if result is None:
            return None
        
        return User(result)


def connect_db():
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
            connection = connect_db()

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

        connection = connect_db()

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
    connection = connect_db()

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM `Product` ")

    result = cursor.fetchall()

    connection.close()

    return render_template("browse.html.jinja", products=result)

@app.route("/product/<product_id>")
def product_page(product_id):

    connection = connect_db()

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM `Product` WHERE `ID` = %s", (product_id))

    result = cursor.fetchone()

    connection.close()
    
    if result is None:
        abort(404)

    
    return render_template("product.html.jinja", product = result)

@app.route("/product/<product_id>/add_to_cart", methods =['POST'])
@login_required
def add_to_cart(product_id):

    quantity = request.form["qty"]

    connection = connect_db()
 
    cursor = connection.cursor()

    cursor.execute(
        """INSERT INTO `Cart` (`Quantity`, `ProductID`,`UserID`)  
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
        `Quantity` = `Quantity` + %s
        """, (quantity, product_id, current_user.id, quantity))

    connection.close()
    return redirect("/cart")

@app.route ("/cart")
@login_required
def cart():
    connection = connect_db()

    cursor = connection.cursor()

    cursor.execute(
        """SELECT * FROM `Cart` 
        Join `Product` ON `Cart`.`ProductID` = `Product`.`ID` WHERE `Cart`.`UserID` = %s""", (current_user.id,))

    result = cursor.fetchall()

    connection.close()

    total = 0
    for item in result:
        total += item['Price'] * item['Quantity']

    return render_template("cart.html.jinja", cart=result, total=total)

@app.route("/cart/<product_id>/remove", methods=['POST'])
@login_required
def remove_from_cart(product_id):

    connection = connect_db()

    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM `Cart`
        WHERE `ProductID` = %s AND `UserID` = %s
  """, (product_id, current_user.id))
    
    connection.close()

    return redirect ("/cart")



@app.route("/cart/<product_id>/update_qty", methods=['POST'])
@login_required
def update_cart(product_id):
    new_qty = request.form['qty']

    connection = connect_db()

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE `Cart`
        SET `Quantity` = %s
        WHERE `ProductID` = %s AND `UserID` = %s
  """, (new_qty, product_id, current_user.id))
    
    connection.close()

    return redirect ("/cart")


