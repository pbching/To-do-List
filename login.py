import hashlib
import tkinter as tk
from tkinter import *
from tkinter import messagebox
import mysql.connector


with open('config.txt', 'r') as file:
    data = file.readlines()
    db_user = data[0].split('=')[1]
    db_pw = data[1].split('=')[1]


def make_pw_hash(password):
    return str(hashlib.sha256(str.encode(password)).hexdigest())


# authenticates user according to information from database
def check_pw_hash(password, user):
    if make_pw_hash(password) == user[2]:
        return True
    return False


class Login_Window(tk.Tk):
    def __init__(self, *args, **kwargs):
        self.root = tk.Tk.__init__(self, *args, **kwargs)
        self.title("Login")
        # ---------------------------- Load database ---------------------------------------
        try:
            self.mydb = mysql.connector.connect(
                host="localhost",
                user=db_user,
                password=db_pw,
                database="mydatabase"
            )
            self.mycursor = self.mydb.cursor()
        except:
            self.mydb = mysql.connector.connect(
                host="localhost",
                user=db_user,
                password=db_pw
            )
            self.mycursor = self.mydb.cursor()
            self.mycursor.execute("CREATE DATABASE mydatabase")
        w = 300
        h = 270
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.geometry("%dx%d+%d+%d" % (w, h, x, y))
        Label(self, text="Please enter credentials below to login").pack()
        Label(self, text="").pack()

        username_verify = StringVar()
        password_verify = StringVar()

        Label(self, text="Username * ").pack(pady=10)
        username_login_entry = Entry(self, textvariable=username_verify, width=25)
        username_login_entry.pack()
        Label(self, text="").pack()
        Label(self, text="Password * ").pack(pady=10)
        password__login_entry = Entry(self, textvariable=password_verify, width=25, show='*')
        password__login_entry.pack()
        Label(self, text="").pack()

        Button(self, text="Login", width=10, height=1,
               command=lambda: self.login_verification(username_verify.get(), password_verify.get(), w, h)).pack()

    def login_verification(self, username, input_pwd, w, h):
        self.mycursor.execute("SELECT * FROM users WHERE username='{}'".format(username))
        arr = self.mycursor.fetchall()

        if len(arr) > 0:
            if check_pw_hash(input_pwd, arr[0]):
                self.destroy()
                from main import ToDo_App
                f1 = ToDo_App(username)
                f1.mainloop()
            else:
                messagebox.showerror("Failed login", "Incorrect Password")
        else:
            messagebox.showerror("Failed login", "User doesn't exist")
