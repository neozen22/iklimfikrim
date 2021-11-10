from flask import Flask, render_template, flash, redirect, session, logging, request, jsonify, url_for
from wtforms import Form, StringField , PasswordField, validators, FileField, SubmitField, HiddenField
import os
import json
import werkzeug
from werkzeug.utils import secure_filename, send_from_directory
import datetime
import logging
import werkzeug
from flask_sqlalchemy import SQLAlchemy
import jwt
from functools import wraps
from flask_ckeditor import CKEditor, CKEditorField, upload_fail, upload_success
from config import Config

# TODO: logging system
# TODO: Config, readme falan
# TODO: article olmadığında article yok de

class CreateForm(Form):
    login = HiddenField("")
    title = StringField("", validators=[validators.DataRequired(message="Burayı Boş Bırakmayınız")])
    cover = FileField(label="")

class EditForm(Form):
    change_title = StringField("Yeni Başlık")
    content = CKEditorField("İçerik")

class Dashboardform(Form):
    delete = SubmitField("Sil")
    hide = SubmitField("Sakla")

class MasterPassword(Form):
    email = StringField("Email", validators=[validators.DataRequired(message="Burayı boş bırakmayınız")])
    masterpass = PasswordField("Master Password", validators=[validators.DataRequired(message="Burayı boş bırakmayınız")])



basedir = os.path.abspath(os.path.dirname(__file__))


config = Config()
app = Flask(__name__)
ckeditor = CKEditor(app)
app.secret_key = config.secret_key

# app.secret_key = "sjmiderimbruhmuanlamadimkardesnediyeyimsende"
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
app.config['CKEDITOR_PKG_TYPE'] = 'full'
app.config['CKEDITOR_FILE_UPLOADER'] = "upload"

class Admins(db.Model):
    email = db.Column(db.String(), primary_key=True)



def fetch_articles():
    with open("static/data/articles.json", encoding="utf-8") as articles_file:
        return json.load(articles_file)



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
    return render_template("index.html", articles=articles)


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
    return render_template("dashboard.html", articles= articles, form=form)



@app.route("/login", methods=["GET", "POST"])
def tlogin():
    passwordform = MasterPassword(request.form)
    
    if request.method == "POST":
        if passwordform.validate():
            if passwordform.masterpass.data == config.master_password:
                token = jwt.encode({'email': passwordform.email.data,'admin': True ,'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=3  )}, app.config["SECRET_KEY"])
                session['token'] = token
                return redirect("/dashboard")
            else:
                flash("şifre yanlış")
                return redirect("/login")

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
    test = 1
    form = EditForm(request.form)

    if request.method == "POST":
        with open(f"static/data/article_assets/{id}/article.html", "w", encoding="utf-8") as file:
            file.write(request.form.get("content"))

        with open("static/data/articles.json", "r+", encoding="utf-8") as article_info:
            old_article_data = json.load(article_info)
            old_article_data[id]['title'] = form.change_title.data
            article_info.seek(0)
            json.dump(old_article_data, article_info, indent=4)
            article_info.truncate()
            
            

        return redirect("/dashboard")
    else:
        try:
            with open(f"static/data/article_assets/{id}/article.html","r", encoding="utf-8") as sj:
                form.content.data = sj.read()
                article_data = fetch_articles()
                article_title = article_data[id]['title']
                try:

                    return render_template("edit.html", form= form, article_title=article_title)
                except TypeError:
                    return render_template("404.html")
        except FileNotFoundError:
            pass

@app.route('/files/<filename>')
def uploaded_files(filename):
    path = 'static/img/img_assets'
    return send_from_directory(path, filename)

@app.route('/upload', methods=['POST'])
@ckeditor.uploader
def upload():
    f = request.files.get('upload')
    f.save(os.path.join('static/img/img_assets', f.filename))
    url = url_for('uploaded_files', filename=f.filename)
    return url



if __name__ == "__main__":

    app.run(use_reloader=True, debug=True)