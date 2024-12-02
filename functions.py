import sqlite3
import pymysql
import subprocess
import os
import random
import hashlib
from typing import Dict
import datetime
import numpy as np

db = {
    'host': os.getenv('Host'),  # Use correct environment variable names
    'user': os.getenv('Username'),
    'password': os.getenv('Password'),
    'database': 'z3c2gl7ijtft4qes',
    'port': 3306
}

def create_user(username: str,
                name: str,
                password: str) -> Dict:
    """
    created: bool, weather user was created sucsessfully
    valid_username: bool, weather username is valid
    valid_password: unused, TODO, bool, weahter pasxsword is legit
    """

    output = dict()
    with pymysql.connect(**db) as conn:
        cursor = conn.cursor()

        if not valid_username(username, cursor):
            output["created"] = False
            output["valid_username"] = False
            output["valid_password"] = True
            return output

        cursor.execute("""
            INSERT INTO users (username, name, password, github, signup)
            VALUES (%s, %s, %s, %s, %s)""",
            (
                str(username), str(name),
                hashlib.sha256(password.encode()).hexdigest(),
                'na',
                str(datetime.date.today())
            )
        )
        conn.commit()

    output["created"] = True
    output["valid_username"] = True
    output["valid_password"] = True
    return output

    # true if created user sucsessfully,
    # false if not created sucsessfully

def update_points(user, points: int):
    # can assume that user is a user
    with pymysql.connect(**db) as conn:
        cursor = conn.cursor()
        cursor.execute(
                f"""
                UPDATE users SET points = points + %s WHERE username = %s
                """, (points, user)
        )



def authenticate_user(username: str,
                      password: str) -> Dict:
    """
    returns a dictionary. keys are 
    auth: bool: weatjer user was authetnticated
    username: False is not in db, else username
    name: false if not authenticated else gives users name
    """

    assert isinstance(username, str), "username must be a string"
    assert isinstance(username, str), "password must be a string"

    # Using a SHA-256 Hash.
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    with pymysql.connect(**db) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT username, name, password, points
            FROM users
            WHERE username = %s
        """, (username,)
        )
        user = cursor.fetchone()
    output = {}
    if user:
        output['username'] = user[0]
        output['name'] = user[1]
        output['points'] = user[3]
        password = user[2]
    else:
        return {"auth": False, "username": False, "name": False, "points": 0}

    output['auth'] = True if password == hashed_password else False
    output['name'] = output['name'] if output['auth'] else False

    return output  # houtput is a dict


def valid_username(username: str, cursor) -> bool:
    cursor.execute("SELECT * FROM users WHERE username= %s", (username,))
    output = cursor.fetchone()
    return False if output else True


def days_until_end_of_december():
    today = datetime.datetime.today()
    dec_start = datetime.datetime(today.year, 12, 1)
    dec_end = datetime.datetime(today.year, 12, 31)

    if today < dec_start:
        days_left = (dec_start - today).days
        return days_left
    elif today > dec_end:
        days_left = (today - dec_end).days
        return days_left
    else:
        days_left = (dec_end - today).days
        return days_left

def get_challenges(current = datetime.date.today()):
    """
    Gets all available challenges open to user at this day
    names : title names
    html : relevant html
    open_status : [bool]
    """

    with pymysql.connect(**db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM challenges")
        output = cursor.fetchall()
        output = [[row[i] for row in output] for i in range(len(output[0]))]

        _, names, html, open_status = output[0], output[1], output[2], output[3]
        open_status = [
            datetime.date(
                *[int(symbol) for symbol in day.split('-')]
                )
            for day in open_status
        ]
        open_status = [True if date.day <= current.day else False
                       for date in open_status]

        return names, html, open_status


def create_token(username: str, password: str) -> str:
    n1 = random.random()
    n2 = random.random()
    n3 = random.random()

    format_string = f"{n1}{username}{password}{n2}{datetime.date.today()}{n3}"
    token = hashlib.sha256(format_string.encode()).hexdigest()

    now = datetime.datetime.now()
    year = now.year
    month = now.month
    day = now.day
    hour = now.hour
    minute = now.minute

    with pymysql.connect(**db) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO tokens (token, user, year, month, day, hour, minute)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (token, username, year, month, day, hour, minute))
        conn.commit()

    return token


def validate_token(token: str) -> bool:
    with pymysql.connect(**db) as conn:
        cursor = conn.cursor()
        # check if token is in the database
        cursor.execute("SELECT * FROM tokens WHERE `token` = %s", (token,))
        tokens = cursor.fetchall()
        if len(tokens) == 0:
            return False
            # token does not exist

        # verify date of the token
        now = datetime.datetime.now()
        year = now.year
        month = now.month
        day = now.day
        hour = now.hour
        minute = now.minute

        def unix_time(year: int, month: int, day: int, hour: int, minute: int):
            total = 0
            if 1970 >= year:
                return 0
            total = total + (year - 1970) * 3153600
            total = total + month * 2592000
            total = total + day * 86400
            total = total + hour * 60 * 60
            total = total + minute * 60

            return total

        # although it does not matter that this unix time func is absoloutely correct
        # all that matters is that it is consistetly innacurate
        token = tokens.pop()
        db_year, db_month, db_day, db_hour, db_minute = token[3:]
        current_unix_time = unix_time(year, month, day, hour, minute)
        token_mint_unix_time = unix_time(*token[3:])
        expiry_time = 10 # in minutes
        if token_mint_unix_time + expiry_time < current_unix_time:
            return False

        return True


def create_query(
    user_query: str,
    time: str,
    runtime: float,
    row_length: int,
    token: str,
    user: str
):
    sql = f"""
    INSERT INTO queries (token, user, user_query, time, runtime, row_length)
    VALUES ('{token}', '{user}', '{user_query}', '{str(time)}', '{runtime}', '{row_length}')
    """
    with pymysql.connect(**db) as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()

def get_user_from_token(token: str):
    with pymysql.connect(**db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user FROM tokens WHERE token = %s", (token,))
        output = cursor.fetchone()
    return output[0]

def get_users():
    # returns a list of all users
    with pymysql.connect(**db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, name FROM users;")
        output = cursor.fetchall()
    return output


def startup_render():
    for filename in os.listdir('quarto'):
        if filename.endswith('.qmd'):
            qmd = f"quarto/{filename}"
            try:
                subprocess.run(['quarto', 'render', qmd], check=True)
                print(f"Rendered {filename} successfully.")
            except subprocess.CalledProcessError:
                print(f"Failed to render {filename}.")

def get_error_messages():
    with pymysql.connect(**db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT display, error FROM messages ORDER BY id DESC LIMIT 1")
        output = cursor.fetchone()

        if output:
            return True if output[0] == 1 else False, output[1]
        return False, "No display Message"

def create_error_msg(display: int, msg):
    insert = 0
    if str(display) == '1':
        insert = 1

    with pymysql.connect(**db) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO messages (display, error) VALUES (%s, %s)", (insert, msg))
        conn.commit()
    return True


def challenges_today(date: int) -> bool:
    if date in [1, 6, 12, 17, 26]:
        return True
    return False

def due_today(date: int) -> bool:
    if date in [5, 12, 16, 23, 31]:
        return True
    return False

def next_due_date(date) -> int:
    with pymysql.connect(**db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT html, name, deadline FROM challenges")
        challenges = cursor.fetchall() # list of all challenges

    # date <- challenge
    challenge_table = {}
    for (challenge, title, deadline) in challenges:
        table_date = int(deadline.split('-')[2])
        challenge_table[table_date-date] = (challenge, deadline, title)
    
    items = [d for d in
        challenge_table.keys() if d >=0]
    if not items:
        return None, None, None, None
    min_dist = min(
        items
    )
    return challenge_table[min_dist][0], challenge_table[min_dist][1], int(challenge_table[min_dist][1].split("-")[2]), challenge_table[min_dist][2]
                

def next_challenge(date) -> int:
    with pymysql.connect(**db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, deadline FROM challenges")
        challenges = cursor.fetchall() # list of all challenges

        # date <- challenge
        challenge_table = {}
        for (challenge, deadline) in challenges:
            table_date = int(deadline.split('-')[2])
            challenge_table[table_date-date] = (challenge, deadline)
        
        items = [d for d in
            challenge_table.keys() if d >0]
        if not items:
            return None, None
        min_dist = min(
            items
        )
        return challenge_table[min_dist][0], challenge_table[min_dist][1]

        
                
    return False

# TODO maybe realias this to current challenge
def last_challenge(date) -> str:
    with pymysql.connect(**db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT html, deadline, name FROM challenges")
        challenges = cursor.fetchall() # list of all challenges

        # date <- challenge
        challenge_table = {}
        for (challenge, deadline, name) in challenges:
            table_date = int(deadline.split('-')[2])
            challenge_table[date-table_date] = (challenge, deadline, name)
       

        items = [d for d in
            challenge_table.keys() if d <0]

        if not items:
            return False, False, False

        min_dist = max(
            items
        )
        return challenge_table[min_dist][0], challenge_table[min_dist][2], challenge_table[min_dist][1]


        
                
    return False

def challenge_released(challenge: str, date: int) -> bool:
    """
        Date is a day integer valued number 
    """
    print(challenge)
    print(date)
    with pymysql.connect(**db) as conn:
        cursor = conn.cursor()
        while date>0:
            cursor.execute('SELECT * FROM challenges WHERE html = %s AND `release` = %s', 
                           (challenge, '2024-12-'+str(date)))
            output = cursor.fetchone()
            if output != None:
                return True
            date = date -1

    return False


def get_question(date: int) -> str:
    """Return a sample question based on the integer date."""

    with pymysql.connect(**db) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM adventcontent WHERE id = %s', (date,))
        output = cursor.fetchone()

    if output:
        return output
        
    return "", "How can you know if a data-science model is making good predictions?", "", ""

def get_table(date: int):
    """Return a matrix format, array of arrays, or False if not available."""
    return False  # Replace with actual logic if needed

def get_image(date: int):
    """Return an image or False if not available."""
    return False  # Replace with actual logic if needed

def get_leaderboard() -> str:
    with pymysql.connect(**db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, points FROM users ORDER BY points LIMIT 5")
        output = cursor.fetchall()
    return output

def get_response(username, date: int) -> str:
    with pymysql.connect(**db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT response FROM adventresponses WHERE username=%s AND date=%s", (username, str(date)))
        output = cursor.fetchone()
    return output[0] if output else False

def advent_response(username, response, date):
    with pymysql.connect(**db) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO adventresponses (username, response, date)
            VALUES (%s, %s, %s)""",
                       (
                       username,
                       response,
                       date)
                       )
        conn.commit()


def get_challenges_due_today(date):
    with pymysql.connect(**db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, html FROM challenges WHERE deadline = %s", (f'2024-12-{date}',))
        output = cursor.fetchone()
    if not output:
        return False, False 
    
    return output[0], output[1]

if __name__ == '__main__':
    get_question(2)
