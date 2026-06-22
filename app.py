from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    return "Recomendador de Presentes em construcao."


if __name__ == "__main__":
    app.run(debug=True)
