import mysql.connector

# Connect to database
database = mysql.connector.connect(
  host="localhost",
  user="root",
  password="xh8PXiuYdlb0FurAIUZXKRsvWEctl8",
  database="sample1"
)

# Default values for first question
START_TIME = 300
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
        correctanswer CHAR NOT NULL,
        avgtime FLOAT,
        numofanswers INT
    ) """

SQL_CREATE_ANSWERS = """
    CREATE TABLE IF NOT EXISTS answers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        question_id INT NOT NULL,
        shortanswer CHAR NOT NULL,
        answer TEXT NOT NULL,
        FOREIGN KEY (question_id) REFERENCES questions(id)
    ) """

SQL_CREATE_ANSWERS_GIVEN = """
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
cursor.execute(SQL_CREATE_USERS)
cursor.execute(SQL_CREATE_QUESTIONS)
cursor.execute(SQL_CREATE_ANSWERS)
cursor.execute(SQL_CREATE_ANSWERS_GIVEN)

# Helper function
def get_user_tuple(name):
    sql = "SELECT * FROM users WHERE name = %s"
    cursor.execute(sql, (name,))
    return cursor.fetchone()

# Enter username + add to database and/or get user tuple
username = input("Type your user name: ")
user_tuple = get_user_tuple(username)
if user_tuple is None:
    sql = "INSERT INTO users (name) VALUES (%s)"
    cursor.execute(sql, (username,))
    database.commit()
    user_tuple = get_user_tuple(username)

# Global variables
total_average_time = 0
opposite_time = 0
suggested_question_ID = 0
question_tuple = 0

# Helper function
def get_question_tuple(id):
    sql = "SELECT * FROM questions WHERE id = %s"
    cursor.execute(sql, (id,))
    return cursor.fetchone()

# Check whether there are questions answered
cursor.execute("SELECT COUNT(numofanswers) FROM questions")
num_of_answers = cursor.fetchone()
print("Num_of_answers: ", num_of_answers)
if num_of_answers[0] == 0: # There are no questions made, assign default values
    total_average_time = START_TIME
    suggested_question_ID = AVERAGE_QUESTION_ID
    question_tuple = get_question_tuple(suggested_question_ID)
else: # There are questions made, calculate total_average_time
    cursor.execute("SELECT SUM(avgtime*numofanswers) FROM questions")
    total_time = cursor.fetchone()
    print("Total_time: ", total_time)
    cursor.execute("SELECT SUM(numofanswers) FROM questions")
    TOTAL_NUM_OF_ANSWERS = cursor.fetchone()
    print("Total_num_of_answers: ", TOTAL_NUM_OF_ANSWERS)
    total_average_time = total_time[0]/float(TOTAL_NUM_OF_ANSWERS[0])

    # Check whether all questions have been answered at least once
    cursor.execute("SELECT id FROM questions WHERE numofanswers IS NULL")
    result = cursor.fetchone()
    if result is not None: # There are questions not answered yet
        suggested_question_ID = result[0]
        question_tuple = get_question_tuple(suggested_question_ID)
    else: # All questions have been answered at least once
        if user_tuple[3] is not None: # User has answered some questions
            opposite_time = 2 * total_average_time - user_tuple[2]
        else: # User has not answered any questions yet
            opposite_time = total_average_time

        # Search for the question whose average is closest to opposite_time, that has not been answered before by the user
        sql = "SELECT * FROM questions WHERE id NOT IN (SELECT DISTINCT question_id FROM answersgiven WHERE user_id = %s) ORDER BY ABS(%s - avgtime) ASC LIMIT 1"
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

# Calculate penalty as global variable
penalty = 0
avg_num_of_penalties = 0
sql = "SELECT COUNT(answer) FROM answers WHERE question_id = %s"
cursor.execute(sql, (question_tuple[0],))
answers = cursor.fetchone()
avg_num_of_penalties = (answers[0] - 1) / 2
if question_tuple[3] is None: # Question has not been answered before
    penalty = total_average_time/avg_num_of_penalties
else: # Question has been answered before
    penalty = question_tuple[3]/avg_num_of_penalties
print("Penalty: ", penalty)
print("Avg_num_of_penalties: ", avg_num_of_penalties)

# Print answers
sql = "SELECT * FROM answers WHERE question_id = %s"
cursor.execute(sql, (question_tuple[0],))
answers = cursor.fetchall()
print("Answers: ", answers)
# Create list of valid answers and print it
valid_answers = []
for short_answer in answers:
    valid_answers.append(short_answer[2])
print("Valid_answers: ", valid_answers)

# Answering the question, global variables
short_answer = 0
short_answers_given = []
answers_given = []
total_time = 0
time_elapsed = 0
while short_answer != question_tuple[2]: # While wrong answer submitted
    if len(answers) - 1 == len(answers_given): # Check if only one answer remaining
        short_answer = question_tuple[2] # Automatically give correct answer
        time_elapsed = 0 # No time elapsed when one answer (correct answer) remaining
    else: # More than one answer remaining, check if valid answer given (if not continue)
        short_answer = input("Submit your answer: ")
        time_elapsed = round(float(input("Submit time elapsed before answering: ")), 1)
        if valid_answers.count(short_answer) != 1:
            print("Invalid answer given")
            continue
    if short_answers_given.count(short_answer) == 1: # Check if earlier answer submitted
        print("Earlier answer submitted")
        continue
    else: # New answer submitted
        short_answers_given.append(short_answer)
        total_time += time_elapsed # Calculate total timescore for question
        if short_answer != question_tuple[2]: total_time += penalty

        # Add new answer given to answersgiven list
        sql = "SELECT id FROM answers WHERE question_id = %s AND shortanswer = %s"
        cursor.execute(sql, (question_tuple[0], short_answer))    
        answer_id = cursor.fetchone()
        answers_given.append((user_tuple[0], question_tuple[0], answer_id[0], time_elapsed))
        print("Answers_given: ", answers_given)

    # Break out of the loop if totaltime equal to or greater than worst score when guessing
    if total_time >= (len(answers) - 1) * penalty:
        total_time = (len(answers) - 1) * penalty
        break  

# Update database answersgiven table by inserting answers_given list
sql = "INSERT INTO answersgiven (user_id, question_id, answer_id, timeelapsed) VALUES (%s, %s, %s, %s)"
cursor.executemany(sql, answers_given)
database.commit()
    
# Update database questions table
sql = "UPDATE questions SET avgtime = %s, numofanswers = %s WHERE id = %s"
if question_tuple[3] is None: # Question not answered before
    cursor.execute(sql, (total_time, 1, question_tuple[0]))
else: # Question answered before
    num_of_answers = question_tuple[4]
    avg_time = question_tuple[3]
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