import os
import math
import hashlib
import sqlite3
import sys
import datetime
import pandas as pd

db_file = 'content.db'

# adding flags system

if '-d' in sys.argv:
    try:
        os.remove('content.db')
    finally:
        pass
    try:
        os.remove('antarctica.db')
    finally:
        pass

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
            html TEXT NOT NULL,
            release TEXT NOT NULL
        )
        ''')

        query = '''
        INSERT INTO challenges (name, html, release)
        VALUES (?, ?, ?)
        '''

        challenges = (
                ("Stars", "stars", "2024-12-1"),
                ("Weeding out the Noise", "farming", "2024-12-5"),
                ("Froth Flotation", "mining", "2024-12-9"),
                ("SQLippery when icy!", "cold", "2024-12-16")
        )

        for challenge in challenges:
            cursor.execute(query, challenge)
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

        # tokens
        # challenges table

        cursor.execute('''
        CREATE TABLE tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT NOT NULL,
            user TEXT NOT NULL,
            year INTEGER,
            month INTEGER,
            day INTEGER,
            hour INTEGER,
            minute INTEGER
        )
        ''')

        cursor.execute('''
        CREATE TABLE queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token INTEGER,
            user TEXT,
            user_query TEXT,
            time REAL,
            runtime TEXT,
            row_length INTEGER
        )
        ''')

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

if '-ice' in sys.argv:
    if not os.path.exists('antarctica.db'):
        with sqlite3.connect('antarctica.db') as conn:
            cursor = conn.cursor()

            stations = {"casey", "davis", "mawson",
                        "macquarrie_island"}
            months = {
                "oct": 10,
                "sep": 9,
                "aug": 8,
                "jul": 7,
                "jun": 6,
                "may": 5
            }

            rename_dict = {
                'Unnamed: 0': 'ID',
                'Date': 'Date',
                'Minimum temperature (°C)': 'MinTemp',
                'Maximum temperature (°C)': 'MaxTemp',
                'Rainfall (mm)': 'Rainfall',
                'Evaporation (mm)': 'Evap',
                'Sunshine (hours)': 'Sunshine',
                'Direction of maximum wind gust ': 'GustDir',
                'Speed of maximum wind gust (km/h)': 'GustSpeed',
                'Time of maximum wind gust': 'GustTime',
                '9am Temperature (°C)': 'Temp9am',
                '9am relative humidity (%)': 'Humid9am',
                '9am cloud amount (oktas)': 'Cloud9am',
                '9am wind direction': 'WindDir9am',
                '9am wind speed (km/h)': 'WindSpd9am',
                '9am MSL pressure (hPa)': 'Press9am',
                '3pm Temperature (°C)': 'Temp3pm',
                '3pm relative humidity (%)': 'Humid3pm',
                '3pm cloud amount (oktas)': 'Cloud3pm',
                '3pm wind direction': 'WindDir3pm',
                '3pm wind speed (km/h)': 'WindSpd3pm',
                '3pm MSL pressure (hPa)': 'Press3pm'
            }

            for station in stations:
                cursor.execute(f'''
                CREATE TABLE {station} (
                    Day INTEGER NOT NULL,
                    Month INTEGER NOT NULL,
                    Year INTEGER NOT NULL,
                    MinTemp REAL,
                    MaxTemp REAL,
                    Rainfall REAL,
                    Evap REAL,
                    Sunshine REAL,
                    GustDir TEXT,
                    GustSpeed REAL,
                    GustTime TEXT,
                    Temp9am REAL,
                    Humid9am REAL,
                    Cloud9am INTEGER,
                    WindDir9am TEXT,
                    Windspd9am REAL,
                    Press9am REAL,
                    Temp3pm REAL,
                    Humid3pm REAL,
                    Cloud3pm INTEGER,
                    WindDir3pm TEXT,
                    Windspd3pm REAL,
                    Press3pm REAL,
                    PRIMARY KEY (Day, Month, Year)
                );
            ''')

            # parsing all dataframes
            for station in stations:
                for month, month_number in months.items():
                    csv_name = f"{station}_{month}.csv"
                    df = pd.read_csv(f'antartica/{csv_name}')
                    df = df.rename(columns=rename_dict)
                    for index, row in df.iterrows():
                        row = row.to_dict()
                        year, month, day = row['Date'].split('-')
                        processed_row = {key: f"'{str(value)}'"
                                         for key, value in row.items()
                                         if (key != 'Date') and (pd.notna(value))}

                        processed_row['Year'] = year
                        processed_row['Month'] = month
                        processed_row['Day'] = day
                        insert = f"""
                        INSERT INTO {station} ({', '.join(processed_row.keys())})
                        VALUES ({', '.join(processed_row.values())})
                        """
                        cursor.execute(insert)

            print("testing")
