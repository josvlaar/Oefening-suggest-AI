import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="PM4b+GNNx6]1=rX7dVL'BO$mC+Gc34"
)

print(mydb)

"""
def create_connection(db_file):
    con = None
    try:
        con = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if con:
            con.close()

if __name__ == '__main__':
    create_connection('sqlite.db')


con = sqlite3.connect('sqlite.db')
cur = con.cursor()
cur.execute('CREATE TABLE users(id PRIMARY KEY, name, avgtime, NA)')
cur.execute('CREATE TABLE questions(id PRIMARY KEY, question, AA, AB, AC, AD, CA, avgtime, NA)')
cur.execute('CREATE TABLE answers(id PRIMARY KEY, user_id, question_id, answer, timeelapsed, factor)')
"""