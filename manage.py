from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import tkinter as tk
import mysql.connector
import hashlib


def make_pw_hash(password):
    return str(hashlib.sha256(str.encode(password)).hexdigest())

class Manager_Window(tk.Tk):
    def __init__(self, username, *args, **kwargs):
        self.root = tk.Tk.__init__(self, *args, **kwargs)
        # Define Attributes
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.fullname = tk.StringVar()

        self.frame = tk.Frame(self)
        self.title('To-Do App')
        w = 720
        h = 480
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        self.geometry("%dx%d+%d+%d" % (w, h, x, y))
        # Frame
        self.frame.rowconfigure(0, weight=5)
        self.frame.rowconfigure(1, weight=5)
        self.frame.rowconfigure(2, weight=5)
        self.frame.rowconfigure(3, weight=5)
        self.frame.rowconfigure(4, weight=5)
        self.frame.rowconfigure(5, weight=1)

        self.frame.columnconfigure(0, weight=5)
        self.frame.columnconfigure(1, weight=5)
        self.frame.columnconfigure(2, weight=5)
        self.frame.columnconfigure(3, weight=5)

        # Init user table
        self.treev = ttk.Treeview(self.frame, selectmode='browse', columns=(1, 2, 3), show=['headings'])
        self.treev.grid(row=0, column=0, rowspan=5, columnspan=3, sticky="news", padx=3)
        self.scroll = tk.Scrollbar(self.treev, command=self.treev.yview)
        self.scroll.pack(side=RIGHT, fill=Y)
        self.treev.configure(yscrollcommand=self.scroll.set)

        self.treev_style = ttk.Style(self.treev)
        self.treev_style.layout('Treeview',
                                [('Treeview.field', {'sticky': 'nswe', 'border': '1', 'children': [
                                    ('Treeview.padding', {'sticky': 'nswe', 'children': [
                                        ('Treeview.treearea', {'sticky': 'nswe'})
                                    ]})
                                ]})
                                 ])
        self.treev_style.configure('Treeview', rowheight=40, font=(None, 10))
        self.treev_style.configure('Treeview.Heading', background='blue', font=('Arial Bold', 11))

        # ------------------ Defining task table heading -------------------------------------------
        self.treev.column("#1", width=100, anchor='w')
        self.treev.column("#2", width=100, anchor='w')
        self.treev.column("#3", width=100, anchor='w')

        self.treev.heading("#1", text="Username", command=lambda: self.sortby(self.treev, "#1", False))
        self.treev.heading("#2", text="Password")
        self.treev.heading("#3", text="Full Name", command=lambda: self.sortby(self.treev, "#3", False))

        # ------------------ Define Button ----------------------------------------------------------
        self.add_b = Button(self.frame, text='Add User', width=15, font=("Arial", 12), command=self.show_add_box)
        self.add_b.grid(row=5, column=0, columnspan=1, sticky='news', padx=2, pady=2)
        self.delete_b = Button(self.frame, text='Remove User', width=15, font=("Arial", 12), command=self.delete_user)
        self.delete_b.grid(row=5, column=1, columnspan=1, sticky='news', padx=2, pady=2)
        self.load_b = Button(self.frame, text='Update User', width=15, font=("Arial", 12), command=self.update_user)
        self.load_b.grid(row=5, column=2, columnspan=1, sticky='news', padx=2, pady=2)

        # ---------------------------- Load database -----------------------------------------------
        self.mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="chinh3458",
            database="mydatabase"
        )
        self.mycursor = self.mydb.cursor()

        # -------------------- Load users list from database to App ----------------------------------------
        self.load_treev()

        # -----------------------------------USER FRAME-----------------------------------------
        self.usersFrame = tk.Frame(self.frame, bg="lightblue")
        self.usersFrame.grid(row=0, column=3, rowspan=6, columnspan=1, sticky="news", padx=3)
        Label(self.usersFrame, text="User: " + username, width=15, font=("Arial Bold", 14)).pack(pady=50)
        self.task_b = Button(self.usersFrame, text='Task Manager',
                             width=15, font=("Courier", 14), command=self.task_manager)
        self.task_b.pack(anchor='center', pady=20)

        self.logout_b = Button(self.usersFrame, text='Log out', width=15, font=("Courier", 12), command=self.logout)
        self.logout_b.pack(side=BOTTOM, pady=20)
        self.frame.grid(row=0, column=0, sticky="news", padx=5, pady=5)
        self.rowconfigure(0, weight=15)
        self.columnconfigure(0, weight=11)

    # Load Data from database
    def load_treev(self):
        self.treev.delete(*self.treev.get_children())

        # -------------------- Load USER -----------------------------------------------------------------
        query = "SELECT * from users WHERE isAdmin = false "
        self.mycursor.execute(query)
        users = self.mycursor.fetchall()
        for i in users:
            self.treev.insert('', 'end', values=(i[1], '''$hashing''', i[4]))

    def add_user(self, username, password, fullname):
        if self.check_user(username):
            hash_password = make_pw_hash(password)
            query = "INSERT INTO users(username, password, isAdmin, fullname) VALUES(%s, %s, false, %s)"
            value = (username, hash_password, fullname)
            self.mycursor.execute(query, value)
            self.mydb.commit()
            self.load_treev()
        else:
            tk.messagebox.showwarning(title="Warning!", message="Existing User!")

    def delete_user(self):
        try:
            user_id = self.treev.focus()
            username = self.treev.item(user_id)['values'][0]
            query = "DELETE FROM users WHERE username = %s"
            self.mycursor.execute(query, (username,))
            self.mydb.commit()
            self.load_treev()
        except:
            tk.messagebox.showwarning(title="Warning!", message="You must select an user.")

    def update_user(self):
        try:
            index = self.treev.focus()
        except:
            tk.messagebox.showwarning(title="Warning!", message="You must select an user.")
        else:
            self.show_update_box(index)

    def update_treev(self, user_id, username, password, fullname):
        user_index = self.treev.focus()
        self.treev.delete(user_index)
        if self.check_user(username):
            query = "UPDATE users " \
                    "SET username = %s, password = %s, fullname = %s " \
                    "WHERE user_id = %s"
            hash_password = make_pw_hash(password)
            self.mycursor.execute(query, (username, hash_password, fullname, user_id))
            self.mydb.commit()
            self.load_treev()
        else:
            tk.messagebox.showwarning(title="Warning!", message="Existing User!")
        self.edit_user_screen.destroy()

    def show_add_box(self):
        self.new_user_screen = tk.Tk()
        self.new_user_screen.title("New User")
        w = 250
        h = 250
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        self.new_user_screen.geometry("%dx%d+%d+%d" % (w, h, x, y))
        Label(self.new_user_screen, text="").pack()

        Label(self.new_user_screen, text="Username * ").pack()
        username_entry = Entry(self.new_user_screen, textvariable=self.username, width=30)
        username_entry.pack()
        Label(self.new_user_screen, text="").pack()

        Label(self.new_user_screen, text="Password * ").pack()
        password_entry = Entry(self.new_user_screen, textvariable=self.password, width=30)
        password_entry.pack()
        Label(self.new_user_screen, text="").pack()

        Label(self.edit_user_screen, text="Full Name * ").pack()
        fullname_entry = Entry(self.edit_user_screen, textvariable=self.password, width=30)
        fullname_entry.pack()
        Label(self.edit_user_screen, text="").pack()

        Button(self.new_user_screen, text="Add", width=10, height=1,
               command=lambda: self.add_user(username_entry.get(), password_entry.get(), fullname_entry.get())).pack()
        self.new_user_screen.mainloop()

    def show_update_box(self, index):
        self.edit_user_screen = tk.Tk()
        self.edit_user_screen.title("Update User")
        w = 250
        h = 250
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        self.edit_user_screen.geometry("%dx%d+%d+%d" % (w, h, x, y))

        Label(self.edit_user_screen, text="").pack()
        Label(self.edit_user_screen, text="User * ").pack()
        username_entry = Entry(self.edit_user_screen, textvariable=self.username, width=30)
        username_entry.insert(0, self.treev.item(index)['values'][0])
        username_entry.pack()
        Label(self.edit_user_screen, text="").pack()

        Label(self.edit_user_screen, text="Password * ").pack()
        password_entry = Entry(self.edit_user_screen, textvariable=self.password, width=30)
        password_entry.insert(0, self.treev.item(index)['values'][1])
        password_entry.pack()
        Label(self.edit_user_screen, text="").pack()

        Label(self.edit_user_screen, text="Full Name * ").pack()
        fullname_entry = Entry(self.edit_user_screen, textvariable=self.fullname, width=30)
        fullname_entry.insert(0, self.treev.item(index)['values'][2])
        fullname_entry.pack()
        Label(self.edit_user_screen, text="").pack()

        query = "SELECT user_id from users WHERE username = %s"
        username = self.treev.item(index)['values'][0]
        self.mycursor.execute(query, (username,))
        user_id = self.mycursor.fetchall()[0][0]

        Button(self.edit_user_screen, text="Update", width=10, height=1,
               command=lambda: self.update_treev(user_id, username_entry.get(), password_entry.get(), fullname_entry.get())).pack()
        self.edit_user_screen.mainloop()

    def check_user(self, username):
        for x in self.treev.get_children():
            if self.treev.item(x)["values"][0] == username:
                return False
        return True

    def logout(self):
        self.destroy()
        from login import Login_Window
        f = Login_Window()
        f.mainloop()

    def sortby(self, treev, col, descending):
        """sort tree contents when a column header is clicked on"""
        # grab values to sort
        data = [(treev.set(child, col), child) for child in treev.get_children('')]
        data.sort(reverse=descending)
        for ix, item in enumerate(data):
            treev.move(item[1], '', ix)
        # switch the heading to sort in the opposite direction
        treev.heading(col, command=lambda: self.sortby(treev, col, int(not descending)))

    def task_manager(self):
        self.destroy()
        from main import ToDo_App
        f1 = ToDo_App("admin")
        f1.mainloop()
