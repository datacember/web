from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return "welcome to datacember"

@app.route("/")
def index():
    return "welcome to datacember"




if __name__ == '__main__':
    app.run(debug=True, port=8999)
