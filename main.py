from tkinter import *
from tkinter import ttk
from tkinter import messagebox, simpledialog
import tkinter as tk
import mysql.connector
import os
from datetime import datetime
from PIL import ImageTk, Image

class ToDo_App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.frame = tk.LabelFrame(self, text="To-do Task Manager")
        self.title('To-Do App')
        self.minsize(850, 400)
        # Frame
        self.frame.rowconfigure(0, weight=5)
        self.frame.rowconfigure(1, weight=5)
        self.frame.rowconfigure(2, weight=5)
        self.frame.rowconfigure(3, weight=5)
        self.frame.rowconfigure(4, weight=5)
        self.frame.rowconfigure(5, weight=3)

        self.frame.columnconfigure(0, weight=5) 
        self.frame.columnconfigure(1, weight=5)
        self.frame.columnconfigure(2, weight=5)
        self.frame.columnconfigure(3, weight=5)
        self.frame.columnconfigure(4, weight=5)
        # Define Attributes
        self.task = tk.StringVar()
        self.start_t = tk.StringVar()
        self.end_t = tk.StringVar()
        self.place = tk.StringVar()
        # Init task table
        self.treev_tasks = ttk.Treeview(self.frame, selectmode='browse', columns=(1, 2, 3, 4))
        self.treev_tasks.grid(row=0, column=0, rowspan=5, columnspan=4, sticky="news", padx=3)

        # Defining Check Done Task
        self.style = ttk.Style(self.treev_tasks)
        self.style.configure('Treeview', rowheight=30)
        im1 = Image.open(r'.\img\checkbox.jpg')
        img1 = im1.resize((16, 16))
        self.im_checked = ImageTk.PhotoImage(img1)
        im2 = Image.open(r'.\img\uncheck.jpg')
        img2 = im2.resize((16, 16))
        self.im_unchecked = ImageTk.PhotoImage(img2)
        self.treev_tasks.tag_configure('done', image=self.im_checked)
        self.treev_tasks.tag_configure('undone', image=self.im_unchecked)

        self.treev_tasks.bind('<Button 1>', self.changeStatus)

        # Defining heading
        self.treev_tasks.column("#0", width=1)
        self.treev_tasks.column("#1", width=120, anchor='w')
        self.treev_tasks.column("#2", width=40, anchor='w')
        self.treev_tasks.column("#3", width=40, anchor='w')
        self.treev_tasks.column("#4", width=20, anchor='c')

        self.treev_tasks.heading("#0", text="Status")
        self.treev_tasks.heading("#1", text="Task")
        self.treev_tasks.heading("#2", text="Start Time")
        self.treev_tasks.heading("#3", text="End Time")
        self.treev_tasks.heading("#4", text="Place")

        # Define Button
        self.add_button = tk.Button(self.frame, text='Add Task', width=15, command=self.show_add_box)
        self.add_button.grid(row=5, column=0, columnspan=1, sticky='news', padx=2, pady=2)
        self.delete_button = tk.Button(self.frame, text='Remove Task', width=15, command=self.delete_task)
        self.delete_button.grid(row=5, column=1, columnspan=1, sticky='news', padx=2, pady=2)
        self.load_button = tk.Button(self.frame, text='Update Task', width=15, command=self.update_task)
        self.load_button.grid(row=5, column=2, columnspan=1, sticky='news', padx=2, pady=2)
        self.save_button = tk.Button(self.frame, text='Log out', width=15, command=self.logout)
        self.save_button.grid(row=5, column=3, columnspan=1, sticky='news', padx=2, pady=2)

        # Load database
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

        self.userFrame = ttk.Frame(self.frame)
        self.userFrame.grid(row=1, column=4, rowspan=2, columnspan=1, sticky="news", padx=3)
        Label(self.userFrame, text="User: Chinh Pham", font=("Courier", 14)).pack()

        self.frame.grid(row=0, column=0, sticky="news", padx=5, pady=5)
        self.rowconfigure(0, weight=15)
        self.columnconfigure(0, weight=11)

        try:
            self.load_data()
        except:
            query = "CREATE TABLE task_list" + "(task_id INT AUTO_INCREMENT PRIMARY KEY, user VARCHAR(255), task NVARCHAR(255), start_time DATETIME, " \
                                                    "end_time DATETIME, place NVARCHAR(255), status BOOLEAN)"
            self.mycursor.execute(query)
            self.load_data()

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
        query = "SELECT task, start_time, end_time, place, status from task_list"
        self.mycursor.execute(query)
        rows = self.mycursor.fetchall()
        self.load_treev_task(rows)

    def add_task(self, task, start_time, end_time, location):
        try:
            start_t = datetime.strptime(start_time, '%d-%m-%Y %H:%M')
            end_t = datetime.strptime(end_time, '%d-%m-%Y %H:%M')
        except:
            messagebox.showwarning(title="Warning!", message="Invalid datetime or Wrong datetime format "
                                                             "(must be dd-mm-YYYY HH:MM!)")
        else:
            if self.check_time(start_t, end_t):
                if self.check_task(task):
                    # self.treev_tasks.insert("", 'end', values=(task, start_time, end_time, location), tags='undone')
                    query = "INSERT INTO task_list(user, task, start_time, end_time, place, status) " \
                                                           "VALUES(%s, %s, %s, %s, %s, false)"
                    self.mycursor.execute(query, ("chinhpham", task, start_t, end_t, location))
                    self.mydb.commit()
                    self.load_data()
                else:
                    tk.messagebox.showwarning(title="Warning!", message="Existing Task!")
            else:
                tk.messagebox.showwarning(title="Warning!", message="Time conflict!")
        # finally:
        #     self.new_task_screen.destroy()

    def delete_task(self):
        try:
            task_index = self.treev_tasks.focus()
            user = "chinhpham"
            task = self.treev_tasks.item(task_index)['values'][0]
            query = "DELETE FROM task_list WHERE user = %s AND task = %s"
            value = (user, task)
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
                                                             "(must be dd-mm-YYYY HH:MM!)")
        else:
            task_index = self.treev_tasks.focus()
            self.treev_tasks.delete(task_index)
            user = "chinhpham"
            if self.check_time(start_t, end_t):
                if self.check_task(task):
                    query = "UPDATE task_list SET task = %s, start_time = %s, end_time = %s, place = %s, status = false WHERE user = %s AND task_id= %s"
                    self.mycursor.execute(query, (task, start_t, end_t, location, user, index))
                    self.mydb.commit()
                    self.load_data()
                else:
                    tk.messagebox.showwarning(title="Warning!", message="Existing Task!")
            else:
                tk.messagebox.showwarning(title="Warning!", message="Time conflict!")
        finally:
            self.task_screen.destroy()

    def show_add_box(self):
        self.new_task_screen = tk.Tk()
        self.new_task_screen.title("New Task")
        self.new_task_screen.geometry("250x350")
        Label(self.new_task_screen, text="").pack()
        Label(self.new_task_screen, text="Task * ").pack()
        task_entry = Entry(self.new_task_screen, textvariable=self.task)
        task_entry.pack()
        Label(self.new_task_screen, text="").pack()
        Label(self.new_task_screen, text="Start Time* ").pack()
        t_start_entry = Entry(self.new_task_screen, textvariable=self.start_t)
        t_start_entry.pack()
        Label(self.new_task_screen, text="").pack()
        Label(self.new_task_screen, text="End Time * ").pack()
        t_end_entry = Entry(self.new_task_screen, textvariable=self.end_t)
        t_end_entry.pack()
        Label(self.new_task_screen, text="").pack()
        Label(self.new_task_screen, text="Place * ").pack()
        place_entry = Entry(self.new_task_screen, textvariable=self.place)
        place_entry.pack()
        Label(self.new_task_screen, text="").pack()

        Button(self.new_task_screen, text="Add", width=10, height=1,
               command=lambda: self.add_task(task_entry.get(), t_start_entry.get(), t_end_entry.get(), place_entry.get())).pack()
        self.new_task_screen.mainloop()

    def show_update_box(self, task_index):
        self.task_screen = tk.Tk()
        self.task_screen.title("Update Task")
        self.task_screen.geometry("300x350")
        Label(self.task_screen, text="").pack()
        Label(self.task_screen, text="Task * ").pack()
        task_entry = Entry(self.task_screen, textvariable=self.task)
        task_entry.insert(0, self.treev_tasks.item(task_index)['values'][0])
        task_entry.pack()
        Label(self.task_screen, text="").pack()
        Label(self.task_screen, text="Start Time* ").pack()
        t_start_entry = Entry(self.task_screen, textvariable=self.start_t)
        t_start_entry.insert(0, self.treev_tasks.item(task_index)['values'][1])
        t_start_entry.pack()
        Label(self.task_screen, text="").pack()
        Label(self.task_screen, text="End Time * ").pack()
        t_end_entry = Entry(self.task_screen, textvariable=self.end_t)
        t_end_entry.insert(0, self.treev_tasks.item(task_index)['values'][2])
        t_end_entry.pack()
        Label(self.task_screen, text="").pack()
        Label(self.task_screen, text="Place * ").pack()
        place_entry = Entry(self.task_screen, textvariable=self.place)
        place_entry.insert(0, self.treev_tasks.item(task_index)['values'][3])
        place_entry.pack()
        Label(self.task_screen, text="").pack()

        user = "chinhpham"
        task = self.treev_tasks.item(task_index)['values'][0]
        query = "SELECT task_id from task_list WHERE user = %s AND task = %s"
        value = (user, task)
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
            if old_start <= start_t < old_end:
                return False
            elif old_start < end_t <= old_end:
                return False
            elif start_t <= old_start <= end_t:
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
            user = "chinhpham"
            if tag == "done":
                query = "UPDATE task_list SET status = false WHERE user = %s AND task = %s"
                value = (user, task)
                self.mycursor.execute(query, value)
                self.mydb.commit()
                self.load_data()
            else:
                query = "UPDATE task_list SET status = true WHERE user = %s AND task = %s"
                value = (user, task)
                self.mycursor.execute(query, value)
                self.mydb.commit()
                self.load_data()
        except:
            pass

    def logout(self):
        pass

def __main__():
    if __name__ == "__main__":
        f = ToDo_App()
        f.mainloop()

__main__()