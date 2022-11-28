import mysql.connector

database = mysql.connector.connect(
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
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (question_id) REFERENCES questions(id)
    ) """

cursor = database.cursor(buffered=True)
cursor.execute(sql_create_users)
cursor.execute(sql_create_questions)
cursor.execute(sql_create_answers)

totalaveragetime = 0
oppositetime = 0
suggestedquestionID = 0
usertuple = 0
questiontuple = 0

def getusertuple(name):
    sql = "SELECT * FROM users WHERE name = %s"
    cursor.execute(sql, (name,))
    return cursor.fetchone()

def getquestiontuple(id):
    sql = "SELECT * FROM questions WHERE id = %s"
    cursor.execute(sql, (id,))
    return cursor.fetchone()

username = input("Type your user name: ")
usertuple = getusertuple(username)
if usertuple is None:
    sql = "INSERT INTO users (name) VALUES (%s)"
    cursor.execute(sql, (username,))
    database.commit()
    usertuple = getusertuple(username)

cursor.execute("SELECT COUNT(numofanswers) FROM questions")
numofanswers = cursor.fetchone()
print("Numofanswers: ", numofanswers)
if numofanswers[0] == 0: # Er zijn geen antwoorden
    totalaveragetime = starttime
    oppositetime = starttime
    suggestedquestionID = averagequestionID
    questiontuple = getquestiontuple(suggestedquestionID)
else: # Er zijn antwoorden
    cursor.execute("SELECT SUM(avgtime*numofanswers) FROM questions")
    totaltime = cursor.fetchone()
    cursor.execute("SELECT SUM(numofanswers) FROM questions")
    totalnumofanswers = cursor.fetchone()
    print("Totaltime: ", totaltime)
    print("Totalnumofanswers: ", totalnumofanswers)
    totalaveragetime = totaltime[0]/float(totalnumofanswers[0])

    cursor.execute("SELECT id FROM questions WHERE avgtime IS NULL")
    result = cursor.fetchone()
    if result is not None: # Er zijn niet gemaakte vragen
        suggestedquestionID = result[0]
        questiontuple = getquestiontuple(suggestedquestionID)
    else: # Alle vragen zijn gemaakt
        if usertuple[2] is not None: # Gebruiker heeft vragen gemaakt
            oppositetime = 2 * totalaveragetime - usertuple[2]
        else: # Gebruiker heeft geen vragen gemaakt
            oppositetime = totalaveragetime

        # Zoek de vraag het dichtst bij oppositetime (die niet al eerder gemaakt is door gebruiker)
        sql = "SELECT * FROM questions WHERE id NOT IN (SELECT DISTINCT question_id FROM answers WHERE user_id = %s) ORDER BY ABS(%s - avgtime) ASC LIMIT 1"
        cursor.execute(sql, (usertuple[0], oppositetime))
        questiontuple = cursor.fetchone()
        if questiontuple is None: print("You have answered all questions")
        else: suggestedquestionID = questiontuple[0]

print("Totalaveragetime: ", totalaveragetime)
print("Oppositetime: ", oppositetime)
print("SuggestedquestionID: ", suggestedquestionID)
print("Usertuple: ", usertuple)
print("Questiontuple: ", questiontuple)

if questiontuple is None: exit()

# Reken penalty uit
penalty = 0
avgnumofpenalties = 0
if questiontuple[8] is None: # Vraag is niet eerder gemaakt
    avgnumofpenalties = 1.5
    penalty = totalaveragetime/avgnumofpenalties
else: # Vraag is eerder gemaakt
    sql = "SELECT COUNT(answer) FROM answers WHERE question_id = %s"
    cursor.execute(sql, (questiontuple[0],))
    answers = cursor.fetchone()
    correctanswers = questiontuple[8]
    errors = answers[0] - correctanswers
    if errors == 0: # Nog geen fouten gemaakt bij vraag
        avgnumofpenalties = 1.5
    else:   # Wel eerder fouten gemaakt
        avgnumofpenalties = errors / correctanswers
    penalty = questiontuple[7] / avgnumofpenalties
print("Penalty: ", penalty)
print("Avgnumofpenalties: ", avgnumofpenalties)

# Vraag maken
answer = 0
answers = []
totaltime = 0
while answer != questiontuple[6]:
    answer = input("Submit your answer: ")
    timeelapsed = round(float(input("Submit time elapsed before answering: ")), 1)
    answers.append((usertuple[0], questiontuple[0], answer, timeelapsed))
    print("Answers: ", answers)
    totaltime += timeelapsed
    if answer != questiontuple[6]: totaltime += penalty
sql = "INSERT INTO answers (user_id, question_id, answer, timeelapsed) VALUES (%s, %s, %s, %s)"
cursor.executemany(sql, answers)
database.commit()

# Database updaten
sql = "UPDATE questions SET avgtime = %s, numofanswers = %s WHERE id = %s"
if questiontuple[7] is None:
    cursor.execute(sql, (totaltime, 1, questiontuple[0]))
    database.commit()
else:
    numofanswers = questiontuple[8]
    avgtime = questiontuple[7]
    totalanswertime = (numofanswers * avgtime + totaltime) / (numofanswers + 1)
    numofanswers += 1
    totalanswertime = round(totalanswertime, 1)
    cursor.execute(sql, (totalanswertime, numofanswers, questiontuple[0]))
    database.commit()
sql = "UPDATE users SET avgtime = %s, numofquestions = %s WHERE id = %s"
if usertuple[2] is None:
    cursor.execute(sql, (totaltime, 1, usertuple[0]))
    database.commit()
else:
    numofquestions = usertuple[3]
    avgtime = usertuple[2]
    totalquestiontime = (numofquestions * avgtime + totaltime) / (numofquestions + 1)
    numofquestions += 1
    totalquestiontime = round(totalquestiontime, 1)
    cursor.execute(sql, (totalquestiontime, numofquestions, usertuple[0]))
    database.commit()