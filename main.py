from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
import os
import json
import flask_mysqldb

class RegisterForm(Form):
    name = StringField("İsim Soyisim (Mehmet Aydın)", validators=[validators.DataRequired(message="Burayı boş bırakmayınız")])
    username = StringField("Kullanıcı Adı", validators=[])
    password = PasswordField("Şifre", validators=[validators.Length(1, 1, "Şifrede boşluk kullanmayınız"), validators.EqualTo("confirm", "Şifre eşleşmiyor")])
    confirm = PasswordField("Şifre Doğrula")

with open("data/articles.json") as articles_file:
    articles = json.load(articles_file)

for i in articles:
    print(i)



app = Flask(__name__)

#SQL CONFIGURATION
# app.config["MYSQL_HOST"] = "localhost"
# app.config["MYSQL_USER"] = "root"
# app.config["MYSQL_PASSWORD"] = ""
# app.config[""]
# app.config["MYSQL_CURSORCLASS"] = "DictCursor"

# mysql = flask_mysqldb.MySQL(app)

@app.route("/")
def hello_world():
    return render_template("index.html", articles=[i for i in range(10)])



@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", articles = articles)

@app.route("/register", methods= ["GET", "POST"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST":
        pass
    else:
        return render_template("register.html", form= form)

if __name__ == "__main__":
    app.run(use_reloader=True, debug=True)
