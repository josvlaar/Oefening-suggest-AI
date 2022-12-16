import mysql.connector

# Connect to database
database = mysql.connector.connect(
  host="localhost",
  user="root",
  password="xh8PXiuYdlb0FurAIUZXKRsvWEctl8",
  database="sample1"
)

# Default values for first question
starttime = 300
averagequestionID = 1

# Create database tables if they don't exist yet
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

# Create cursor and execute SQL create statements
cursor = database.cursor(buffered=True)
cursor.execute(sql_create_users)
cursor.execute(sql_create_questions)
cursor.execute(sql_create_answers)
cursor.execute(sql_create_answers_given)

# Helper function
def getusertuple(name):
    sql = "SELECT * FROM users WHERE name = %s"
    cursor.execute(sql, (name,))
    return cursor.fetchone()

# Enter username + add to database and/or get user tuple
username = input("Type your user name: ")
usertuple = getusertuple(username)
if usertuple is None:
    sql = "INSERT INTO users (name) VALUES (%s)"
    cursor.execute(sql, (username,))
    database.commit()
    usertuple = getusertuple(username)

# Global variables
totalaveragetime = 0
oppositetime = 0
suggestedquestionID = 0
questiontuple = 0

# Helper function
def getquestiontuple(id):
    sql = "SELECT * FROM questions WHERE id = %s"
    cursor.execute(sql, (id,))
    return cursor.fetchone()

# Check whether there are questions answered
cursor.execute("SELECT COUNT(numofanswers) FROM questions")
numofanswers = cursor.fetchone()
print("Numofanswers: ", numofanswers)
if numofanswers[0] == 0: # There are no questions made, assign default values
    totalaveragetime = starttime
    suggestedquestionID = averagequestionID
    questiontuple = getquestiontuple(suggestedquestionID)
else: # There are questions made, calculate totalaveragetime
    cursor.execute("SELECT SUM(avgtime*numofanswers) FROM questions")
    totaltime = cursor.fetchone()
    print("Totaltime: ", totaltime)
    cursor.execute("SELECT SUM(numofanswers) FROM questions")
    totalnumofanswers = cursor.fetchone()
    print("Totalnumofanswers: ", totalnumofanswers)
    totalaveragetime = totaltime[0]/float(totalnumofanswers[0])

    # Check whether all questions have been answered at least once
    cursor.execute("SELECT id FROM questions WHERE numofanswers IS NULL")
    result = cursor.fetchone()
    if result is not None: # There are questions not answered yet
        suggestedquestionID = result[0]
        questiontuple = getquestiontuple(suggestedquestionID)
    else: # All questions have been answered at least once
        if usertuple[3] is not None: # User has answered some questions
            oppositetime = 2 * totalaveragetime - usertuple[2]
        else: # User has not answered any questions yet
            oppositetime = totalaveragetime

        # Search for the question whose average is closest to oppositetime, that has not been answered before by the user
        sql = "SELECT * FROM questions WHERE id NOT IN (SELECT DISTINCT question_id FROM answersgiven WHERE user_id = %s) ORDER BY ABS(%s - avgtime) ASC LIMIT 1"
        cursor.execute(sql, (usertuple[0], oppositetime))
        questiontuple = cursor.fetchone()
        if questiontuple is None:
            print("You have answered all questions")
            exit()
        else: suggestedquestionID = questiontuple[0]

# Print intermediate values
print("Totalaveragetime: ", totalaveragetime)
print("Oppositetime: ", oppositetime)
print("SuggestedquestionID: ", suggestedquestionID)
print("Usertuple: ", usertuple)
print("Questiontuple: ", questiontuple)

# Calculate penalty as global variable
penalty = 0
avgnumofpenalties = 0
sql = "SELECT COUNT(answer) FROM answers WHERE question_id = %s"
cursor.execute(sql, (questiontuple[0],))
answers = cursor.fetchone()
avgnumofpenalties = (answers[0] - 1) / 2
if questiontuple[3] is None: # Question has not been answered before
    penalty = totalaveragetime/avgnumofpenalties
else: # Question has been answered before
    penalty = questiontuple[3]/avgnumofpenalties
print("Penalty: ", penalty)
print("Avgnumofpenalties: ", avgnumofpenalties)

# Print answers
sql = "SELECT * FROM answers WHERE question_id = %s"
cursor.execute(sql, (questiontuple[0],))
answers = cursor.fetchall()
print("Answers: ", answers)

# Answering the question, global variables
shortanswer = 0
shortanswersgiven = []
answersgiven = []
totaltime = 0
timeelapsed = 0
while shortanswer != questiontuple[2]: # While wrong answer submitted
    if len(answers) - 1 == len(answersgiven): # Check if only one answer remaining
        shortanswer = questiontuple[2] # Automatically give correct answer
        timeelapsed = 0 # No time elapsed when one answer (correct answer) remaining
    else: # More than one answer remaining
        shortanswer = input("Submit your answer: ")
        timeelapsed = round(float(input("Submit time elapsed before answering: ")), 1)    
    if shortanswersgiven.count(shortanswer) == 1: # Check if earlier answer submitted
        print("Earlier answer submitted")
        continue
    else: # New answer submitted
        shortanswersgiven.append(shortanswer)
        totaltime += timeelapsed # Calculate total timescore for question
        if shortanswer != questiontuple[2]: totaltime += penalty

    # Add new answer given to answersgiven list
    sql = "SELECT id FROM answers WHERE question_id = %s AND shortanswer = %s"
    cursor.execute(sql, (questiontuple[0], shortanswer))    
    answer_id = cursor.fetchone()
    answersgiven.append((usertuple[0], questiontuple[0], answer_id[0], timeelapsed))
    print("Answers given: ", answersgiven)

# Update database answersgiven table by inserting answersgiven list
sql = "INSERT INTO answersgiven (user_id, question_id, answer_id, timeelapsed) VALUES (%s, %s, %s, %s)"
cursor.executemany(sql, answersgiven)
database.commit()
    
# Update database questions table
sql = "UPDATE questions SET avgtime = %s, numofanswers = %s WHERE id = %s"
if questiontuple[3] is None: # Question not answered before
    cursor.execute(sql, (totaltime, 1, questiontuple[0]))
else: # Question answered before
    numofanswers = questiontuple[4]
    avgtime = questiontuple[3]
    totalanswertime = (numofanswers * avgtime + totaltime) / (numofanswers + 1)
    numofanswers += 1
    totalanswertime = round(totalanswertime, 1)
    cursor.execute(sql, (totalanswertime, numofanswers, questiontuple[0]))
database.commit()

# Update database users table
sql = "UPDATE users SET avgtime = %s, numofquestions = %s WHERE id = %s"
if usertuple[2] is None: # User has not answered questions before
    cursor.execute(sql, (totaltime, 1, usertuple[0]))
else: # User has answered questions before
    numofquestions = usertuple[3]
    avgtime = usertuple[2]
    totalquestiontime = (numofquestions * avgtime + totaltime) / (numofquestions + 1)
    numofquestions += 1
    totalquestiontime = round(totalquestiontime, 1)
    cursor.execute(sql, (totalquestiontime, numofquestions, usertuple[0]))
database.commit()