from flask import Flask, json, request, jsonify, Response
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import create_session
from sqlalchemy.exc import OperationalError
import os

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///static/data/database.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class ArticleData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content_path = db.Column(db.String(1000), nullable=False)
    creation_date = db.Column(db.String(100), nullable=False)
    hidden = db.Column(db.Boolean, nullable=False)

def create_article(title, content_path, creation_date, hidden):
    article = ArticleData(title=title, content_path=content_path, creation_date=creation_date, hidden=hidden)
    db.session.add(article)
    db.session.commit()


class Article(Resource):
    # def get(self):
    #     try:
    #         with open("static/data/articles.json", "r", encoding="utf-8") as articles_file:
    #             return json.load(articles_file)
    #     except FileNotFoundError:
    #         with open("static/data/articles.json", "w+", encoding="utf-8") as articles_file:
    #             articles_file.write("")
    #             return jsonify(json.load(articles_file))
    def get(self):
        return ArticleData.query.filter_by(hidden=False).all()
    def post(self):
        data = request.data
        print(data)
        try:
            create_article(data["title"], data["content_path"], data["creation_date"], data["hidden"])
            return Response(json.dumps({"status": "success"}), status=200, mimetype='application/json')
        except TypeError:
            return Response(json.dumps({"error": "no Data given"}), status=400, mimetype='application/json')



api.add_resource(Article, "/")
if __name__ == '__main__':
    if not os.path.isfile("static/data/database.db"):
        print('No database found. Initializing database')
        db.create_all()

    app.run(debug=True, port=4000)