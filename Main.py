import mysql.connector

# Connect to database
database = mysql.connector.connect(
  host="localhost",
  user="root",
  password="xh8PXiuYdlb0FurAIUZXKRsvWEctl8",
  database="sample1"
)

# Default values for first question
STARTTIME = 300
AVERAGE_QUESTION_ID = 1

# Create database tables if they don't exist yet
SQL_CREATE_USERS = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        avgtime FLOAT,
        numofquestions INT,
        UNIQUE (name)
    ) """
SQL_CREATE_QUESTIONS = """
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
SQL_CREATE_ANSWERS = """
    CREATE TABLE IF NOT EXISTS answers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        question_id INT NOT NULL,
        answer CHAR NOT NULL,
        timeelapsed FLOAT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (question_id) REFERENCES questions(id)
    ) """

# Create cursor and execute SQL create statements
cursor = database.cursor(buffered=True)
cursor.execute(SQL_CREATE_USERS)
cursor.execute(SQL_CREATE_QUESTIONS)
cursor.execute(SQL_CREATE_ANSWERS)

# Global variables
total_average_time = 0
opposite_time = 0
suggested_question_ID = 0
user_tuple = 0
question_tuple = 0

# Helper functions
def get_user_tuple(name):
    sql = "SELECT * FROM users WHERE name = %s"
    cursor.execute(sql, (name,))
    return cursor.fetchone()

def get_question_tuple(id):
    sql = "SELECT * FROM questions WHERE id = %s"
    cursor.execute(sql, (id,))
    return cursor.fetchone()

# Enter user_name + add to database and/or get user tuple
user_name = input("Type your user name: ")
user_tuple = get_user_tuple(user_name)
if user_tuple is None:
    sql = "INSERT INTO users (name) VALUES (%s)"
    cursor.execute(sql, (user_name,))
    database.commit()
    user_tuple = get_user_tuple(user_name)

# Check whether there are questions answered
cursor.execute("SELECT COUNT(numofanswers) FROM questions")
num_of_answers = cursor.fetchone()
print("Num_of_answers: ", num_of_answers)
if num_of_answers[0] == 0: # There are no questions made, assign default values
    total_average_time = STARTTIME
    opposite_time = STARTTIME
    suggested_question_ID = AVERAGE_QUESTION_ID
    question_tuple = get_question_tuple(suggested_question_ID)
else: # There are questions made, calculate total_average_time
    cursor.execute("SELECT SUM(avgtime*numofanswers) FROM questions")
    total_time = cursor.fetchone()
    cursor.execute("SELECT SUM(numofanswers) FROM questions")
    TOTAL_NUM_OF_ANSWERS = cursor.fetchone()
    print("Total_time: ", total_time)
    print("Total_num_of_answers: ", TOTAL_NUM_OF_ANSWERS)
    total_average_time = total_time[0]/float(TOTAL_NUM_OF_ANSWERS[0])

    # Check whether all questions have been answered at least once
    cursor.execute("SELECT id FROM questions WHERE avgtime IS NULL")
    result = cursor.fetchone()
    if result is not None: # There are questions not answered yet
        suggested_question_ID = result[0]
        question_tuple = get_question_tuple(suggested_question_ID)
    else: # All questions have been answered at least once
        if user_tuple[2] is not None: # User has answered some questions
            opposite_time = 2 * total_average_time - user_tuple[2]
        else: # User has not answered any questions yet
            opposite_time = total_average_time

        # Search for the question whose average is closest to oppositetime, that has not been answered before by the user
        sql = "SELECT * FROM questions WHERE id NOT IN (SELECT DISTINCT question_id FROM answers WHERE user_id = %s) ORDER BY ABS(%s - avgtime) ASC LIMIT 1"
        cursor.execute(sql, (user_tuple[0], opposite_time))
        question_tuple = cursor.fetchone()
        if question_tuple is None:
            print("You have answered all questions")
            exit()
        else: suggested_question_ID = question_tuple[0]

# Print intermediate values
print("Total_average_time: ", total_average_time)
print("Opposite_time: ", opposite_time)
print("Suggested_question_ID: ", suggested_question_ID)
print("User_tuple: ", user_tuple)
print("Question_tuple: ", question_tuple)

# Calculate penalty, global variables
penalty = 0
avg_num_of_penalties = 0
if question_tuple[8] is None: # Question has not been answered before
    avg_num_of_penalties = 1.5
    penalty = total_average_time/avg_num_of_penalties
else: # Question has been answered before
    sql = "SELECT COUNT(answer) FROM answers WHERE question_id = %s"
    cursor.execute(sql, (question_tuple[0],))
    answers = cursor.fetchone()
    CORRECT_ANSWERS = question_tuple[8]
    ERRORS = answers[0] - CORRECT_ANSWERS
    if ERRORS == 0: # No errors have been made yet answering the question
        avg_num_of_penalties = 1.5
    else:   # There have been errors made answering the question
        avg_num_of_penalties = ERRORS / CORRECT_ANSWERS
    penalty = question_tuple[7] / avg_num_of_penalties
# Print intermediate values
print("Penalty: ", penalty)
print("Avg_num_of_penalties: ", avg_num_of_penalties)

# Answering the question
answer = 0
answers = []
total_time = 0
while answer != question_tuple[6]:
    answer = input("Submit your answer: ")
    TIME_ELAPSED = round(float(input("Submit time elapsed before answering: ")), 1)
    answers.append((user_tuple[0], question_tuple[0], answer, TIME_ELAPSED))
    print("Answers: ", answers)
    total_time += TIME_ELAPSED
    if answer != question_tuple[6]: total_time += penalty
# Correct answer given, update database answers table
sql = "INSERT INTO answers (user_id, question_id, answer, timeelapsed) VALUES (%s, %s, %s, %s)"
cursor.executemany(sql, answers)
database.commit()

# Update database questions table
sql = "UPDATE questions SET avgtime = %s, numofanswers = %s WHERE id = %s"
if question_tuple[7] is None: # Question not answered before
    cursor.execute(sql, (total_time, 1, question_tuple[0]))
else: # Question answered before
    num_of_answers = question_tuple[8]
    avg_time = question_tuple[7]
    total_answer_time = (num_of_answers * avg_time + total_time) / (num_of_answers + 1)
    num_of_answers += 1
    total_answer_time = round(total_answer_time, 1)
    cursor.execute(sql, (total_answer_time, num_of_answers, question_tuple[0]))
database.commit()

# Update database users table
sql = "UPDATE users SET avgtime = %s, numofquestions = %s WHERE id = %s"
if user_tuple[2] is None: # User has not answered questions before
    cursor.execute(sql, (total_time, 1, user_tuple[0]))
else: # User has answered questions before
    num_of_questions = user_tuple[3]
    avg_time = user_tuple[2]
    total_question_time = (num_of_questions * avg_time + total_time) / (num_of_questions + 1)
    num_of_questions += 1
    total_question_time = round(total_question_time, 1)
    cursor.execute(sql, (total_question_time, num_of_questions, user_tuple[0]))
database.commit()