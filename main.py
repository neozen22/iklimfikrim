from enum import unique
from inspect import Parameter
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, jsonify
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, FileField, SubmitField
from passlib.hash import sha256_crypt
import os
import json
from werkzeug.utils import secure_filename
import datetime
import logging
import werkzeug
from flask_sqlalchemy import SQLAlchemy
import jwt
import uuid
import hashlib

class RegisterForm(Form):
    name = StringField("İsim Soyisim (Mehmet Aydın)", validators=[validators.DataRequired(message="Burayı boş bırakmayınız")])
    username = StringField("Kullanıcı Adı", validators=[])
    password = PasswordField("Şifre", validators=[validators.Length(1, 1, "Şifrede boşluk kullanmayınız")])
    confirm = PasswordField("Şifre Doğrula", validators=[validators.EqualTo("password", "Şifre eşleşmiyor")])

class LoginForm(Form):
    username = StringField("Kullanıcı Adı")
    password = PasswordField("Şifre")


class CreateForm(Form):
    title = StringField("", validators=[validators.DataRequired(message="Burayı Boş Bırakmayınız")])
    cover = FileField(label="")

class EditForm(Form):
    change_title = StringField("Yeni Başlık")
    content = TextAreaField("İçerik")

class Dashboardform(Form):
    delete = SubmitField("Sil")
    hide = SubmitField("Sakla")


basedir = os.path.abspath(os.path.dirname(__file__))




app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
app.secret_key = "sjmiderimbruhmuanlamadimkardesnediyeyimsende"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dbdir/test.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
class User(db.Model):
    _id = db.Column(db.String(), primary_key= True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(), unique=False, nullable= False)
    name = db.Column(db.String(80), unique=False, nullable= True)
    admin = db.Column(db.Boolean)
    def __init__(self,_id, username , password, name, admin) -> None:
        self._id = _id
        self.username = username
        self.password = password
        self.name = name
        self.admin = admin

# photos = UploadSet('photos', IMAGES)
# configure_uploads(app, photos)name
# patch_request_class(app)


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

def write_json(new_data, file_number,filename='static/data/articles.json'):
    with open(filename,'r+', encoding='utf-8') as file:
          # First we load existing data into a dict.
        file_data = json.load(file)

        file_data[str(file_number)]= new_data
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent = 4)

@app.route("/")
def hello_world():
    articles = fetch_articles()
    
    return render_template("index.html", articles=articles)



@app.route("/dashboard", methods=["GET", "POST"] )
def dashboard():
    with open("static/data/articles.json", "r+", encoding="utf-8") as a:
        data = json.load(a)
        if request.method == "POST":
            try:
                if request.form["delete"]:
                    deleted_data= request.form["delete"]
                    delete_path = f"{basedir}/static/data/article_assets/{deleted_data}"
                    del data[request.form["delete"]]
                    files_in_dir = os.listdir(delete_path)
                    for file in files_in_dir:                  # loop to delete each file in folder
                        os.remove(f'{delete_path}/{file}')
                    os.rmdir(delete_path)
            except:
                
                try:
                    if request.form["hide"]:
                        if (data[request.form["hide"]]["hidden"]):
                            data[request.form["hide"]]["hidden"] = False

                        else:
                            data[request.form["hide"]]["hidden"] = True
                except:
                    pass
                
            a.seek(0)
            json.dump(data, a, indent=4)
            a.truncate()

            
    
    form = Dashboardform(request.form)
    articles = fetch_articles()
    return render_template("dashboard.html", articles= articles, form=form)

@app.route("/register", methods= ["GET", "POST"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST":
        user = User(_id=uuid.uuid4().hex, username=form.username.data, password=hashlib.sha256(b"form.password.data").hexdigest(), name=form.name.data, admin=False)
        db.session.add(user)
        db.session.commit()
        return redirect("/register")
    else:
        return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
        found_user = (User.query.filter_by(username=form.username.data)).delete()
        print(found_user.password)
        return redirect("/login")

    else:
        return render_template("login.html", form=form)
@app.route("/article/<string:id>")
def article(id):
    try:
        with open(f"static/data/article_assets/{id}/article.html","r", encoding="utf-8") as sj:
            article_content = sj.read()
            return render_template("articleholder.html",article_content=article_content)
    except FileNotFoundError:
        return render_template("404.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")



@app.route("/create", methods=["GET", "POST"])
def create_article():
    form = CreateForm(request.form)
    if request.method == "POST":
        file_number = int(os.listdir("static/data/article_assets")[-1]) + 1

        path = os.path.join("static/data/article_assets", str(file_number))

        os.mkdir(path)
        with open(f"static/data/article_assets/{file_number}/article.html", "w", encoding="utf-8") as file:
            file.write(f"<title>{form.title.data}</title>")
        now= datetime.datetime.now()
        article_dict= {
        "title": form.title.data,
        "content": f"static/data/article_assets/{str(file_number)}/article.html",
        "creation_date": f"{now.day}/{now.month}/{now.year}",
        "hidden": True
        
        }
        file = request.files['cover']
        filename = secure_filename(file.filename)
        file.save(os.path.join(f"static/data/article_assets/{file_number}", f"cover.{filename.split('.')[-1]}"))
        
        write_json(article_dict, file_number)
        redirect("/create")
        return redirect("/dashboard")
    else:
        return render_template("create.html", form=form)



@app.route("/edit/<string:id>", methods=["GET", "POST"])
def edit_article(id):  
    form = EditForm(request.form)

    if request.method == "POST":
        with open(f"static/data/article_assets/{id}/article.html", "w", encoding="utf-8") as file:
            file.write(request.form.get("content"))
        return redirect("/")
    else:
        try:
            with open(f"static/data/article_assets/{id}/article.html","r", encoding="utf-8") as sj:
                form.content.data = sj.read() 
                return render_template("edit.html", form= form)
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    app.run(use_reloader=True, debug=True)
