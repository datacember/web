import os
import sqlite3

# Define the database file name
db_file = 'sqlite.db'

# Check if the database file already exists
if not os.path.exists(db_file):
    # Connect to the SQLite database (it will create it if it doesn't exist)
    conn = sqlite3.connect(db_file)
    
    # Create a cursor object
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE
    )
    ''')

    # Create weeks table
    cursor.execute('''
    CREATE TABLE weeks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number INTEGER NOT NULL,
        name TEXT NOT NULL,
        release_date TEXT NOT NULL,
        file TEXT NOT NULL
    )
    ''')

    # Create submissions table
    cursor.execute('''
    CREATE TABLE submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        week_number INTEGER NOT NULL,
        FOREIGN KEY (week_number) REFERENCES weeks (number)
    )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    print(f'Database "{db_file}" created with the necessary tables.')
else:
    print(f'Database "{db_file}" already exists.')

