import os
import hashlib
import sqlite3
import sys
import datetime

db_file = 'content.db'

# adding flags system

if '-d' in sys.argv:
    os.remove('content.db')

if not os.path.exists('content.db'):
    with sqlite3.connect('content.db') as conn:
        cursor = conn.cursor()

        # users table
        cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            password TEXT NOT NULL,
            github TEXT NOT NULL,
            signup TEXT NOT NULL
        )
        ''')

        # challenges table
        cursor.execute('''
        CREATE TABLE challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            release TEXT NOT NULL
        )
        ''')
        
        # challenges
        # - Mining
        # - Stars
        # - Weather - https://archive.ics.uci.edu/dataset/501/beijing+multi+site+air+quality+data
        # - farming
        # - News
        # - sql

        # https://data.weather.gov.hk/weatherAPI/doc/HKO_Open_Data_API_Documentation.pdf
        # https://www.kaggle.com/datasets/edumagalhaes/quality-prediction-in-a-mining-process
        # https://archive.ics.uci.edu/dataset/913/forty+soybean+cultivars+from+subsequent+harvests

        # submission

        
    print("db created")

if '-a' in sys.argv:
    with sqlite3.connect('content.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO users (username, name, password, github, signup)
        VALUES(?, ?, ?, ?, ?)
        ''', ('wingfooted', 'Alexander',
              hashlib.sha256('password'.encode()).hexdigest(),
              'https://github.com/wingfooted',
              str(datetime.date.today()))
        )

if '-c' in sys.argv:
    with sqlite3.connect('content.db') as conn:
        cursor = conn.cursor()

        cursor.execute('''
        INSERT INTO users (username, name, password, github, signup)
        VALUES(?, ?, ?, ?, ?)
        ''', ('wingfooted', 'Alexander',
              hashlib.sha256('password'.encode()).hexdigest(),
              'https://github.com/wingfooted',
              str(datetime.date.today()))
        )

if '-s' in sys.argv:
    if not os.path.exists('antarctica.db'):
        with sqlite3.connect('antarctica.db') as conn:
            cursor = conn.cursor()

            stations = {""}

            # users table
            cursor.execute('''
            CREATE TABLE mawson (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                password TEXT NOT NULL,
                github TEXT NOT NULL,
                signup TEXT NOT NULL
            )
            ''')

