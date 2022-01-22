import hashlib
import mysql.connector


def make_pw_hash(password):
    return str(hashlib.sha256(str.encode(password)).hexdigest())


try:
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="chinh3458",
        database="mydatabase"
    )
    c = mydb.cursor()
except:
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="chinh3458"
    )
    c = mydb.cursor()
    c.execute("CREATE DATABASE mydatabase")

try:
    c.execute('''CREATE TABLE users (user_id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255), 
        password VARCHAR(255), isAdmin BOOLEAN, fullname NVARCHAR(255))''')
    # Insert admin account
    query = "INSERT INTO users (username, password, isAdmin, fullname) VALUES (%s, %s, true, %s)"
    username = "admin"
    password = "admin123"
    password = make_pw_hash(password)
    c.execute(query, (username, password, username))
except:
    print("Table already created")

mydb.commit()
mydb.close()
