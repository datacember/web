import sqlite3
import hashlib
from typing import Dict
import datetime
import numpy as np


def create_user(username: str,
                name: str,
                password: str,
                github: str) -> Dict:
    """
    created: bool, weather user was created sucsessfully
    valid_username: bool, weather username is valid
    valid_password: unused, TODO, bool, weahter pasxsword is legit
    """

    output = dict()
    with sqlite3.connect('content.db') as conn:
        cursor = conn.cursor()

        if not valid_username(username, cursor):
            output["created"] = False
            output["valid_username"] = False
            output["valid_password"] = True
            return output

        cursor.execute("""
            INSERT INTO users (username, name, password, github, signup)
            VALUES (?, ?, ?, ?, ?)""",
            (
                username, name,
                hashlib.sha256(password.encode()).hexdigest(),
                'https://github.com/wingfooted',
                str(datetime.date.today())
            )
        )
        cursor.execute("SELECT * FROM users")
        user = cursor.fetchall()
        print(user)

    output["created"] = True
    output["valid_username"] = True
    output["valid_password"] = True
    return output

    # true if created user sucsessfully,
    # false if not created sucsessfully


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
    with sqlite3.connect('content.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT username, name, password
            FROM users
            WHERE username = ?
        """, (username,)
        )
        user = cursor.fetchone()
    output = {}
    if user:
        output['username'] = user[0]
        output['name'] = user[1]
        password = user[2]
    else:
        return {"auth": False, "username": False, "name": False}

    output['auth'] = True if password == hashed_password else False
    output['name'] = output['name'] if output['auth'] else False

    return output  # houtput is a dict


def valid_username(username: str, cursor: sqlite3.Cursor) -> bool:
    cursor.execute("SELECT * FROM users WHERE username= ?", (username,))
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

def get_challenges(current: datetime.date = datetime.date.today()):
    """
    Gets all available challenges open to user at this day
    names : title names
    html : relevant html
    open_status : [bool]
    """

    with sqlite3.connect('content.db') as conn:
        cursor = conn.cursor()
        output = cursor.execute("SELECT * FROM challenges").fetchall()
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

if __name__ == '__main__':
    print(*get_challenges(datetime.date(2024, 12, 6)))
