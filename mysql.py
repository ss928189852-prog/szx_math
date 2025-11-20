import pymysql
from sqlalchemy import false


def connect_to_db():
    connection = pymysql.connect(host='rm-wz9wb5d61opb097g5go.mysql.rds.aliyuncs.com', user='root', password='Ss950721',
                               db='eduhk_gpt', port=3306, charset='utf8')
    return connection


def select_choice_data():
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            sql_select = "SELECT * FROM student_choice_info"
            cursor.execute(sql_select)
            results = cursor.fetchall()
            return results
    finally:
        connection.close()

def select_chatbot_data():
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            sql_select = "SELECT * FROM chatbot_use_info"
            cursor.execute(sql_select)
            results = cursor.fetchall()
            return results
    finally:
        connection.close()


def insert_student_choice_info(Username, Question_bank, Question_id, Student_choice, Correct_answer, Chatbot_state):
    connection = connect_to_db()
    school_id = "A"
    try:
        with connection.cursor() as cursor:
            sql_insert = "INSERT INTO student_choice_info_30102025 (school_id, username, question_bank, question_id, student_choice, correct_answer, chatbot_state) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql_insert, (school_id, Username, Question_bank, Question_id, Student_choice, Correct_answer, Chatbot_state))
        connection.commit()
    finally:
        connection.close()

def insert_ai_suggestion_info(Username, Score, Suggestion):
    connection = connect_to_db()
    school_id = "A"
    try:
        with connection.cursor() as cursor:
            sql_insert = "INSERT INTO ai_suggestion_30102025 (school_id, username, score, suggestion) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql_insert, (school_id, Username, Score, Suggestion))
        connection.commit()
    finally:
        connection.close()



def insert_exam_records_info(Username, Question_bank, Question_id, Student_choice, Correct_answer, Start_time, End_time, Duration):
    connection = connect_to_db()
    school_id = "A"
    try:
        with connection.cursor() as cursor:
            sql_insert = "INSERT INTO exam_records_30102025 (school_id, username, question_bank, question_id, student_choice, correct_answer, start_time, end_time, duration) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql_insert, (school_id, Username, Question_bank, Question_id, Student_choice, Correct_answer, Start_time, End_time, Duration))
        connection.commit()
    finally:
        connection.close()

def insert_chatbot_use_info(Username, Question_bank, Question_id):
    connection = connect_to_db()
    school_id = "A"
    try:
        with connection.cursor() as cursor:
            sql_insert = "INSERT INTO chatbot_use_info_30102025 (school_id, username, question_bank, question_id) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql_insert, (school_id, Username, Question_bank, Question_id))
        connection.commit()
    finally:
        connection.close()

def insert_student_info(Username, Password, Class, Sex):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            sql_insert = "INSERT INTO student_info_25_6 (username, password, class, sex) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql_insert, (Username, Password, Class, Sex))
        connection.commit()
    finally:
        connection.close()

def check_login(Username, Password):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            # 先查学生表
            sql_query = "SELECT * FROM student_info_25_6 WHERE username = %s AND password = %s"
            cursor.execute(sql_query, (Username, Password))
            result = cursor.fetchone()
            if result:
                return "student"  # 明确返回用户类型

            # 再查教师表
            sql_query = "SELECT * FROM teacher_info_25_6 WHERE username = %s AND password = %s"
            print("Query username:", Username)
            print("Query password:", Password)
            cursor.execute(sql_query, (Username, Password))
            result = cursor.fetchone()
            print("SQL result:", result)
            if result:
                return "teacher"  # 明确返回用户类型

        # 都没找到返回 None
        return None
    finally:
        connection.close()

def get_teacher_classes(username):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            print("Query username:", username)
            sql = "SELECT class FROM teacher_info_25_6 WHERE username = %s"
            cursor.execute(sql, (username,))
            result = cursor.fetchone()
            print("SQL result:", result)
            if result and result[0]:
                # 以逗号分割并去除空格
                return [c.strip() for c in result[0].split(',') if c.strip()]
            else:
                return []
    finally:
        connection.close()

def get_teacher_question_ids(teacher_classes):
    if not teacher_classes:
        return []
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            # 兼容单个班级和多个班级
            if len(teacher_classes) == 1:
                sql_students = "SELECT username FROM student_info_25_6 WHERE class = %s"
                cursor.execute(sql_students, (teacher_classes[0],))
            else:
                format_strings = ','.join(['%s'] * len(teacher_classes))
                sql_students = f"SELECT username FROM student_info_25_6 WHERE class IN ({format_strings})"
                cursor.execute(sql_students, tuple(teacher_classes))
            students = [row[0] for row in cursor.fetchall()]
            if not students:
                return []
            # 兼容单个学生和多个学生
            if len(students) == 1:
                sql_questions = "SELECT DISTINCT question_id FROM student_choice_info WHERE username = %s"
                cursor.execute(sql_questions, (students[0],))
            else:
                format_strings2 = ','.join(['%s'] * len(students))
                sql_questions = f"SELECT DISTINCT question_id FROM student_choice_info WHERE username IN ({format_strings2})"
                cursor.execute(sql_questions, tuple(students))
            question_ids = [row[0] for row in cursor.fetchall()]
            return question_ids
    finally:
        connection.close()

def get_student_class(username):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT class FROM student_info_25_6 WHERE username=%s", (username,))
            stu_class_row = cursor.fetchone()
            return stu_class_row[0] if stu_class_row else None
    finally:
        connection.close()

def get_students_by_class(class_name):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT username FROM student_info_25_6 WHERE class=%s", (class_name,))
            return [row[0] for row in cursor.fetchall()]
    finally:
        connection.close()

def get_students_by_classes(class_list):
    if not class_list:
        return []
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            if len(class_list) == 1:
                cursor.execute("SELECT username FROM student_info_25_6 WHERE class=%s", (class_list[0],))
            else:
                format_strings = ','.join(['%s'] * len(class_list))
                cursor.execute(f"SELECT username FROM student_info_25_6 WHERE class IN ({format_strings})", tuple(class_list))
            return [row[0] for row in cursor.fetchall()]
    finally:
        connection.close()

def get_students_by_name(username):
    connection = connect_to_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM student_info_25_6 WHERE username = %s", (username,))
            result = cursor.fetchone()
            return result
    finally:
        connection.close()
