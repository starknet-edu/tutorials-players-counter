import sqlite3
con = sqlite3.connect('tutorials_events.db')
cur = con.cursor()
cur.execute('''CREATE TABLE players
               (
                   id INTEGER PRIMARY KEY,
                   account TEXT,
                   from_address TEXT,
                   blockHash TEXT,
                   transactionHash TEXT,
                   status TEXT,
                   keys TEXT,
                   rank INTEGER
               )''')


cur.execute('''CREATE TABLE exercises
               (
                   id INTEGER PRIMARY KEY,
                   account TEXT,
                   workshop INTEGER,
                   exercise INTEGER,
                   from_address TEXT,
                   blockHash TEXT,
                   transactionHash TEXT,
                   status TEXT,
                   keys TEXT
               )''')
