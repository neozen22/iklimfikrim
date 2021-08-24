from flask import Flask, render_template


app = Flask(__name__)


@app.route("/")
def hello_world():
    return render_template("index.html", articles=[i for i in range(10)])


if __name__ == "__main__":
    app.run(use_reloader=True, debug=True)
