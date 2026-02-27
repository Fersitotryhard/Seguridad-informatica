import mysql.connector

def get_connection():
    '''return mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin",
        database="gatodb"
    )'''
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin",
        database="gatodb"
    )