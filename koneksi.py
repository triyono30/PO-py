import mysql.connector

def koneksi():
    return mysql.connector.connect(
        host="localhost",port="3301",
        user="root",
        password="password",
        database="po_db"
    )
