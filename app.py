import functions
import time
import sqlite3
import datetime
from flask import Flask, session, redirect, url_for, request, render_template, jsonify
import yaml
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from mover import upkeep, is_kept


# loading the yaml config
with open('config.yaml', 'r') as yaml_file:
    config = yaml.safe_load(yaml_file)

app = Flask(__name__)
app.secret_key = config['secret_key']

limiter = Limiter(get_remote_address, app=app, default_limits=["999 per hour"])

@app.route("/", methods=['GET', 'POST'])
def index():
    if session.get('auth') != True:
        return redirect(url_for('login'))
  
    # TODO, 2024 12, 10 is a debug
    names, link, status_open = functions.get_challenges(datetime.date(2024, 12, 28))
    return render_template('main.html',
                           days=functions.days_until_end_of_december(),
                           name=session['name'],
                           names=names,
                           link=link,
                           status_open=status_open,
                           loop_length=len(status_open)
                           )

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print("user:", username, password)
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


@app.route("/<dynamic>")
@limiter.limit("30 per minute")
def challenge(dynamic):
    # TODO check_valid_challenge()
    check_valid_challenge = lambda x: True
    # TODO check_upkeep 

    if not is_kept(dynamic):
        upkeep(dynamic)
        return redirect(url_for('challenge', dynamic=dynamic))

    if check_valid_challenge(dynamic):
        return render_template(f'{dynamic}.html')

    else:
        return dynamic

@app.route("/workspace")
def workspace():
    if session.get('auth') != True:
        return redirect(url_for('login'))

    # token, (somewhat naievely) contains randomness for better or worse
    # improvement
    #
    # session['auth'] => username + password => mint token
    token = functions.create_token(session['username'], password="placeholder")

    return render_template('workspace.html', token=token)

@app.route("/sql", methods=['GET', 'POST'])
@limiter.limit("20 per minute")
def sql():
    if request.method == 'POST':
        data = request.get_json()
        sql = data.get('sql')
        token = data.get('token')

        # Error 1: token sql not in tact
        # Error 2: token invalid / expired
        # Error 3: Broken SQL
        # Sucsess

        if not functions.validate_token(token):
            # TODO : How to differentiate, broken token, fake account, etc
            return jsonify({'error': "Invalid token. Make sure that your username and password are correct, otherwise a token will not be minted. \n Note: tokens refresh every 10 minutes. \n to mint a new token use the context manager with datacamber \n see guides for more"}), 401
        if not sql:
            return jsonify(
                {'error': 'could not find your sql query'}), 400

        # safe to assumpe that token valid, sql legit
        try:
            with sqlite3.connect('antarctica.db') as conn:
                start = time.time()
                cursor = conn.cursor()
                cursor.execute(sql)
                output = cursor.fetchall()
                length_output = len(output)
                end = time.time()
                user = functions.get_user_from_token(token)
                functions.create_query(sql, str(datetime.datetime.today()),
                                       end-start, length_output, token, user)
                return jsonify({'content': output}), 200
                # add functionality, appending to dataframes

        except sqlite3.OperationalError as OppErr:
            return jsonify({'error': str(OppErr), 'hint': 'Likely an error in your sql code'}), 400

        except sqlite3.Error as generic_error:
            return jsonify({"error": str(generic_error)}), 400

        return jsonify({"content": "moment", "token": functions.validate_token(token)}), 200


@app.route('/auth', methods=['POST', 'GET'])
@limiter.limit("10 per minute")
def auth():
    if request.method == 'POST':
        data = request.get_json()
        db_response = functions.authenticate_user(
                username=data.get('username'),
                password=data.get('password')
        )

        if db_response['auth']:
            username = data.get('username')
            password = data.get('password')
            # make the user an auth token
            return jsonify({'auth': True,
                            'token': functions.create_token(username, password)
                            }), 200
        else:
            return jsonify({'auth': False}), 200

    if request.method == 'GET':
        # for stray requests
        return redirect(url_for('index'))



if __name__ == '__main__':
    # TODO find a way to render
    # naive start up render does not work
    # for instance, cold.qmd requires app
    # but adding startup render makes app require cold.qmd
    # circular dependancy
    app.run(debug=True, port=8999, host='0.0.0.0')
