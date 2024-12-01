import functions
import pytz
import random
import time
import sqlite3
from datetime import datetime 
from flask import Flask, session, redirect, url_for, request, render_template, jsonify
import yaml
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from mover import upkeep, is_kept

def day(local_timezone: str = "Europe/Dublin", target_timezone: str = "Australia/Sydney") -> int:
    local_tz = pytz.timezone(local_timezone)
    target_tz = pytz.timezone(target_timezone)
    local_time = datetime.now(local_tz)
    target_time = local_time.astimezone(target_tz)
    return target_time.day

# TODO MAKE LAMBDA FUNCTIONS
escape = lambda cstr: cstr.replace('/', '-')

def loggedin(session):
    if session.get('auth') and session.get('username') and session.get('name'):
        return True
    return False

def get_date_schema():
    # timeless method
    return {
        date: {
            "challenge": functions.challenges_today(date),
            "due": functions.due_today(date),
        }
        for date in range(-10, 40, 1)
    }
# loading the yaml config
with open('config.yaml', 'r') as yaml_file:
    config = yaml.safe_load(yaml_file)



app = Flask(__name__)
app.secret_key = config['secret_key'] + "" if (day() % 3 != 0) else str(day())
# wierd hack to clear the session every n days (6)
 
limiter = Limiter(get_remote_address,
                  app=app,
                  default_limits=["999 per hour"]
)


@app.route("/", methods=['GET', 'POST'])
def index():
    if session.get('auth') != True:
        return redirect(url_for('login'))
  
    # TODO, 2024 12, 10 is a debug
    # welcome messages 

    welcome_message = random.choice([
        '"Data science is a journey, not a destination." – DJ Patil',
        '"Don’t worry about failure; you only have to be right once." – Drew Houston',
        '"The best way to predict the future is to invent it." – Alan Kay',
        '"The best way to predict the future is to invent it." – Alan Kay',
        '"The best way to predict the future is to invent it." – Alan Kay',
        '"The best way to predict the future is to invent it." – Alan Kay',
        '"Success is the ability to go from one failure to another with no loss of enthusiasm." – Winston Churchill',
        '"We are surrounded by data, but it’s only valuable when you can understand it and make decisions based on it." – Cathy O\'Neil',
        '"We are surrounded by data, but it’s only valuable when you can understand it and make decisions based on it." – Cathy O\'Neil',
        '"We are surrounded by data, but it’s only valuable when you can understand it and make decisions based on it." – Cathy O\'Neil',
        '"The greatest minds are capable of the greatest vices as well as of the greatest virtues." – Albert Einstein',
        '"We can only see a short distance ahead, but we can see plenty there that needs to be done." – Alan Turing',
        '"We can only see a short distance ahead, but we can see plenty there that needs to be done." – Alan Turing',
        '"We can only see a short distance ahead, but we can see plenty there that needs to be done." – Alan Turing',
        '"We can only see a short distance ahead, but we can see plenty there that needs to be done." – Alan Turing',
            'Nah',
        'Anybody know where I can get a haircut exactly the same as William Shakespeare?',
        '"Complexity is the enemy of execution." – Tony Robbins',
        '"Complexity is the enemy of execution." – Tony Robbins',
        '"Complexity is the enemy of execution." – Tony Robbins',
        '"Complexity is the enemy of execution." – Tony Robbins',
        '"First, solve the problem. Then, write the code." – John Johnson',
        '"First, solve the problem. Then, write the code." – John Johnson',
        '"First, solve the problem. Then, write the code." – John Johnson',
        '"First, solve the problem. Then, write the code." – John Johnson',
        '"First, solve the problem. Then, write the code." – John Johnson',
        "They don't know me son",
        "Andrew vs Hydraulic Press",


    ])

    # error messages
    display_error_msg, error_msg = functions.get_error_messages()
    
    # custom processing in Error messaging
    error_msg = error_msg.replace('<NAME>', session['name'])
    error_msg = error_msg.replace('<USERNAME>', session['username'])

    names, link, status_open = functions.get_challenges(datetime.now(pytz.timezone('Europe/Dublin')).astimezone(pytz.timezone('Australia/Sydney')).date())
    # names, link, status_open = functions.get_challenges(datetime.date(2024, 12, 28)) # Debugging Date
    return render_template('main.html',
                           days=functions.days_until_end_of_december(),
                           name=session['name'],
                           points=session['points'],
                           names=names,
                           link=link,
                           status_open=status_open,
                           loop_length=len(status_open),
                           dateschema=get_date_schema(),
                           today=day(),
                           welcome_message=welcome_message,
                           display_error_msg=display_error_msg,
                           error_msg=error_msg
                           )

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print("user:", username, password)
        if username=='default':
            return render_template('login.html')
        usercred = functions.authenticate_user(username, password)
        session['auth'] = usercred['auth']
        session['username'] = usercred['username']
        session['name'] = usercred['name']
        session['points'] = usercred['points']
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
        name  = request.form.get('name')

        usercred = functions.create_user(username, name, password, 'depreciated')

        if usercred['created']:
            return redirect(url_for('login'))

        # TODO add error messaging
        # Adding eror messaging for different types of errors ad addign ap assword

    return render_template('signup.html')

@app.route("/advent")
def advent_dateless():
    today = day()
    return redirect(url_for('advent', date=today))

@app.route("/advent/<date>", methods=['GET', 'POST'])
def advent(date):

    if not loggedin(session):
        return redirect(url_for('login'))

    # post
    if request.method == 'POST':
        user = request.form.get('response')
        if user:
            print(user)
            functions.advent_response(session['username'], user, date)

        return redirect(url_for('advent_dateless'))  # TODO Fix

    # date number
    try:
        date = int(date)
        if not (date > 0 and date < 32):
            return redirect(url_for('index'))
    except:
            return redirect(url_for('index'))

    if date > day():
        return redirect(url_for('early'))
    
    current_challenge, current_title, current_due = functions.last_challenge(date)
    title_today, html_today = functions.get_challenges_due_today(date)


    return render_template('advent.html',
                           today = date,
                           name = session['name'],
                           points = session['points'],
                           #WEEK SUMMARY
                            current_challenge=current_challenge,
                           current_title=current_title,
                           title_today=title_today,
                           html_today=html_today,
                           current_due=current_due,
                             #QUESTION

                           question = functions.get_question(date),
                           table = functions.get_table(date),
                           image = functions.get_image(date),
                           response = functions.get_response(session['username'], date))


@app.route("/logout")
def logout():
    session.pop('username', None)
    session.pop('auth', None)
    return redirect(url_for("login"))


@app.route("/messaging", methods=['GET', 'POST'])
def messaging():
    if not (session['auth'] and session.get('username') == 'wingfooted'):
        return redirect(url_for('index'))
    
    if request.method == 'GET':
        return render_template('messaging.html')

    if request.method == 'POST':
        display = request.form.get('display_true_val')
        msg = request.form.get('error_display_msg')
        if display and msg:
            print(display, msg)
            output = functions.create_error_msg(display, msg)
            return f'{output} <a href="/">Home</a>'
        else:
            return render_template('messaging.html')


@app.route("/challenge/<dynamic>")
@limiter.limit("30 per minute")
def challenge(dynamic):
    # user logged in
    if not loggedin(session):
        return redirect(url_for('login'))


    def check_valid_challenge(challenge):
        if challenge == 'cold':
            return True
        elif challenge == 'mining':
            return True
        elif challenge == 'stars':
            return True
        elif challenge == 'news':
            return True
        else:
            return False

    if not functions.challenge_released(dynamic, day()):
        return redirect(url_for('early'))

    if not is_kept(dynamic):
        upkeep(dynamic)
        return redirect(url_for('challenge', dynamic=dynamic))

    if check_valid_challenge(dynamic):
        return render_template(f'{dynamic}.html', name=session['name'], points=session['points'])

    else:
        return redirect(url_for('index'))
        return dynamic

@app.route("/give-points/<dir>/<quantity>/<target>/<username>/<password>")
@limiter.limit("1 per second")
def point_update(dir, quantity, target, username, password):
    #1 indicates positive
    #0 indicates negative
    if username == "wingfooted":
        if functions.authenticate_user(username, password)['auth']:

            # checking the input
            if not (dir == "0" or dir == "1"):
                return "dir value not valid", 400

            if not (quantity.isnumeric()):
                return "quantity not a number", 400

            dir = int(dir) * 2 - 1

            functions.update_points(target, int(quantity) * dir)
            return f"given {target} {dir * int(quantity)} pts"


        else: 
            return "incorrect username + password", 400
    else:
        return "forbidden not admin", 400


@app.route("/guide/<dynamic>")
@limiter.limit("30 per minute")
def guide(dynamic):
    def check_valid_guide(guide):
        if guide in ['thanks', 'submissions', 'reports', 'points', 'welcome', 'sql', 'privacy', 'advent', 'return', 'people']:
            return True
        return False

    if not is_kept(dynamic):
        upkeep(dynamic)
        return redirect(url_for('guide', dynamic=dynamic))

    if check_valid_guide(dynamic):
        if dynamic == "advent":
            return redirect(url_for('advent', date=day()))
        return render_template(f'{dynamic}.html', name=session['name'], points=session['points'])

    else:
        return dynamic


@app.route("/workbench")
def workbench():
    if session.get('auth') != True:
        return redirect(url_for('login'))

    # token, (somewhat naievely) contains randomness for better or worse
    # improvement
    #
    # session['auth'] => username + password => mint token

    token = functions.create_token(session['username'], password="placeholder")

    return render_template('workspace.html', token=token, name=session['name'], points=session['points'])

@app.route("/sql", methods=['POST'])
@limiter.limit("20 per minute")
def sql():
    if request.method == 'POST':
        data = request.get_json()
        sql = data.get('sql')
        token = data.get('token')
        print("PRINTING AT THE NAIVE RECIEVE LEVEL", sql, token, sep="\n")

        # Error 1: token sql not in tact
        # Error 2: token invalid / expired
        # Error 3: Broken SQL
        # Sucsess

        if not functions.validate_token(token):
            # TODO : How to differentiate, broken token, fake account, etc
            return jsonify({'error': "Invalid token. Make sure that your username and password are correct, otherwise a token will not be minted. \n Note: tokens refresh every 10 minutes. \n to mint a new token use the context manager with datacamber \n see guides for more"}), 401
        if not sql:
            return jsonify(
                {'error': 'could not find your sql query'}), 418

        # safe to assumpe that token valid, sql legit
        try:
            with sqlite3.connect('antarctica.db') as conn:
                start = time.time()
                cursor = conn.cursor()
                cursor.execute(sql)
                header = [description[0] for description in cursor.description]
                output = cursor.fetchall()
                length_output = len(output)
                end = time.time()
                user = functions.get_user_from_token(token)
                functions.create_query(sql, str(datetime.now(pytz.timezone('Europe/Dublin')).astimezone(pytz.timezone('Australia/Sydney')).date()),
                                       end-start, length_output, token, user)
                print(sql, header, output, end-start, sep="\n")
                return jsonify({'content': output, 'header': header, 'runtime': f"{end - start:.4f}", 'rows': length_output}), 200
                # add functionality, appending to dataframes

        except sqlite3.OperationalError as OppErr:
            return jsonify({'error': str(OppErr), 'hint': 'Likely an error in your sql code'}), 418

        except sqlite3.Error as generic_error:
            return jsonify({"error": str(generic_error)}), 418


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


@app.route('/leaderboard')
def leaderboard():
    if loggedin(session):
        print(functions.get_leaderboard())
        return render_template('people.html', 
                               content=functions.get_leaderboard())
    else:
        return redirect(url_for('login'))


@app.route('/come-back-soon')
def early():
    if not loggedin(session):
        return redirect(url_for('login'))
    return render_template('return.html',
                           name=session['name'],
                           today=day(),
                           points=session['points'],
                           )

if __name__ == '__main__':
    app.run(debug=True, port=8997, host='0.0.0.0')
