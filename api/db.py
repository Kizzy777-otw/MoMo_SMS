import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",   #  empty for XAMPP
        database="momo_sms_db"
    )