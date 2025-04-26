# hamlog_core.py
# Code writing by ChatGPT (26-Apr-25).
# Inital version window layout with basic log display with add/modify/delete.

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# ==========================================================
# Database Manager
# ==========================================================

class DatabaseManager:
    def __init__(self, db_name="hamlog.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                callsign TEXT NOT NULL,
                frequency TEXT,
                mode TEXT,
                date TEXT,
                time TEXT
            )
        ''')
        self.conn.commit()

    def add_entry(self, callsign, frequency, mode, date, time):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO logs (callsign, frequency, mode, date, time)
            VALUES (?, ?, ?, ?, ?)
        ''', (callsign, frequency, mode, date, time))
        self.conn.commit()

    def update_entry(self, entry_id, callsign, frequency, mode, date, time):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE logs
            SET callsign=?, frequency=?, mode=?, date=?, time=?
            WHERE id=?
        ''', (callsign, frequency, mode, date, time, entry_id))
        self.conn.commit()

    def delete_entry(self, entry_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM logs WHERE id=?', (entry_id,))
        self.conn.commit()

    def fetch_entries(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM logs ORDER BY id DESC')
        return cursor.fetchall()

# ==========================================================
# GUI Application
# ==========================================================

class HamLogApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HamLog-Core")
        self.geometry("900x500")

        self.db = DatabaseManager()
        self.selected_entry_id = None

        self.create_main_frames()
        self.create_upper_frames()
        self.create_input_fields()
        self.create_log_list()
        self.populate_log_list()

    def create_main_frames(self):
        self.top_frame = tk.Frame(self)
        self.bottom_frame = tk.Frame(self)

        self.top_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def create_upper_frames(self):
        # Upper frame split into left and right
        self.upper_left_frame = tk.Frame(self.top_frame, width=450, height=200, bg="lightgrey")
        self.upper_right_frame = tk.Frame(self.top_frame, width=450, height=200)

        self.upper_left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.upper_right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.upper_left_frame.pack_propagate(False)
        self.upper_right_frame.pack_propagate(False)

    def create_input_fields(self):
        input_frame = tk.Frame(self.upper_right_frame)
        input_frame.pack(side=tk.TOP, anchor="ne", padx=10, pady=10)

        tk.Label(input_frame, text="Callsign").grid(row=0, column=0, sticky="e")
        tk.Label(input_frame, text="Frequency").grid(row=1, column=0, sticky="e")
        tk.Label(input_frame, text="Mode").grid(row=2, column=0, sticky="e")
        tk.Label(input_frame, text="Date").grid(row=3, column=0, sticky="e")
        tk.Label(input_frame, text="Time").grid(row=4, column=0, sticky="e")

        self.callsign_entry = tk.Entry(input_frame)
        self.frequency_entry = tk.Entry(input_frame)
        self.mode_entry = tk.Entry(input_frame)
        self.date_entry = tk.Entry(input_frame)
        self.time_entry = tk.Entry(input_frame)

        self.callsign_entry.grid(row=0, column=1)
        self.frequency_entry.grid(row=1, column=1)
        self.mode_entry.grid(row=2, column=1)
        self.date_entry.grid(row=3, column=1)
        self.time_entry.grid(row=4, column=1)

        # Buttons
        button_frame = tk.Frame(input_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        add_btn = tk.Button(button_frame, text="Add", width=10, command=self.add_entry)
        modify_btn = tk.Button(button_frame, text="Modify", width=10, command=self.modify_entry)
        delete_btn = tk.Button(button_frame, text="Delete", width=10, command=self.delete_entry)

        add_btn.grid(row=0, column=0, padx=5)
        modify_btn.grid(row=0, column=1, padx=5)
        delete_btn.grid(row=0, column=2, padx=5)

    def create_log_list(self):
        self.log_list = ttk.Treeview(self.bottom_frame, columns=("ID", "Callsign", "Frequency", "Mode", "Date", "Time"), show="headings")
        self.log_list.heading("ID", text="ID")
        self.log_list.heading("Callsign", text="Callsign")
        self.log_list.heading("Frequency", text="Frequency")
        self.log_list.heading("Mode", text="Mode")
        self.log_list.heading("Date", text="Date")
        self.log_list.heading("Time", text="Time")
        self.log_list.column("ID", width=30)

        self.log_list.bind("<<TreeviewSelect>>", self.on_select)

        self.log_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(self.bottom_frame, orient="vertical", command=self.log_list.yview)
        self.log_list.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)

    def populate_log_list(self):
        for row in self.log_list.get_children():
            self.log_list.delete(row)

        for entry in self.db.fetch_entries():
            self.log_list.insert("", tk.END, values=entry)

    def on_select(self, event):
        selected = self.log_list.selection()
        if selected:
            item = self.log_list.item(selected[0])
            values = item['values']
            self.selected_entry_id = values[0]

            # Populate fields
            self.callsign_entry.delete(0, tk.END)
            self.callsign_entry.insert(0, values[1])

            self.frequency_entry.delete(0, tk.END)
            self.frequency_entry.insert(0, values[2])

            self.mode_entry.delete(0, tk.END)
            self.mode_entry.insert(0, values[3])

            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, values[4])

            self.time_entry.delete(0, tk.END)
            self.time_entry.insert(0, values[5])

    def add_entry(self):
        self.db.add_entry(
            self.callsign_entry.get(),
            self.frequency_entry.get(),
            self.mode_entry.get(),
            self.date_entry.get(),
            self.time_entry.get()
        )
        self.populate_log_list()
        self.clear_fields()

    def modify_entry(self):
        if self.selected_entry_id:
            self.db.update_entry(
                self.selected_entry_id,
                self.callsign_entry.get(),
                self.frequency_entry.get(),
                self.mode_entry.get(),
                self.date_entry.get(),
                self.time_entry.get()
            )
            self.populate_log_list()
            self.clear_fields()
        else:
            messagebox.showwarning("Select Entry", "Please select an entry to modify.")

    def delete_entry(self):
        if self.selected_entry_id:
            self.db.delete_entry(self.selected_entry_id)
            self.populate_log_list()
            self.clear_fields()
        else:
            messagebox.showwarning("Select Entry", "Please select an entry to delete.")

    def clear_fields(self):
        self.selected_entry_id = None
        self.callsign_entry.delete(0, tk.END)
        self.frequency_entry.delete(0, tk.END)
        self.mode_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.time_entry.delete(0, tk.END)

# ==========================================================
# Main Program Entry Point
# ==========================================================

if __name__ == "__main__":
    app = HamLogApp()
    app.mainloop()
