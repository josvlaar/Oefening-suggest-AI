import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="xh8PXiuYdlb0FurAIUZXKRsvWEctl8",
  database="test"
)

sql_create_users = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name TEXT NOT NULL,
        avgtime INT,
        numofquestions INT
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
        avgtime INT NOT NULL,
        numofanswers INT
    ) """
sql_create_answers = """
    CREATE TABLE IF NOT EXISTS answers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        question_id INT NOT NULL,
        answer CHAR NOT NULL,
        timeelapsed INT NOT NULL,
        factor FLOAT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (question_id) REFERENCES questions(id)
    ) """

mycursor = mydb.cursor()
mycursor.execute(sql_create_users)
mycursor.execute(sql_create_questions)
mycursor.execute(sql_create_answers)

user = input("Type your user name: ")