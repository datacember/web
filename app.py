import functions
from flask import Flask, session, redirect, url_for, request, render_template
  # custom functions for database conenctivity
import yaml

# loading the yaml config
with open('config.yaml', 'r') as yaml_file:
    config = yaml.safe_load(yaml_file)

app = Flask(__name__)
app.secret_key = config['secret_key']


@app.route("/", methods=['GET', 'POST'])
def index():
    if session.get('auth') != True:
        return redirect(url_for('login'))
    
    return render_template('main.html',
                           days=functions.days_until_end_of_december(),
                           name=session['name']
                           )

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        usercred = functions.authenticate_user(username, password)
        session['auth'] = usercred['auth']
        session['username'] = usercred['username']
        session['name'] = usercred['name']
        if not session['username']:
            return render_template('login.html', msg="wrong username")
        elif not session['auth']:
            return render_template('login.html', msg="wrong password")
        else:
            return redirect(url_for('index'))

    return render_template('login.html')


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        password = request.form.get('password')
        username = request.form.get('username')
        github = request.form.get('github')
        name  = request.form.get('name')

        usercred = functions.create_user(username, name, password, github)

        if usercred['created']:
            return redirect(url_for('login'))

        # TODO add error messaging
        # Adding eror messaging for different types of errors ad addign ap assword

    return render_template('signup.html')


@app.route("/logout")
def logout():
    session.pop('username', None)
    session.pop('auth', None)
    return redirect(url_for("login"))


if __name__ == '__main__':
    app.run(debug=True, port=8999)
