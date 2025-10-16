#!/usr/bin/env python3
"""
Personal Calendar & Task Manager - Safe Version
A simple desktop application for managing appointments and tasks
with safer GUI initialization
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import calendar
from datetime import datetime, timedelta
import json
import os
import sys

class CalendarApp:
    def __init__(self, root):
        self.root = root
        self.fullscreen = False
        
        # Set window properties BEFORE any other operations
        try:
            self.root.title("Personal Calendar & Task Manager")
        except Exception as e:
            print(f"Error setting title: {e}")
            
        try:
            self.root.geometry("1000x700")
        except Exception as e:
            print(f"Error setting geometry: {e}")
        
        # Bind F11 for fullscreen and Escape to exit fullscreen
        self.root.bind('<F11>', self.toggle_fullscreen)
        self.root.bind('<Escape>', self.exit_fullscreen)
        
        # Data storage
        self.data_file = os.path.expanduser("~/calendar_data.json")
        self.appointments = {}
        self.todo_today = []
        self.todo_later = []
        
        # Load existing data
        print("Loading data...")
        self.load_data()
        print("Data loaded successfully")
        
        # Current date
        self.current_date = datetime.now()
        self.selected_date = None
        
        # Setup UI with error handling
        print("Setting up UI...")
        try:
            self.setup_ui()
            print("UI setup complete")
        except Exception as e:
            print(f"Error during UI setup: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
            
        # Update calendar
        print("Updating calendar...")
        try:
            self.update_calendar()
            print("Calendar updated")
        except Exception as e:
            print(f"Error updating calendar: {e}")
            import traceback
            traceback.print_exc()
        
    def setup_ui(self):
        # Main container with error handling
        try:
            main_frame = ttk.Frame(self.root, padding="10")
            main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        except Exception as e:
            print(f"Error creating main frame: {e}")
            raise
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Left panel - Task lists
        print("  Setting up left panel...")
        self.setup_left_panel(main_frame)
        
        # Right panel - Calendar
        print("  Setting up right panel...")
        self.setup_right_panel(main_frame)
        
    def setup_left_panel(self, parent):
        left_frame = ttk.Frame(parent, padding="5")
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_frame.columnconfigure(0, weight=1)
        
        # To Do Today section
        today_label = ttk.Label(left_frame, text="To Do Today", font=('Arial', 12, 'bold'))
        today_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Today list with scrollbar
        today_frame = ttk.Frame(left_frame)
        today_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        today_frame.columnconfigure(0, weight=1)
        today_frame.rowconfigure(0, weight=1)
        
        today_scroll = ttk.Scrollbar(today_frame)
        today_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.today_listbox = tk.Listbox(today_frame, height=10, yscrollcommand=today_scroll.set)
        self.today_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        today_scroll.config(command=self.today_listbox.yview)
        
        # Today buttons
        today_btn_frame = ttk.Frame(left_frame)
        today_btn_frame.grid(row=2, column=0, sticky=tk.W, pady=(0, 20))
        
        ttk.Button(today_btn_frame, text="Add", command=lambda: self.add_task('today')).pack(side=tk.LEFT, padx=2)
        ttk.Button(today_btn_frame, text="Remove", command=lambda: self.remove_task('today')).pack(side=tk.LEFT, padx=2)
        ttk.Button(today_btn_frame, text="Done", command=lambda: self.mark_done('today')).pack(side=tk.LEFT, padx=2)
        
        # Things to Get Around To section
        later_label = ttk.Label(left_frame, text="Things to Get Around To", font=('Arial', 12, 'bold'))
        later_label.grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        
        # Later list with scrollbar
        later_frame = ttk.Frame(left_frame)
        later_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        later_frame.columnconfigure(0, weight=1)
        later_frame.rowconfigure(0, weight=1)
        
        later_scroll = ttk.Scrollbar(later_frame)
        later_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.later_listbox = tk.Listbox(later_frame, height=10, yscrollcommand=later_scroll.set)
        self.later_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        later_scroll.config(command=self.later_listbox.yview)
        
        # Later buttons
        later_btn_frame = ttk.Frame(left_frame)
        later_btn_frame.grid(row=5, column=0, sticky=tk.W, pady=(5, 0))
        
        ttk.Button(later_btn_frame, text="Add", command=lambda: self.add_task('later')).pack(side=tk.LEFT, padx=2)
        ttk.Button(later_btn_frame, text="Remove", command=lambda: self.remove_task('later')).pack(side=tk.LEFT, padx=2)
        ttk.Button(later_btn_frame, text="Move to Today", command=self.move_to_today).pack(side=tk.LEFT, padx=2)
        
        # Configure row weights
        left_frame.rowconfigure(1, weight=1)
        left_frame.rowconfigure(4, weight=1)
        
        self.update_task_lists()
        
    def setup_right_panel(self, parent):
        right_frame = ttk.Frame(parent, padding="5")
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # Calendar header
        header_frame = ttk.Frame(right_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(1, weight=1)
        
        ttk.Button(header_frame, text="<", command=self.prev_month).grid(row=0, column=0, padx=5)
        
        self.month_year_label = ttk.Label(header_frame, text="", font=('Arial', 14, 'bold'))
        self.month_year_label.grid(row=0, column=1)
        
        ttk.Button(header_frame, text=">", command=self.next_month).grid(row=0, column=2, padx=5)
        ttk.Button(header_frame, text="Today", command=self.go_to_today).grid(row=0, column=3, padx=5)
        
        # Calendar grid
        self.calendar_frame = ttk.Frame(right_frame)
        self.calendar_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Day labels
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day in enumerate(days):
            label = ttk.Label(self.calendar_frame, text=day, font=('Arial', 10, 'bold'))
            label.grid(row=0, column=i, padx=2, pady=2, sticky=(tk.W, tk.E))
            self.calendar_frame.columnconfigure(i, weight=1)
        
        # Appointment display
        appt_frame = ttk.Frame(right_frame)
        appt_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        appt_frame.columnconfigure(0, weight=1)
        appt_frame.rowconfigure(1, weight=1)
        
        self.selected_date_label = ttk.Label(appt_frame, text="Select a date to view appointments", 
                                              font=('Arial', 11, 'bold'))
        self.selected_date_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Appointments list
        appt_list_frame = ttk.Frame(appt_frame)
        appt_list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        appt_list_frame.columnconfigure(0, weight=1)
        appt_list_frame.rowconfigure(0, weight=1)
        
        appt_scroll = ttk.Scrollbar(appt_list_frame)
        appt_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.appt_listbox = tk.Listbox(appt_list_frame, height=6, yscrollcommand=appt_scroll.set)
        self.appt_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        appt_scroll.config(command=self.appt_listbox.yview)
        
        # Appointment buttons
        appt_btn_frame = ttk.Frame(appt_frame)
        appt_btn_frame.grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        
        ttk.Button(appt_btn_frame, text="Add Appointment", command=self.add_appointment).pack(side=tk.LEFT, padx=2)
        ttk.Button(appt_btn_frame, text="Remove", command=self.remove_appointment).pack(side=tk.LEFT, padx=2)
        
        right_frame.rowconfigure(2, weight=0)
        
    def update_calendar(self):
        # Clear existing calendar buttons
        for widget in self.calendar_frame.grid_slaves():
            if int(widget.grid_info()["row"]) > 0:
                widget.destroy()
        
        # Update month/year label
        month_name = self.current_date.strftime("%B %Y")
        self.month_year_label.config(text=month_name)
        
        # Get calendar data
        year = self.current_date.year
        month = self.current_date.month
        cal = calendar.monthcalendar(year, month)
        
        today = datetime.now().date()
        
        # Create calendar buttons
        for week_num, week in enumerate(cal, start=1):
            for day_num, day in enumerate(week):
                if day == 0:
                    label = ttk.Label(self.calendar_frame, text="")
                    label.grid(row=week_num, column=day_num, padx=2, pady=2)
                else:
                    date = datetime(year, month, day).date()
                    date_str = date.strftime("%Y-%m-%d")
                    
                    has_appt = date_str in self.appointments and len(self.appointments[date_str]) > 0
                    
                    btn_text = str(day)
                    if has_appt:
                        btn_text += " *"
                    
                    btn = tk.Button(self.calendar_frame, text=btn_text, 
                                   command=lambda d=date: self.select_date(d),
                                   width=8, height=3)
                    
                    if date == today:
                        btn.config(bg='lightblue', font=('Arial', 10, 'bold'))
                    elif has_appt:
                        btn.config(bg='lightyellow')
                    
                    if self.selected_date and date == self.selected_date:
                        btn.config(relief=tk.SUNKEN, bg='lightgreen')
                    
                    btn.grid(row=week_num, column=day_num, padx=2, pady=2, sticky=(tk.W, tk.E, tk.N, tk.S))
                    
        for i in range(7):
            self.calendar_frame.rowconfigure(i, weight=1)
    
    def select_date(self, date):
        self.selected_date = date
        self.update_calendar()
        self.update_appointments_display()
        
    def update_appointments_display(self):
        if not self.selected_date:
            return
            
        date_str = self.selected_date.strftime("%Y-%m-%d")
        display_date = self.selected_date.strftime("%B %d, %Y")
        self.selected_date_label.config(text=f"Appointments for {display_date}")
        
        self.appt_listbox.delete(0, tk.END)
        if date_str in self.appointments:
            for appt in self.appointments[date_str]:
                self.appt_listbox.insert(tk.END, appt)
    
    def add_appointment(self):
        if not self.selected_date:
            messagebox.showwarning("No Date Selected", "Please select a date first.")
            return
            
        appt = simpledialog.askstring("New Appointment", "Enter appointment details:")
        if appt:
            date_str = self.selected_date.strftime("%Y-%m-%d")
            if date_str not in self.appointments:
                self.appointments[date_str] = []
            self.appointments[date_str].append(appt)
            self.save_data()
            self.update_calendar()
            self.update_appointments_display()
    
    def remove_appointment(self):
        if not self.selected_date:
            return
            
        selection = self.appt_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an appointment to remove.")
            return
            
        date_str = self.selected_date.strftime("%Y-%m-%d")
        idx = selection[0]
        
        if date_str in self.appointments and idx < len(self.appointments[date_str]):
            del self.appointments[date_str][idx]
            if not self.appointments[date_str]:
                del self.appointments[date_str]
            self.save_data()
            self.update_calendar()
            self.update_appointments_display()
    
    def update_task_lists(self):
        self.today_listbox.delete(0, tk.END)
        for task in self.todo_today:
            self.today_listbox.insert(tk.END, task)
        
        self.later_listbox.delete(0, tk.END)
        for task in self.todo_later:
            self.later_listbox.insert(tk.END, task)
    
    def add_task(self, list_type):
        task = simpledialog.askstring("New Task", "Enter task description:")
        if task:
            if list_type == 'today':
                self.todo_today.append(task)
            else:
                self.todo_later.append(task)
            self.save_data()
            self.update_task_lists()
    
    def remove_task(self, list_type):
        if list_type == 'today':
            listbox = self.today_listbox
            task_list = self.todo_today
        else:
            listbox = self.later_listbox
            task_list = self.todo_later
        
        selection = listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a task to remove.")
            return
        
        idx = selection[0]
        if idx < len(task_list):
            del task_list[idx]
            self.save_data()
            self.update_task_lists()
    
    def mark_done(self, list_type):
        if list_type == 'today':
            listbox = self.today_listbox
            task_list = self.todo_today
        else:
            return
        
        selection = listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a task to mark as done.")
            return
        
        idx = selection[0]
        if idx < len(task_list):
            task = task_list[idx]
            result = messagebox.askyesno("Mark Done", f"Mark this task as done?\n\n{task}")
            if result:
                del task_list[idx]
                self.save_data()
                self.update_task_lists()
    
    def move_to_today(self):
        selection = self.later_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a task to move to today.")
            return
        
        idx = selection[0]
        if idx < len(self.todo_later):
            task = self.todo_later[idx]
            del self.todo_later[idx]
            self.todo_today.append(task)
            self.save_data()
            self.update_task_lists()
    
    def prev_month(self):
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month - 1)
        self.update_calendar()
    
    def next_month(self):
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        self.update_calendar()
    
    def go_to_today(self):
        self.current_date = datetime.now()
        self.update_calendar()
    
    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes('-fullscreen', self.fullscreen)
        return "break"
    
    def exit_fullscreen(self, event=None):
        if self.fullscreen:
            self.fullscreen = False
            self.root.attributes('-fullscreen', False)
        return "break"
    
    def save_data(self):
        try:
            data = {
                'appointments': self.appointments,
                'todo_today': self.todo_today,
                'todo_later': self.todo_later
            }
            
            temp_file = self.data_file + '.tmp'
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            if os.path.exists(self.data_file):
                os.replace(temp_file, self.data_file)
            else:
                os.rename(temp_file, self.data_file)
                
        except Exception as e:
            print(f"Error saving data: {e}")
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                file_size = os.path.getsize(self.data_file)
                if file_size > 10 * 1024 * 1024:
                    print(f"Warning: Data file is very large ({file_size} bytes). Creating backup and resetting.")
                    os.rename(self.data_file, self.data_file + '.backup')
                    self.appointments = {}
                    self.todo_today = []
                    self.todo_later = []
                    return
                
                with open(self.data_file, 'r') as f:
                    content = f.read()
                    
                if not content.strip():
                    print("Data file is empty, starting fresh.")
                    self.appointments = {}
                    self.todo_today = []
                    self.todo_later = []
                    return
                
                data = json.loads(content)
                self.appointments = data.get('appointments', {})
                self.todo_today = data.get('todo_today', [])
                self.todo_later = data.get('todo_later', [])
                print(f"Successfully loaded data from {self.data_file}")
                
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                print("Creating backup and starting with fresh data.")
                os.rename(self.data_file, self.data_file + '.corrupted')
                self.appointments = {}
                self.todo_today = []
                self.todo_later = []
            except Exception as e:
                print(f"Error loading data: {e}")
                print("Starting with fresh data.")
                self.appointments = {}
                self.todo_today = []
                self.todo_later = []
        else:
            print(f"No existing data file found at {self.data_file}. Starting fresh.")
            self.appointments = {}
            self.todo_today = []
            self.todo_later = []

def main():
    print("Starting Calendar App...")
    print(f"Python version: {sys.version}")
    
    try:
        print("Creating Tk root...")
        root = tk.Tk()
        print("Tk root created successfully")
        
        print("Initializing CalendarApp...")
        app = CalendarApp(root)
        print("CalendarApp initialized successfully")
        
        print("Starting mainloop...")
        root.mainloop()
        print("Mainloop ended normally")
        
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
