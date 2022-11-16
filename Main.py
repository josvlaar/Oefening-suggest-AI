import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="xh8PXiuYdlb0FurAIUZXKRsvWEctl8",
  database="test"
)

mycursor = mydb.cursor()
mycursor.execute("CREATE TABLE users(name VARCHAR(255))")



sql_create_users = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name text NOT NULL,
        avgtime integer,
        numofquestions integer
    ) """
sql_create_questions = """
    CREATE TABLE IF NOT EXISTS questions (
        id INT AUTO_INCREMENT PRIMARY KEY,
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
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id integer NOT NULL,
        question_id integer NOT NULL,
        answer text NOT NULL,
        timeelapsed integer NOT NULL,
        factor real NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (question_id) REFERENCES questions(id)
    ) """