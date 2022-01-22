from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import tkinter as tk
import mysql.connector
from datetime import date, datetime
from PIL import ImageTk, Image
from tkcalendar import Calendar


class ToDo_App(tk.Tk):
    def __init__(self, username, *args, **kwargs):
        self.root = tk.Tk.__init__(self, *args, **kwargs)
        # Define Attributes
        self.task = tk.StringVar()
        self.start_t = tk.StringVar()
        self.end_t = tk.StringVar()
        self.place = tk.StringVar()

        self.frame = tk.Frame(self)
        self.title('To-Do App')
        w = 1080
        h = 720
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

        self.frame.columnconfigure(0, weight=8)
        self.frame.columnconfigure(1, weight=8)
        self.frame.columnconfigure(2, weight=8)
        self.frame.columnconfigure(3, weight=3)

        # Init task table
        self.treev_tasks = ttk.Treeview(self.frame, selectmode='browse', columns=(1, 2, 3, 4))
        self.treev_tasks.grid(row=0, column=0, rowspan=5, columnspan=3, sticky="news", padx=3)
        self.scroll = tk.Scrollbar(self.treev_tasks, command=self.treev_tasks.yview)
        self.scroll.pack(side=RIGHT, fill=Y)
        self.treev_tasks.configure(yscrollcommand=self.scroll.set)

        self.treev_style = ttk.Style(self.treev_tasks)
        self.treev_style.layout('Treeview',
                                [('Treeview.field', {'sticky': 'nswe', 'border': '1', 'children': [
                                    ('Treeview.padding', {'sticky': 'nswe', 'children': [
                                        ('Treeview.treearea', {'sticky': 'nswe'})
                                    ]})
                                ]})
                                 ])
        self.treev_style.configure('Treeview', rowheight=40, font=(None, 10))
        self.treev_style.configure('Treeview.Heading', background='blue', font=('Arial Bold', 11))

        # ----------------- Define Check Done Task --------------------------------------------
        im1 = Image.open(r'.\img\checkbox.jpg')
        img1 = im1.resize((16, 16))
        self.im_checked = ImageTk.PhotoImage(img1)
        im2 = Image.open(r'.\img\uncheck.jpg')
        img2 = im2.resize((16, 16))
        self.im_unchecked = ImageTk.PhotoImage(img2)

        self.treev_tasks.tag_configure('done', image=self.im_checked)
        self.treev_tasks.tag_configure('undone', image=self.im_unchecked)

        self.treev_tasks.bind('<Double-1>', self.changeStatus)

        # ------------------ Defining task table heading -------------------------------------------
        self.treev_tasks.column("#0", width=1)
        self.treev_tasks.column("#1", width=120, anchor='w')
        self.treev_tasks.column("#2", width=40, anchor='w')
        self.treev_tasks.column("#3", width=40, anchor='w')
        self.treev_tasks.column("#4", width=20, anchor='c')

        self.treev_tasks.heading("#0", text="Status")
        self.treev_tasks.heading("#1", text="Task", command=lambda: self.sort_treev(self.treev_tasks, "#1", False))
        self.treev_tasks.heading("#2", text="Start Time",
                                 command=lambda: self.sort_treev(self.treev_tasks, "#2", False))
        self.treev_tasks.heading("#3", text="End Time")
        self.treev_tasks.heading("#4", text="Place")

        # ------------------ Define Button ----------------------------------------------------------
        self.add_b = Button(self.frame, text='Add Task', width=15, font=("Arial", 12), command=self.show_add_box)
        self.add_b.grid(row=5, column=0, columnspan=1, sticky='news', padx=2, pady=2)
        self.delete_b = Button(self.frame, text='Remove Task', width=15, font=("Arial", 12), command=self.delete_task)
        self.delete_b.grid(row=5, column=1, columnspan=1, sticky='news', padx=2, pady=2)
        self.load_b = Button(self.frame, text='Update Task', width=15, font=("Arial", 12), command=self.update_task)
        self.load_b.grid(row=5, column=2, columnspan=1, sticky='news', padx=2, pady=2)

        # ---------------------------- Load database -----------------------------------------------
        try:
            self.mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="chinh3458",
                database="mydatabase"
            )
            self.mycursor = self.mydb.cursor()
        except:
            self.mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="chinh3458"
            )
            self.mycursor = self.mydb.cursor()
            self.mycursor.execute("CREATE DATABASE mydatabase")

        # -------------------- Load USER -----------------------------------------------------------------
        query = "SELECT * from users WHERE username = %s"
        self.mycursor.execute(query, (username,))
        self.user = self.mycursor.fetchone()
        print(self.user)

        # -------------------- Load task list from database to App ----------------------------------------
        try:
            self.load_data()
        except:
            query = "CREATE TABLE task_list" + "(task_id INT not null AUTO_INCREMENT PRIMARY KEY, " \
                                               "user_id INT not null, " \
                                               "task NVARCHAR(255), " \
                                               "start_time DATETIME, " \
                                               "end_time DATETIME, " \
                                               "place NVARCHAR(255), " \
                                               "status BOOLEAN, " \
                                               "FOREIGN key (user_id) REFERENCES users(user_id))"
            self.mycursor.execute(query)
            self.load_data()

        # -----------------------------------USER FRAME-----------------------------------------
        self.userFrame = tk.Frame(self.frame, bg="lightblue")
        self.userFrame.grid(row=0, column=3, rowspan=6, columnspan=1, sticky="news", padx=3)
        Label(self.userFrame, text="WELCOME!!!", width=15, font=("Arial Bold", 14)).pack(ipady=3, pady=20)
        Label(self.userFrame, text="User: " + self.user[4], wraplength=500, justify="center",
              font=("Arial Bold", 14)).pack(ipadx=5, ipady=3, pady=10)
        if self.user[3] == 1:
            self.manage_b = Button(self.userFrame, text='Account Manager',
                                   width=15, font=("Courier", 14), command=self.manage_acc)
            self.manage_b.pack(anchor='center', pady=20)

        # ----------------------------------- Calendar ------------------------------------------
        today = date.today()
        self.cal = Calendar(self.userFrame, font="Arial 9", selectmode='day',
                            year=today.year, month=today.month, day=today.day)
        self.cal.pack(fill="both", pady=20)
        Button(self.userFrame, text='Filter', font=("Courier", 12), width=10,
               command=self.filter_date).place(x=15, y=450)
        Button(self.userFrame, text='Unfilter', font=("Courier", 12), width=10,
               command=self.load_data).place(x=165, y=450)

        self.logout_b = Button(self.userFrame, text='Log out', width=15, font=("Courier", 12), command=self.logout)
        self.logout_b.pack(side=BOTTOM, pady=20)

        # ----------------------------------- GRID MAINFRAME --------------------------------------
        self.frame.grid(row=0, column=0, sticky="news", padx=5, pady=5)
        self.rowconfigure(0, weight=15)
        self.columnconfigure(0, weight=11)

    def filter_date(self):
        date = self.cal.selection_get()
        print(date)
        query = "SELECT task, start_time, end_time, place, status from task_list " \
                "WHERE user_id = %s AND DATE(start_time) = %s"
        user_id = self.user[0]
        self.mycursor.execute(query, (user_id, date))
        rows = self.mycursor.fetchall()
        self.load_treev_task(rows)

    # Load Data from database
    def load_treev_task(self, rows):
        self.treev_tasks.delete(*self.treev_tasks.get_children())
        for i in rows:
            start_t = datetime.strftime(i[1], '%d-%m-%Y %H:%M')
            end_t = datetime.strftime(i[2], '%d-%m-%Y %H:%M')
            if i[4] == 0:
                tag = 'undone'
            else:
                tag = 'done'
            self.treev_tasks.insert('', 'end', values=(i[0], start_t, end_t, i[3]), tags=tag)

    def load_data(self):
        query = "SELECT task, start_time, end_time, place, status from task_list WHERE user_id = %s"
        user_id = self.user[0]
        self.mycursor.execute(query, (user_id,))
        rows = self.mycursor.fetchall()
        self.load_treev_task(rows)

    def add_task(self, task, start_time, end_time, location):
        try:
            start_t = datetime.strptime(start_time, '%d-%m-%Y %H:%M')
            end_t = datetime.strptime(end_time, '%d-%m-%Y %H:%M')
        except:
            messagebox.showwarning(title="Warning!", message="Invalid datetime or Wrong datetime format "
                                                             "(must be dd-mm-YYYY HH:MM)")
        else:
            if self.check_time(start_t, end_t):
                if self.check_task(task):
                    query = "INSERT INTO task_list(user_id, task, start_time, end_time, place, status) " \
                            "VALUES(%s, %s, %s, %s, %s, false)"
                    user_id = self.user[0]
                    value = (user_id, task, start_t, end_t, location)
                    self.mycursor.execute(query, value)
                    self.mydb.commit()
                    self.load_data()
                else:
                    tk.messagebox.showwarning(title="Warning!", message="Existing Task!")
            else:
                tk.messagebox.showwarning(title="Warning!", message="Time conflict!")

    def delete_task(self):
        try:
            task_index = self.treev_tasks.focus()
            user_id = self.user[0]
            task = self.treev_tasks.item(task_index)['values'][0]
            query = "DELETE FROM task_list WHERE user_id = %s AND task = %s"
            value = (user_id, task)
            self.mycursor.execute(query, value)
            self.mydb.commit()
            self.load_data()
        except:
            tk.messagebox.showwarning(title="Warning!", message="You must select a task.")

    def update_task(self):
        try:
            task_index = self.treev_tasks.focus()
        except:
            tk.messagebox.showwarning(title="Warning!", message="You must select a task.")
        else:
            self.show_update_box(task_index)

    def update_treev(self, index, task, start_time, end_time, location):
        try:
            start_t = datetime.strptime(start_time, '%d-%m-%Y %H:%M')
            end_t = datetime.strptime(end_time, '%d-%m-%Y %H:%M')
        except:
            tk.messagebox.showwarning(title="Warning!", message="Invalid datetime or Wrong datetime format "
                                                                "(must be dd-mm-YYYY HH:MM)")
        else:
            task_index = self.treev_tasks.focus()
            self.treev_tasks.delete(task_index)
            if self.check_time(start_t, end_t):
                if self.check_task(task):
                    query = "UPDATE task_list " \
                            "SET task = %s, start_time = %s, end_time = %s, place = %s, status = false " \
                            "WHERE user_id = %s AND task_id= %s"
                    user_id = self.user[0]
                    self.mycursor.execute(query, (task, start_t, end_t, location, user_id, index))
                    self.mydb.commit()
                else:
                    tk.messagebox.showwarning(title="Warning!", message="Existing Task!")
            else:
                tk.messagebox.showwarning(title="Warning!", message="Time conflict!")
        finally:
            self.load_data()
            self.task_screen.destroy()

    def show_add_box(self):
        self.new_task_screen = tk.Tk()
        self.new_task_screen.title("New Task")
        w = 300
        h = 350
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        self.new_task_screen.geometry("%dx%d+%d+%d" % (w, h, x, y))
        Label(self.new_task_screen, text="").pack()
        Label(self.new_task_screen, text="Task * ").pack()
        task_entry = Entry(self.new_task_screen, textvariable=self.task, width=30)
        task_entry.pack()
        Label(self.new_task_screen, text="").pack()
        Label(self.new_task_screen, text="Start Time * ").pack()
        t_start_entry = Entry(self.new_task_screen, textvariable=self.start_t, width=30)
        t_start_entry.pack()
        Label(self.new_task_screen, text="").pack()
        Label(self.new_task_screen, text="End Time * ").pack()
        t_end_entry = Entry(self.new_task_screen, textvariable=self.end_t, width=30)
        t_end_entry.pack()
        Label(self.new_task_screen, text="").pack()
        Label(self.new_task_screen, text="Place * ").pack()
        place_entry = Entry(self.new_task_screen, textvariable=self.place, width=30)
        place_entry.pack()
        Label(self.new_task_screen, text="").pack()

        Button(self.new_task_screen, text="Add", width=10, height=1,
               command=lambda: self.add_task(task_entry.get(), t_start_entry.get(), t_end_entry.get(),
                                             place_entry.get())).pack()
        self.new_task_screen.mainloop()

    def show_update_box(self, task_index):
        self.task_screen = tk.Tk()
        self.task_screen.title("Update Task")
        w = 300
        h = 350
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        self.task_screen.geometry("%dx%d+%d+%d" % (w, h, x, y))
        Label(self.task_screen, text="").pack()
        Label(self.task_screen, text="Task * ").pack()
        task_entry = Entry(self.task_screen, textvariable=self.task, width=30)
        task_entry.insert(0, self.treev_tasks.item(task_index)['values'][0])
        task_entry.pack()
        Label(self.task_screen, text="").pack()
        Label(self.task_screen, text="Start Time * ").pack()
        t_start_entry = Entry(self.task_screen, textvariable=self.start_t, width=30)
        t_start_entry.insert(0, self.treev_tasks.item(task_index)['values'][1])
        t_start_entry.pack()
        Label(self.task_screen, text="").pack()
        Label(self.task_screen, text="End Time * ").pack()
        t_end_entry = Entry(self.task_screen, textvariable=self.end_t, width=30)
        t_end_entry.insert(0, self.treev_tasks.item(task_index)['values'][2])
        t_end_entry.pack()
        Label(self.task_screen, text="").pack()
        Label(self.task_screen, text="Place * ").pack()
        place_entry = Entry(self.task_screen, textvariable=self.place, width=30)
        place_entry.insert(0, self.treev_tasks.item(task_index)['values'][3])
        place_entry.pack()
        Label(self.task_screen, text="").pack()

        query = "SELECT task_id from task_list WHERE user_id = %s AND task = %s"
        user_id = self.user[0]
        task = self.treev_tasks.item(task_index)['values'][0]
        value = (user_id, task)
        self.mycursor.execute(query, value)
        task_id = self.mycursor.fetchall()[0][0]

        Button(self.task_screen, text="Update", width=10, height=1,
               command=lambda: self.update_treev(task_id, task_entry.get(), t_start_entry.get(),
                                                 t_end_entry.get(), place_entry.get())).pack()
        self.task_screen.mainloop()

    def check_time(self, start_t, end_t):
        if start_t > end_t:
            return False
        for x in self.treev_tasks.get_children():
            old_start = datetime.strptime(self.treev_tasks.item(x)["values"][1], '%d-%m-%Y %H:%M')
            old_end = datetime.strptime(self.treev_tasks.item(x)["values"][2], '%d-%m-%Y %H:%M')
            if old_start < start_t < old_end:
                return False
            elif old_start < end_t < old_end:
                return False
            elif start_t < old_start < end_t:
                return False
        return True

    def check_task(self, task):
        for x in self.treev_tasks.get_children():
            if self.treev_tasks.item(x)["values"][0] == task:
                return False
        return True

    def changeStatus(self, event):
        try:
            rowid = self.treev_tasks.identify_row(event.y)
            tag = self.treev_tasks.item(rowid, "tag")[0]
            task = self.treev_tasks.item(rowid)['values'][0]
            user_id = self.user[0]
            if tag == "done":
                query = "UPDATE task_list SET status = false WHERE user_id = %s AND task = %s"
                value = (user_id, task)
                self.mycursor.execute(query, value)
                self.mydb.commit()
                self.load_data()
            else:
                query = "UPDATE task_list SET status = true WHERE user_id = %s AND task = %s"
                value = (user_id, task)
                self.mycursor.execute(query, value)
                self.mydb.commit()
                self.load_data()
        except:
            tk.messagebox.showwarning(title="Warning!", message="You must select a task.")

    def logout(self):
        self.destroy()
        from login import Login_Window
        f = Login_Window()
        f.mainloop()

    def sort_treev(self, treev, col, desc):
        """sort tree contents when a column header is clicked on"""
        # grab values to sort
        data = [(treev.set(child, col), child) for child in treev.get_children('')]
        if col == '#2':
            data.sort(reverse=desc, key=lambda t: datetime.strptime(t[0], "%d-%m-%Y %H:%M"))
        else:
            data.sort(reverse=desc)
        for ix, item in enumerate(data):
            treev.move(item[1], '', ix)
        # switch the heading to sort in the opposite direction
        treev.heading(col, command=lambda: self.sort_treev(treev, col, int(not desc)))

    def manage_acc(self):
        self.destroy()
        from manage import Manager_Window
        f = Manager_Window("admin")
        f.mainloop()
