from flask import Flask, render_template, flash, redirect, session, logging, request, jsonify, url_for
import sqlalchemy
from wtforms import Form, StringField , PasswordField, validators, FileField, SubmitField, HiddenField
import os
import json
import werkzeug
from werkzeug.utils import secure_filename, send_from_directory
import logging
import werkzeug
from flask_sqlalchemy import SQLAlchemy
import jwt
from functools import wraps
from flask_ckeditor import CKEditor, CKEditorField, upload_fail, upload_success
from config import Config
import datetime

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
    email = StringField("Email", validators=[validators.data_required(message="burayı boş bırakmayınız")])
    masterpass = PasswordField("Password", validators=[validators.DataRequired(message="Burayı boş bırakmayınız")])



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

class Article(db.Model):
    id = db.Column(db.String(), primary_key=True)
    title = db.Column(db.String(), nullable=False)
    creation_date = db.Column(db.DateTime(), nullable=False)
    hidden = db.Column(db.Boolean(), nullable=False)



def fetch_articles_from_db():
    articles = Article.query.all()
    return articles


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
    articles = fetch_articles_from_db()
    return render_template("index.html", articles=articles)


@app.route("/dashboard", methods=["GET", "POST"] )
@admin_required
def dashboard():

    data = Article.query.all()
    if request.method == "POST":
        try:
            if request.form["delete"]:
                deleted_data= request.form["delete"]
                delete_path = f"{basedir}/static/data/article_assets/{deleted_data}"
                # remove object from db
                obj = Article.query.filter_by(id=deleted_data).first()
                db.session.delete(obj)
                db.session.commit()
                files_in_dir = os.listdir(delete_path)
                for file in files_in_dir:                  # loop to delete each file in folder
                    os.remove(f'{delete_path}/{file}')
                os.rmdir(delete_path)
        except:
            
            try:
                if request.form["hide"]:
                    
                    if Article.query.filter_by(id=request.form["hide"]).first().hidden:
                        db.session.query(Article).filter_by(id=request.form["hide"]).update(dict(hidden=False))
                        db.session.commit()
                    else:
                        print('bruhhh')
                        db.session.query(Article).filter_by(id=request.form["hide"]).update(dict(hidden=True))
                        db.session.commit()
            except:
                raise
        db.session.commit()


            
    
    form = Dashboardform(request.form)
    articles = Article.query.all()
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

    article_title = Article.query.filter_by(id=id).first().title

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
        session_data = Article(id=file_number, title=form.title.data, creation_date=now, hidden=True)
        db.session.add(session_data)
        db.session.commit()

        file = request.files['cover']
        filename = secure_filename(file.filename)
        file.save(os.path.join(f"static/data/article_assets/{file_number}", f"cover.{filename.split('.')[-1]}"))
        
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
            db.session.query(Article).filter_by(id=id).update(dict(title=form.change_title.data))
            db.session.commit()

            

        return redirect("/dashboard")
    else:
        try:
            with open(f"static/data/article_assets/{id}/article.html","r", encoding="utf-8") as sj:
                form.content.data = sj.read()
                article_title = Article.query.filter_by(id=id).first().title
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
    db.create_all()
    app.run(use_reloader=True, debug=True)