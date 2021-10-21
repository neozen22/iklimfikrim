from enum import unique
from inspect import Parameter
import re
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, jsonify
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, FileField, SubmitField, HiddenField
from passlib.hash import sha256_crypt
import os
import json
import werkzeug
from werkzeug.utils import secure_filename
import datetime
import logging
import werkzeug
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
import jwt
import uuid
import hashlib
from functools import wraps
from flask_ckeditor import CKEditor


class RegisterForm(Form):
    register = HiddenField("")
    name = StringField("", validators=[validators.DataRequired(message="Burayı boş bırakmayınız")])
    username = StringField("")
    password = PasswordField("", validators=[validators.Length(min=1, message="Şifrede boşluk kullanmayınız"), validators.DataRequired(message="Burayı boş bırakmayınız")])

class LoginForm(Form):
    username = StringField("")
    password = PasswordField("")


class CreateForm(Form):
    login = HiddenField("")
    title = StringField("", validators=[validators.DataRequired(message="Burayı Boş Bırakmayınız")])
    cover = FileField(label="")

class EditForm(Form):
    change_title = StringField("Yeni Başlık")
    content = TextAreaField("İçerik")

class Dashboardform(Form):
    delete = SubmitField("Sil")
    hide = SubmitField("Sakla")

class MasterPassword(Form):
    email = StringField("email", validators=[validators.DataRequired(message="Burayı boş bırakmayınız")])
    masterpass = PasswordField("Master Password", validators=[validators.DataRequired(message="Burayı boş bırakmayınız")])


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

def is_loggedin():
    try:
        token = session["token"]
    except KeyError:
        return False
    try:
        data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        return True
    except:
        return False

def write_json(new_data, file_number,filename='static/data/articles.json'):
    with open(filename,'r+', encoding='utf-8') as file:
        file_data = json.load(file)

        file_data[str(file_number)]= new_data
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent = 4)
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            token = session["token"]
        except KeyError:
            # return jsonify({'message' : 'Token is missing!'}), 403
            return redirect("/login")


        try:
            data =(jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"]))

        except jwt.exceptions.ExpiredSignatureError:
            session.pop("token")
            return redirect('/login')

        if data["admin"]:
            return f(*args, **kwargs)
        else:
            return jsonify({"message": "Buraya giriş yapmak için admin olmanız gerekiyor"})



    return decorated

    

@app.route("/")
def index():
    articles = fetch_articles()
    try:
        data = (jwt.decode(session["token"], app.config["SECRET_KEY"], algorithms=["HS256"]))
    except KeyError:
        return render_template("index.html", articles=articles, logged_in=False)
    return render_template("index.html", articles=articles, logged_in=is_loggedin(), name=data["name"])



@app.route("/dashboard", methods=["GET", "POST"] )
@admin_required
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
    userdata = jwt.decode(session["token"], app.config["SECRET_KEY"], algorithms=["HS256"])
    return render_template("dashboard.html", articles= articles, form=form, logged_in=is_loggedin(), name=userdata["name"])



@app.route("/login", methods=["GET", "POST"])
def login():
    registerform = RegisterForm(request.form)
    loginform = LoginForm(request.form)
    if request.method == "POST":
        try:
            if request.form["form"] == "register":
                if registerform.validate():
                    user = User(_id=uuid.uuid4().hex, username=registerform.username.data, password=hashlib.sha256((registerform.password.data).encode("utf-8")).hexdigest(), name=registerform.name.data, admin=False)
                    # print(hashlib.sha256(registerform.password.data).hexdigest())
                    db.session.add(user)    
                    db.session.commit()

            currentuser = User.query.filter_by(username=request.form["username"]).first()
            if currentuser is None:
                pass
            else:
                if (hashlib.sha256((registerform.password.data).encode("utf-8")).hexdigest() == currentuser.password):
                    token = jwt.encode({'name': currentuser.name,'admin': currentuser.admin ,'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config["SECRET_KEY"])
                    session['token'] = token
            return redirect("/")

        except werkzeug.exceptions.BadRequestKeyError:
            raise


    return render_template("login.html", registerform=registerform, loginform=loginform)

@app.route("/tlogin", methods=["GET", "POST"])
def tlogin():
    passwordform = MasterPassword(request.form)
    
    if request.method == "POST":
        if passwordform.validate():
            token = jwt.encode({'name': currentuser.name,'admin': currentuser.admin ,'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config["SECRET_KEY"])
            session['token'] = token



    return render_template("master_password.html", passform= passwordform)


@app.route("/article/<string:id>")
def article(id):
    with open("static/data/articles.json", encoding="utf-8") as articles_file:
        article_data = json.load(articles_file)
        article_title = article_data[id]["title"]
    try:
        with open(f"static/data/article_assets/{id}/article.html","r", encoding="utf-8") as sj:
            article_content = sj.read()

            return render_template("articleholder.html",article_content=article_content, article_title=article_title)
    except FileNotFoundError:
        return render_template("404.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")



@app.route("/create", methods=["GET", "POST"])
@admin_required
def create_article():
    form = CreateForm(request.form)
    if request.method == "POST":
        try:
            file_number = int(os.listdir("static/data/article_assets")[-1]) + 1
        except IndexError:
            file_number = 1
            
        

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
@admin_required
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

@app.route("/uploadimg", methods=["GET", "POST"])
def process_img():
    print("sj")



if __name__ == "__main__":

    app.run(use_reloader=True, debug=True)

