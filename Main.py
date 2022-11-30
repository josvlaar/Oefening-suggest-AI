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
        correctanswer CHAR NOT NULL,
        avgtime FLOAT,
        numofanswers INT
    ) """

sql_create_answers = """
    CREATE TABLE IF NOT EXISTS answers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        question_id INT NOT NULL,
        shortanswer CHAR NOT NULL,
        answer TEXT NOT NULL,
        FOREIGN KEY (question_id) REFERENCES questions(id)
    ) """

sql_create_answers_given = """
    CREATE TABLE IF NOT EXISTS answersgiven (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        question_id INT NOT NULL,
        answer_id INT NOT NULL,
        timeelapsed FLOAT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (question_id) REFERENCES questions(id),
        FOREIGN KEY (answer_id) REFERENCES answers(id)
    ) """

cursor = database.cursor(buffered=True)
cursor.execute(sql_create_users)
cursor.execute(sql_create_questions)
cursor.execute(sql_create_answers)
cursor.execute(sql_create_answers_given)

def getusertuple(name):
    sql = "SELECT * FROM users WHERE name = %s"
    cursor.execute(sql, (name,))
    return cursor.fetchone()

username = input("Type your user name: ")
usertuple = getusertuple(username)
if usertuple is None:
    sql = "INSERT INTO users (name) VALUES (%s)"
    cursor.execute(sql, (username,))
    database.commit()
    usertuple = getusertuple(username)

totalaveragetime = 0
oppositetime = 0
suggestedquestionID = 0
questiontuple = 0

def getquestiontuple(id):
    sql = "SELECT * FROM questions WHERE id = %s"
    cursor.execute(sql, (id,))
    return cursor.fetchone()

cursor.execute("SELECT COUNT(numofanswers) FROM questions")
numofanswers = cursor.fetchone()
print("Numofanswers: ", numofanswers)
if numofanswers[0] == 0: # Er zijn geen vragen gemaakt
    totalaveragetime = starttime
    suggestedquestionID = averagequestionID
    questiontuple = getquestiontuple(suggestedquestionID)
else: # Er zijn vragen gemaakt
    cursor.execute("SELECT SUM(avgtime*numofanswers) FROM questions")
    totaltime = cursor.fetchone()
    print("Totaltime: ", totaltime)
    cursor.execute("SELECT SUM(numofanswers) FROM questions")
    totalnumofanswers = cursor.fetchone()
    print("Totalnumofanswers: ", totalnumofanswers)
    totalaveragetime = totaltime[0]/float(totalnumofanswers[0])

    cursor.execute("SELECT id FROM questions WHERE numofanswers IS NULL")
    result = cursor.fetchone()
    if result is not None: # Er zijn niet gemaakte vragen
        suggestedquestionID = result[0]
        questiontuple = getquestiontuple(suggestedquestionID)
    else: # Alle vragen zijn gemaakt
        if usertuple[3] is not None: # Gebruiker heeft vragen gemaakt
            oppositetime = 2 * totalaveragetime - usertuple[2]
        else: # Gebruiker heeft geen vragen gemaakt
            oppositetime = totalaveragetime

        # Zoek de vraag het dichtst bij oppositetime (die niet al eerder gemaakt is door gebruiker)
        sql = "SELECT * FROM questions WHERE id NOT IN (SELECT DISTINCT question_id FROM answersgiven WHERE user_id = %s) ORDER BY ABS(%s - avgtime) ASC LIMIT 1"
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
sql = "SELECT COUNT(answer) FROM answers WHERE question_id = %s"
cursor.execute(sql, (questiontuple[0],))
answers = cursor.fetchone()
avgnumofpenalties = (answers[0] - 1) / 2
if questiontuple[3] is None: penalty = totalaveragetime/avgnumofpenalties
else: penalty = questiontuple[3]/avgnumofpenalties
print("Penalty: ", penalty)
print("Avgnumofpenalties: ", avgnumofpenalties)

# Vraag maken
sql = "SELECT * FROM answers WHERE question_id = %s"
cursor.execute(sql, (questiontuple[0],))
answers = cursor.fetchall()
print("Answers: ", answers)

shortanswer = 0
shortanswersgiven = []
answersgiven = []
totaltime = 0
timeelapsed = 0
while shortanswer != questiontuple[2]:
    if len(answers) - 1 == len(answersgiven):
        shortanswer = questiontuple[2]
        timeelapsed = 0
    else:
        shortanswer = input("Submit your answer: ")
        timeelapsed = round(float(input("Submit time elapsed before answering: ")), 1)    
    if shortanswersgiven.count(shortanswer) == 1:
        print("Earlier answer submitted")
        continue
    else:
        shortanswersgiven.append(shortanswer)
        totaltime += timeelapsed
        if shortanswer != questiontuple[2]: totaltime += penalty

    sql = "SELECT id FROM answers WHERE question_id = %s AND shortanswer = %s"
    cursor.execute(sql, (questiontuple[0], shortanswer))    
    answer_id = cursor.fetchone()
    answersgiven.append((usertuple[0], questiontuple[0], answer_id[0], timeelapsed))
    print("Answers given: ", answersgiven)

sql = "INSERT INTO answersgiven (user_id, question_id, answer_id, timeelapsed) VALUES (%s, %s, %s, %s)"
cursor.executemany(sql, answersgiven)
database.commit()
    
# Database updaten
sql = "UPDATE questions SET avgtime = %s, numofanswers = %s WHERE id = %s"
if questiontuple[3] is None:
    cursor.execute(sql, (totaltime, 1, questiontuple[0]))
    database.commit()
else:
    numofanswers = questiontuple[4]
    avgtime = questiontuple[3]
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