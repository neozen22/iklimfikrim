from flask import Flask, render_template, flash, redirect, url_for, session, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
import os

app = Flask(__name__)

sql = MySQL()


@app.route("/")
def hello_world():
    return render_template("index.html", articles=[i for i in range(10)])

@app.route("/create")
def create():
    return render_template("create.html")

if __name__ == "__main__":
    app.run(use_reloader=True, debug=True)
