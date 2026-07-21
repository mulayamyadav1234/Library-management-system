import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="mulayam@123",
        database="library_management_system"
    )
