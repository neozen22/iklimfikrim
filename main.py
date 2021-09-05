from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, jsonify
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

app = Flask(__name__)


def fetch_articles():
    with open("static/data/articles.json", encoding="utf-8") as articles_file:
        return json.load(articles_file)

# articles = fetch_articles()

#SQL CONFIGURATION
# app.config["MYSQL_HOST"] = "localhost"
# app.config["MYSQL_USER"] = "root"
# app.config["MYSQL_PASSWORD"] = ""
# app.config[""]
# app.config["MYSQL_CURSORCLASS"] = "DictCursor"

# mysql = flask_mysqldb.MySQL(app)

@app.route("/")
def hello_world():
    articles = fetch_articles()
    
    return render_template("index.html", articles=articles)



@app.route("/dashboard")
def dashboard():
    articles = fetch_articles()
    return render_template("dashboard.html", articles = articles)

@app.route("/register", methods= ["GET", "POST"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST":
        pass
    else:
        return render_template("register.html", form= form)

@app.route("/article/<string:id>")
def article(id):
    with open(f"static/data/article_assets/{id}/article.html","r", encoding="utf-8") as sj:
        article_content = sj.read()
    return render_template("articleholder.html",article_content=article_content)



if __name__ == "__main__":
    app.run(use_reloader=True, debug=True)
