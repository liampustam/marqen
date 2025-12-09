from flask import Flask, render_template

import pymysql

from dynaconf import Dynaconf

app = Flask(__name__)

config = Dynaconf(settings_file=["settings.toml"])

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

@app.route("/")
def browse():
    return render_template("browse.html.jinja")