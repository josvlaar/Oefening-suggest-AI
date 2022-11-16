
import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    con = None
    try:
        con = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return con

def create_table(con, create_table_sql):
    try:
        cur = con.cursor()
        cur.execute(create_table_sql)
    except Error as e:
        print(e)

def main():
    database = 'sqlite.db'

    sql_create_users = """
    CREATE TABLE IF NOT EXISTS users (
        id integer PRIMARY KEY,
        name text NOT NULL,
        avgtime integer,
        numofquestions integer
    ) """
    sql_create_questions = """
    CREATE TABLE IF NOT EXISTS questions (
        id integer PRIMARY KEY,
        question text NOT NULL,
        answerA text NOT NULL,
        answerB text NOT NULL,
        answerC text NOT NULL,
        answerD text NOT NULL,
        correctanswer text NOT NULL,
        avgtime integer NOT NULL,
        numofanswers integer
    ) """
    sql_create_answers = """
    CREATE TABLE IF NOT EXISTS answers (
        id integer PRIMARY KEY,
        user_id integer NOT NULL,
        question_id integer NOT NULL,
        answer text NOT NULL,
        timeelapsed integer NOT NULL,
        factor real NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (question_id) REFERENCES questions (id)
    ) """

    con = create_connection(database)
    if con is not None:
        create_table(con, sql_create_users)
        create_table(con, sql_create_questions)
        create_table(con, sql_create_answers)
    else:
        print("Error! cannot create the database connection.")

    

if __name__ == '__main__':
    main()