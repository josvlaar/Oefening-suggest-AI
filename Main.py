import sqlite3
dbconnection = sqlite3.connect('sqlite.db')
cursor = dbconnection.cursor()
cursor.execute('CREATE TABLE users(id PRIMARY KEY, name, avgscore)')
cursor.execute('CREATE TABLE questions(id PRIMARY KEY, question, answer, avgtime, avgscore)')
cursor.execute('CREATE TABLE answers(user, question, answer, timeelapsed)')
