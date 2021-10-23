from flask import Flask
from flask_restful import Resource, Api
import json



app = Flask(__name__)
api = Api(app)


class Article(Resource):
    def __init__(self) -> None:
        pass

    def get(self):
        with open("static/data/articles.json", encoding="utf-8") as articles_file:
            return json.load(articles_file)
        
api.add_resource(Article, "/")

if __name__ == "__main__":
    app.run(debug=True)