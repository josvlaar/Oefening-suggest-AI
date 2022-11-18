import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="xh8PXiuYdlb0FurAIUZXKRsvWEctl8",
  database="sample1"
)

starttime = 300
averagequestionID = 1

sql_create_users = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        avgtime FLOAT,
        numofquestions INT,
        UNIQUE (name)
    ) """
sql_create_questions = """
    CREATE TABLE IF NOT EXISTS questions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        question TEXT NOT NULL,
        answerA TEXT NOT NULL,
        answerB TEXT NOT NULL,
        answerC TEXT NOT NULL,
        answerD TEXT NOT NULL,
        correctanswer CHAR NOT NULL,
        avgtime FLOAT,
        numofanswers INT
    ) """
sql_create_answers = """
    CREATE TABLE IF NOT EXISTS answers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        question_id INT NOT NULL,
        answer CHAR NOT NULL,
        timeelapsed FLOAT NOT NULL,
        factor FLOAT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (question_id) REFERENCES questions(id)
    ) """

mycursor = mydb.cursor()
mycursor.execute(sql_create_users)
mycursor.execute(sql_create_questions)
mycursor.execute(sql_create_answers)

user = input("Type your user name: ")
mycursor.execute("SELECT name FROM users")
result = mycursor.fetchall()
found = False
for x in result:
    if x == (user,):
        found = True
        break
if not found:
    sql = "INSERT INTO users (name) VALUES (%s)"
    mycursor.execute(sql, (user,))
    mydb.commit()

numofanswers = mycursor.execute("SELECT COUNT(*) FROM answers")
if numofanswers is None:
    totalaverage = starttime
    suggestedquestionID = averagequestionID
else:
    pass



def func():
    pass
