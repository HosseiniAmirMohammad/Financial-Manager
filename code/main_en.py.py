import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import json
import os
import sys
import datetime
import re
from collections import defaultdict
import hashlib

# File Paths For Data Storage
DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")
DATA_FILE = os.path.join(DESKTOP, "finance_data.json")
SETTINGS_FILE = os.path.join(DESKTOP, "settings.json")
PASSWORD_FILE = os.path.join(DESKTOP, "password.json")

# Default Color Scheme
DEFAULT_COLORS = {
    "bg": "#FFE4E1",
    "table_bg": "#FFF0F5",
    "btn_green": "#4CAF50",
    "btn_blue": "#2196F3",
    "btn_red": "#F44336",
    "btn_orange": "#FF9800",
    "btn_purple": "#9C27B0"
}

# Gregorian calendar
GREGORIAN_MONTHS = ["January", "February", "March", "April", "May", "June", 
                    "July", "August", "September", "October", "November", "December"]
MONTHS_MAP = {name: i+1 for i, name in enumerate(GREGORIAN_MONTHS)}

# Password Functions

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_password_data():
    """Load password data from file"""
    if os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_password_data(password_hash, question, answer_hash):
    """Save password data to file"""
    data = {
        "password_hash": password_hash,
        "question": question,
        "answer_hash": answer_hash
    }
    with open(PASSWORD_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def check_password(password):
    """Verify if the entered password matches the stored hash"""
    password_data = load_password_data()
    if not password_data:
        return True
    return hash_password(password) == password_data["password_hash"]

# Settings Function

def load_settings():
    """Load application settings from file"""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "auto_date": True,
        "add_salary_to_balance": True,
        "bg_color": DEFAULT_COLORS["bg"],
        "table_bg": DEFAULT_COLORS["table_bg"],
        "btn_green": DEFAULT_COLORS["btn_green"],
        "btn_blue": DEFAULT_COLORS["btn_blue"],
        "btn_red": DEFAULT_COLORS["btn_red"],
        "btn_orange": DEFAULT_COLORS["btn_orange"],
        "btn_purple": DEFAULT_COLORS["btn_purple"]
    }

def save_settings(settings):
    """Save Application Settings to File"""
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

# Load Settings at Startup
settings = load_settings()

# Core Functions

def get_today_date():
    """Gregorian Calendar Format"""
    return datetime.date.today().strftime("%Y/%m/%d")

def convert_to_number(text):
    """Convert user input to number, removing non-digit characters"""
    cleaned = re.sub(r'[^\d]', '', str(text))
    try:
        return int(cleaned) if cleaned else 0
    except:
        return 0

def load_data():
    """Load Financial Data"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure all required fields exist
            if "balance" not in data:
                data["balance"] = 0
            if "initial_balance" not in data:
                data["initial_balance"] = 0
            if "monthly_balances" not in data:
                data["monthly_balances"] = {}
            if "notes" not in data:
                data["notes"] = {}
            return data
    return {
        "transactions": [],
        "salary": [],
        "savings": [],
        "charity": [],
        "debt_claim": [],
        "installments": [],
        "balance": 0,
        "initial_balance": 0,
        "monthly_balances": {},
        "notes": {}
    }

def save_data(data):
    """Save Financial Data to File"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_last_day_of_month(year, month):
    """Get the last day of a given month in Gregorian calendar"""
    if month in [1, 3, 5, 7, 8, 10, 12]:
        return 31
    elif month in [4, 6, 9, 11]:
        return 30
    else:  # February
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            return 29
        return 28

def get_month_key():
    """Generate a unique key for the current month"""
    return f"{filter_year.get()}_{filter_month.get()}"

def get_selected_date_range():
    """Get the date range for the selected month and year"""
    year = int(filter_year.get())
    month_name = filter_month.get()
    month_num = MONTHS_MAP[month_name]
    
    start_date = datetime.date(year, month_num, 1)
    last_day = get_last_day_of_month(year, month_num)
    end_date = datetime.date(year, month_num, last_day)
    
    return start_date, end_date

def _in_range(date_str, start, end):
    """Check if a date string falls within a given range"""
    try:
        y, m, d = map(int, date_str.split('/'))
        return start <= datetime.date(y, m, d) <= end
    except:
        return False

# Password Dialogs

def show_password_dialog():
    """Display password dialog for login or initial setup"""
    password_data = load_password_data()

    if not password_data:
        # create password
        dialog = tk.Toplevel(root)
        dialog.title("Set Password")
        dialog.geometry("500x500")
        dialog.configure(bg=settings["bg_color"])
        dialog.transient(root)
        dialog.grab_set()

        tk.Label(dialog, text="🔐 Set Password", bg=settings["bg_color"],
                font=("Arial", 14, "bold")).pack(pady=20)
        
        tk.Label(dialog, text="New Password:", bg=settings["bg_color"], 
                font=("Arial", 11)).pack(pady=5)
        password_entry = tk.Entry(dialog, show="*", width=30, font=("Arial", 11))
        password_entry.pack(pady=5)
        
        tk.Label(dialog, text="Confirm Password:", bg=settings["bg_color"], 
                font=("Arial", 11)).pack(pady=5)
        confirm_entry = tk.Entry(dialog, show="*", width=30, font=("Arial", 11))
        confirm_entry.pack(pady=5)
        
        tk.Label(dialog, text="Security Question:", bg=settings["bg_color"], 
                font=("Arial", 11)).pack(pady=5)
        question_entry = tk.Entry(dialog, width=30, font=("Arial", 11))
        question_entry.insert(0, "What is your favorite food?")
        question_entry.pack(pady=5)
        
        tk.Label(dialog, text="Security Answer:", bg=settings["bg_color"], 
                font=("Arial", 11)).pack(pady=5)
        answer_entry = tk.Entry(dialog, width=30, font=("Arial", 11))
        answer_entry.pack(pady=5)

        def save_password():
            password = password_entry.get().strip()
            confirm = confirm_entry.get().strip()
            question = question_entry.get().strip()
            answer = answer_entry.get().strip()
            
            if not password or not confirm:
                messagebox.showerror("Error", "Please enter a password")
                return
            if password != confirm:
                messagebox.showerror("Error", "Passwords do not match")
                return
            if not question or not answer:
                messagebox.showerror("Error", "Please enter security question and answer")
                return
                
            save_password_data(hash_password(password), question, hash_password(answer))
            dialog.destroy()
            messagebox.showinfo("Success", "Password set successfully")

        tk.Button(dialog, text="Set Password", command=save_password,
                 bg=settings["btn_green"], fg='white', 
                 font=("Arial", 11), padx=20, pady=5).pack(pady=20)
        
        root.wait_window(dialog)
        return load_password_data() is not None

    else:
        # login
        attempt = 0
        while attempt < 3:
            dialog = tk.Toplevel(root)
            dialog.title("Login")
            dialog.geometry("350x250")
            dialog.configure(bg=settings["bg_color"])
            dialog.transient(root)
            dialog.grab_set()

            tk.Label(dialog, text="Login", bg=settings["bg_color"],
                    font=("Arial", 14, "bold")).pack(pady=20)
            tk.Label(dialog, text="Password:", bg=settings["bg_color"], 
                    font=("Arial", 11)).pack(pady=5)
            password_entry = tk.Entry(dialog, show="*", width=30, font=("Arial", 11))
            password_entry.pack(pady=5)
            password_entry.focus()

            result = {"success": False}

            def check_entered_password():
                if check_password(password_entry.get().strip()):
                    result["success"] = True
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Incorrect password")
                    password_entry.delete(0, tk.END)
                    password_entry.focus()

            def forgot_password():
                dialog.destroy()
                show_forgot_password_dialog()

            btn_frame = tk.Frame(dialog, bg=settings["bg_color"])
            btn_frame.pack(pady=20)
            
            tk.Button(btn_frame, text="Login", command=check_entered_password,
                     bg=settings["btn_green"], fg='white', 
                     font=("Arial", 11), padx=20, pady=5).pack(side=tk.LEFT, padx=10)
            tk.Button(btn_frame, text="Forgot Password", command=forgot_password,
                     bg=settings["btn_red"], fg='white', 
                     font=("Arial", 10), padx=15, pady=5).pack(side=tk.LEFT, padx=10)
            
            dialog.bind("<Return>", lambda e: check_entered_password())
            root.wait_window(dialog)

            if result["success"]:
                return True
            attempt += 1

        messagebox.showerror("Error", "Maximum login attempts exceeded")
        return False

def show_forgot_password_dialog():
    """Display forgot password dialog for recovery"""
    password_data = load_password_data()
    if not password_data:
        messagebox.showerror("Error", "No password has been set")
        return

    dialog = tk.Toplevel(root)
    dialog.title("Password Recovery")
    dialog.geometry("400x300")
    dialog.configure(bg=settings["bg_color"])
    dialog.transient(root)
    dialog.grab_set()

    tk.Label(dialog, text="❓ Password Recovery", bg=settings["bg_color"],
            font=("Arial", 14, "bold")).pack(pady=20)
    tk.Label(dialog, text=f"Security Question: {password_data['question']}",
            bg=settings["bg_color"], font=("Arial", 11)).pack(pady=10)
    tk.Label(dialog, text="Answer:", bg=settings["bg_color"], 
            font=("Arial", 11)).pack(pady=5)
    answer_entry = tk.Entry(dialog, width=30, font=("Arial", 11))
    answer_entry.pack(pady=5)
    answer_entry.focus()

    def set_new_password():
        answer = answer_entry.get().strip()
        if hash_password(answer) == password_data["answer_hash"]:
            dialog.destroy()
            change_password_dialog(force_change=True)
        else:
            messagebox.showerror("Error", "Incorrect answer")
            answer_entry.delete(0, tk.END)
            answer_entry.focus()

    btn_frame = tk.Frame(dialog, bg=settings["bg_color"])
    btn_frame.pack(pady=20)
    tk.Button(btn_frame, text="Verify Answer", command=set_new_password,
             bg=settings["btn_green"], fg='white', 
             font=("Arial", 11), padx=20, pady=5).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="Cancel", command=dialog.destroy,
             bg=settings["btn_red"], fg='white', 
             font=("Arial", 10), padx=15, pady=5).pack(side=tk.LEFT, padx=10)
    
    dialog.bind("<Return>", lambda e: set_new_password())
    root.wait_window(dialog)

def change_password_dialog(force_change=False):
    """Display dialog to change password"""
    dialog = tk.Toplevel(root)
    dialog.title("Change Password")
    dialog.geometry("400x380")
    dialog.configure(bg=settings["bg_color"])
    dialog.transient(root)
    dialog.grab_set()

    tk.Label(dialog, text="Change Password", bg=settings["bg_color"],
            font=("Arial", 14, "bold")).pack(pady=20)

    old_pass_entry = None
    if not force_change:
        tk.Label(dialog, text="Current Password:", bg=settings["bg_color"], 
                font=("Arial", 11)).pack(pady=5)
        old_pass_entry = tk.Entry(dialog, show="*", width=30, font=("Arial", 11))
        old_pass_entry.pack(pady=5)

    tk.Label(dialog, text="New Password:", bg=settings["bg_color"], 
            font=("Arial", 11)).pack(pady=5)
    new_pass_entry = tk.Entry(dialog, show="*", width=30, font=("Arial", 11))
    new_pass_entry.pack(pady=5)
    
    tk.Label(dialog, text="Confirm New Password:", bg=settings["bg_color"], 
            font=("Arial", 11)).pack(pady=5)
    confirm_entry = tk.Entry(dialog, show="*", width=30, font=("Arial", 11))
    confirm_entry.pack(pady=5)
    
    tk.Label(dialog, text="New Security Question:", bg=settings["bg_color"], 
            font=("Arial", 11)).pack(pady=5)
    question_entry = tk.Entry(dialog, width=30, font=("Arial", 11))
    password_data = load_password_data()
    question_entry.insert(0, password_data["question"] if password_data else "What is your mother's name?")
    question_entry.pack(pady=5)
    
    tk.Label(dialog, text="New Security Answer:", bg=settings["bg_color"], 
            font=("Arial", 11)).pack(pady=5)
    answer_entry = tk.Entry(dialog, width=30, font=("Arial", 11))
    answer_entry.pack(pady=5)

    def save_new_password():
        if not force_change:
            pd = load_password_data()
            if not pd or hash_password(old_pass_entry.get().strip()) != pd["password_hash"]:
                messagebox.showerror("Error", "Current password is incorrect")
                return
        
        new_pass = new_pass_entry.get().strip()
        confirm = confirm_entry.get().strip()
        question = question_entry.get().strip()
        answer = answer_entry.get().strip()
        
        if not new_pass or not confirm:
            messagebox.showerror("Error", "Please enter a new password")
            return
        if new_pass != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return
        if not question or not answer:
            messagebox.showerror("Error", "Please enter security question and answer")
            return
            
        save_password_data(hash_password(new_pass), question, hash_password(answer))
        dialog.destroy()
        messagebox.showinfo("Success", "Password changed successfully")

    tk.Button(dialog, text="Change Password", command=save_new_password,
             bg=settings["btn_green"], fg='white', 
             font=("Arial", 11), padx=20, pady=5).pack(pady=20)

# Balance Functions

def get_current_month_balance():
    """Get the balance for the current month"""
    key = get_month_key()
    return data["monthly_balances"].get(key, 0)

def set_current_month_balance(amount):
    """Set the balance for the current month"""
    key = get_month_key()
    data["monthly_balances"][key] = amount
    save_data(data)

def update_balance():
    """Update the balance display"""
    balance = get_current_month_balance()
    lbl_balance.config(text=f"💰 Current Balance: ${balance:,}")
    return balance

# Main Application

# Initialize Main Window
root = tk.Tk()
root.tk.call('tk', 'scaling', 2)
root.title("Financial Manager")
root.geometry("1300x950")
root.configure(bg=settings["bg_color"])
root.resizable(True, True)

# Show password dialog before loading the main application
if not show_password_dialog():
    root.destroy()
    sys.exit()

# Configure Styles
style = ttk.Style()
style.configure("TNotebook", background=settings["bg_color"])
style.configure("TFrame", background=settings["bg_color"])
style.configure("Treeview", 
                background=settings["table_bg"], 
                fieldbackground=settings["table_bg"], 
                font=("Arial", 10))
style.configure("Treeview.Heading", font=("Arial", 11, "bold"))
style.configure("Treeview", rowheight=30)

# Load data
data = load_data()

# Top Frame
top_frame = tk.Frame(root, bg=settings["bg_color"])
top_frame.pack(fill=tk.X, padx=10, pady=5)

balance_frame = tk.Frame(top_frame, bg=settings["bg_color"], relief=tk.RIDGE, bd=2)
balance_frame.pack(fill=tk.X, padx=10, pady=5)

lbl_balance = tk.Label(balance_frame, text="💰 Current Balance: $0",
                       bg=settings["bg_color"], font=("Arial", 14, "bold"), 
                       fg=settings["btn_green"])
lbl_balance.pack(padx=20, pady=5)

def set_initial_balance():
    """Dialog to set initial balance"""
    dialog = tk.Toplevel(root)
    dialog.title("Set Balance")
    dialog.geometry("300x150")
    dialog.configure(bg=settings["bg_color"])
    dialog.transient(root)
    dialog.grab_set()
    
    tk.Label(dialog, text="Enter your balance in USD:", bg=settings["bg_color"], 
            font=("Arial", 11)).pack(pady=10)
    entry_balance = tk.Entry(dialog, font=("Arial", 11), width=20)
    entry_balance.pack(pady=5)

    def save_initial():
        try:
            amount = convert_to_number(entry_balance.get())
            set_current_month_balance(amount)
            update_balance()
            save_data(data)
            dialog.destroy()
            messagebox.showinfo("Success", "Balance recorded")
        except:
            messagebox.showerror("Error", "Please enter a valid number")

    tk.Button(dialog, text="Save", command=save_initial, 
             bg=settings["btn_green"], fg='white').pack(pady=10)

tk.Button(balance_frame, text="Set Initial Balance", command=set_initial_balance,
          bg=settings["btn_blue"], fg='white', font=("Arial", 10)).pack(padx=20, pady=5)

# Filter Section

def apply_filter():
    """Apply all filters and update all views"""
    update_transactions()
    update_salary_list()
    update_savings_list()
    update_charity_list()
    update_debt_claim_list()
    update_monthly_report()
    update_yearly_report()
    update_installments_list()
    update_notes()
    update_balance()

filter_frame = tk.Frame(top_frame, bg=settings["bg_color"])
filter_frame.pack(side=tk.RIGHT, padx=10)

tk.Label(filter_frame, text="Filter by Month:", bg=settings["bg_color"], 
         font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=5)
tk.Label(filter_frame, text="Month:", bg=settings["bg_color"]).pack(side=tk.LEFT, padx=2)

filter_month = ttk.Combobox(filter_frame, values=GREGORIAN_MONTHS, width=10)
current_month = datetime.date.today().strftime("%B")
filter_month.set(current_month)
filter_month.pack(side=tk.LEFT, padx=2)
filter_month.bind("<<ComboboxSelected>>", lambda e: apply_filter())

tk.Label(filter_frame, text="Year:", bg=settings["bg_color"]).pack(side=tk.LEFT, padx=2)
filter_year = ttk.Combobox(filter_frame, values=[str(i) for i in range(2020, 2035)], width=6)
filter_year.set(str(datetime.date.today().year))
filter_year.pack(side=tk.LEFT, padx=2)
filter_year.bind("<<ComboboxSelected>>", lambda e: apply_filter())

tk.Button(filter_frame, text="🔄 Refresh", command=apply_filter, 
          bg=settings["btn_orange"], fg='white', font=("Arial", 10)).pack(side=tk.LEFT, padx=10)

# Notebook
notebook = ttk.Notebook(root, padding=10)
notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Date Picker

def select_date(title="Select Date", default_date=None):
    """Popup date selection dialog"""
    result = {"date": None, "success": False}

    dialog = tk.Toplevel(root)
    dialog.title(title)
    dialog.geometry("300x280")
    dialog.configure(bg=settings["bg_color"])
    dialog.transient(root)
    dialog.grab_set()

    tk.Label(dialog, text="Select Date:", bg=settings["bg_color"], 
            font=("Arial", 12, "bold")).pack(pady=10)

    today = datetime.date.today()
    default_day = today.strftime("%d")
    default_month = today.strftime("%B")
    default_year = str(today.year)

    # Day Selection
    frame_day = tk.Frame(dialog, bg=settings["bg_color"])
    frame_day.pack(pady=5)
    tk.Label(frame_day, text="Day:", bg=settings["bg_color"], 
            font=("Arial", 11)).pack(side=tk.LEFT, padx=5)
    day_spin = ttk.Combobox(frame_day, values=[f"{i:02d}" for i in range(1, 32)], width=5)
    day_spin.set(default_day)
    day_spin.pack(side=tk.LEFT)

    # Month Selection
    frame_month = tk.Frame(dialog, bg=settings["bg_color"])
    frame_month.pack(pady=5)
    tk.Label(frame_month, text="Month:", bg=settings["bg_color"], 
            font=("Arial", 11)).pack(side=tk.LEFT, padx=5)
    month_combo = ttk.Combobox(frame_month, values=GREGORIAN_MONTHS, width=10)
    month_combo.set(default_month)
    month_combo.pack(side=tk.LEFT)

    # Year Selection
    frame_year = tk.Frame(dialog, bg=settings["bg_color"])
    frame_year.pack(pady=5)
    tk.Label(frame_year, text="Year:", bg=settings["bg_color"], 
            font=("Arial", 11)).pack(side=tk.LEFT, padx=5)
    year_combo = ttk.Combobox(frame_year, values=[str(i) for i in range(2020, 2035)], width=6)
    year_combo.set(default_year)
    year_combo.pack(side=tk.LEFT)

    def confirm():
        try:
            year = int(year_combo.get())
            month_name = month_combo.get()
            month_num = MONTHS_MAP[month_name]
            day = int(day_spin.get())
            selected_date = datetime.date(year, month_num, day)
            result["date"] = selected_date.strftime("%Y/%m/%d")
            result["success"] = True
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Invalid date: {e}")

    tk.Button(dialog, text="✅ Confirm", command=confirm,
              bg=settings["btn_green"], fg='white', 
              font=("Arial", 11), padx=20, pady=5).pack(pady=20)

    root.wait_window(dialog)
    return result["date"] if result["success"] else None


# TRANSACTIONS TAB 

frame_trans = tk.Frame(notebook, bg=settings["bg_color"])
notebook.add(frame_trans, text="📋 Transactions")

form_frame = tk.Frame(frame_trans, bg=settings["bg_color"])
form_frame.pack(pady=10)

tk.Label(form_frame, text="Title:", bg=settings["bg_color"], 
         font=("Arial", 11)).grid(row=0, column=0, padx=10, pady=5)
entry_title = tk.Entry(form_frame, width=30, font=("Arial", 11))
entry_title.grid(row=0, column=1, padx=10, pady=5)

tk.Label(form_frame, text="Amount (USD):", bg=settings["bg_color"], 
         font=("Arial", 11)).grid(row=0, column=2, padx=10, pady=5)
entry_amount = tk.Entry(form_frame, width=20, font=("Arial", 11))
entry_amount.grid(row=0, column=3, padx=10, pady=5)

def add_transaction():
    """Add a new expense transaction"""
    title = entry_title.get().strip()
    if not title:
        messagebox.showerror("Error", "Please enter a title")
        return
    amount = convert_to_number(entry_amount.get())

    selected_date = select_date("Select Transaction Date")
    if selected_date is None:
        return

    data["transactions"].append({"title": title, "amount": amount, "date": selected_date})
    balance = get_current_month_balance() - amount
    set_current_month_balance(balance)
    save_data(data)

    entry_title.delete(0, tk.END)
    entry_amount.delete(0, tk.END)
    update_transactions()
    update_monthly_report()
    update_yearly_report()
    update_balance()
    messagebox.showinfo("Success", f"Transaction recorded for {selected_date}")

tk.Button(form_frame, text="➕ Add", command=add_transaction, 
          bg=settings["btn_green"], fg='white', 
          font=("Arial", 11)).grid(row=1, column=0, columnspan=4, pady=10)

# Transactions List
columns_trans = ("Date", "Title", "Amount (USD)")
tree_trans = ttk.Treeview(frame_trans, columns=columns_trans, show="headings", height=8)
for col in columns_trans:
    tree_trans.heading(col, text=col)
tree_trans.column("Date", width=110, anchor="center")
tree_trans.column("Title", width=380, anchor="center")
tree_trans.column("Amount (USD)", width=160, anchor="center")
tree_trans.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

# Action Buttons
trans_btn_frame = tk.Frame(frame_trans, bg=settings["bg_color"])
trans_btn_frame.pack(pady=5)
tk.Button(trans_btn_frame, text="✏️ Edit Row", command=lambda: edit_selected_transaction(),
          bg=settings["btn_orange"], fg='white', font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
tk.Button(trans_btn_frame, text="🗑 Delete Row",
          command=lambda: deleted_selected(tree_trans, data["transactions"], "transaction"),
          bg=settings["btn_red"], fg='white', font=("Arial", 10)).pack(side=tk.LEFT, padx=5)

# Monthly Report
report_frame = tk.Frame(frame_trans, bg=settings["bg_color"])
report_frame.pack(fill=tk.X, padx=10, pady=5)
tk.Label(report_frame, text="📊 Monthly Report:", bg=settings["bg_color"], 
         font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)
monthly_report_text = tk.Text(report_frame, height=6, width=60, 
                              font=("Arial", 10), bg=settings["table_bg"])
monthly_report_text.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)

def update_monthly_report():
    """Update the monthly report display"""
    monthly_report_text.delete(1.0, tk.END)
    monthly_expense = defaultdict(int)
    monthly_income = defaultdict(int)

    for t in data["transactions"]:
        try:
            y, m, d = map(int, t["date"].split('/'))
            monthly_expense[f"{y} {GREGORIAN_MONTHS[m-1]}"] += t["amount"]
        except:
            pass

    for s in data["salary"]:
        try:
            y, m, d = map(int, s["date"].split('/'))
            monthly_income[f"{y} {GREGORIAN_MONTHS[m-1]}"] += s["amount"]
        except:
            pass

    report = "Monthly Financial Report:\n" + "-" * 50 + "\n"
    all_months = set(monthly_expense.keys()) | set(monthly_income.keys())
    for month in sorted(all_months):
        income = monthly_income.get(month, 0)
        expense = monthly_expense.get(month, 0)
        net = income - expense
        report += f"{month}:\n   Income: ${income:,}\n   Expense: ${expense:,}\n   Balance: ${net:,}\n\n"

    if not all_months:
        report += "No data available"
    monthly_report_text.insert(1.0, report)

def update_transactions():
    """Refresh the transactions list with current filter"""
    for row in tree_trans.get_children():
        tree_trans.delete(row)

    start_date, end_date = get_selected_date_range()
    filtered = [t for t in data["transactions"] if _in_range(t["date"], start_date, end_date)]
    filtered.sort(key=lambda x: x["date"], reverse=True)

    for t in filtered:
        tree_trans.insert("", tk.END, values=(t["date"], t["title"], f"${t['amount']:,}"))

def edit_selected_transaction():
    """Edit the selected transaction"""
    selected = tree_trans.selection()
    if not selected:
        messagebox.showerror("Error", "Please select a row")
        return
    item = tree_trans.item(selected[0])
    values = item['values']
    index = tree_trans.index(selected[0])
    actual_index = -(index + 1)

    dialog = tk.Toplevel(root)
    dialog.title("Edit Transaction")
    dialog.geometry("400x300")
    dialog.configure(bg=settings["bg_color"])
    dialog.transient(root)
    dialog.grab_set()

    tk.Label(dialog, text="Title:", bg=settings["bg_color"], 
            font=("Arial", 11)).grid(row=0, column=0, padx=10, pady=10, sticky='e')
    entry_edit_title = tk.Entry(dialog, width=30, font=("Arial", 11))
    entry_edit_title.insert(0, values[1])
    entry_edit_title.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(dialog, text="Amount (USD):", bg=settings["bg_color"], 
            font=("Arial", 11)).grid(row=1, column=0, padx=10, pady=10, sticky='e')
    entry_edit_amount = tk.Entry(dialog, width=20, font=("Arial", 11))
    entry_edit_amount.insert(0, values[2].replace("$", "").replace(",", ""))
    entry_edit_amount.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(dialog, text="Date:", bg=settings["bg_color"], 
            font=("Arial", 11)).grid(row=2, column=0, padx=10, pady=10, sticky='e')
    entry_edit_date = tk.Entry(dialog, width=20, font=("Arial", 11))
    entry_edit_date.insert(0, values[0])
    entry_edit_date.grid(row=2, column=1, padx=10, pady=10)

    def save_edit():
        new_title = entry_edit_title.get().strip()
        if not new_title:
            messagebox.showerror("Error", "Please enter a title")
            return
        new_amount = convert_to_number(entry_edit_amount.get())
        new_date = entry_edit_date.get().strip()
        old_amount = data["transactions"][actual_index]["amount"]
        data["transactions"][actual_index] = {"title": new_title, "amount": new_amount, "date": new_date}

        balance = get_current_month_balance() + old_amount - new_amount
        set_current_month_balance(balance)
        save_data(data)

        update_transactions()
        update_monthly_report()
        update_yearly_report()
        update_balance()
        dialog.destroy()
        messagebox.showinfo("Success", "Transaction updated")

    tk.Button(dialog, text="Save Changes", command=save_edit, 
             bg=settings["btn_green"], fg='white', 
             font=("Arial", 11)).grid(row=3, column=0, columnspan=2, pady=20)

# SALARY TAB

frame_salary = tk.Frame(notebook, bg=settings["bg_color"])
notebook.add(frame_salary, text="💰 Salary")

salary_form = tk.Frame(frame_salary, bg=settings["bg_color"])
salary_form.pack(pady=10)

tk.Label(salary_form, text="Source:", bg=settings["bg_color"], 
         font=("Arial", 11)).grid(row=0, column=0, padx=10, pady=5)
entry_salary_source = tk.Entry(salary_form, width=25, font=("Arial", 11))
entry_salary_source.grid(row=0, column=1, padx=10, pady=5)

tk.Label(salary_form, text="Amount (USD):", bg=settings["bg_color"], 
         font=("Arial", 11)).grid(row=0, column=2, padx=10, pady=5)
entry_salary = tk.Entry(salary_form, width=20, font=("Arial", 11))
entry_salary.grid(row=0, column=3, padx=10, pady=5)

def add_salary():
    """Add salary income"""
    source = entry_salary_source.get().strip()
    if not source:
        messagebox.showerror("Error", "Please enter a source")
        return
    amount = convert_to_number(entry_salary.get())

    selected_date = select_date("Select Salary Date")
    if selected_date is None:
        return

    data["salary"].append({"source": source, "amount": amount, "date": selected_date})
    balance = get_current_month_balance() + amount
    set_current_month_balance(balance)
    save_data(data)

    entry_salary_source.delete(0, tk.END)
    entry_salary.delete(0, tk.END)
    update_salary_list()
    update_monthly_report()
    update_yearly_report()
    update_balance()
    messagebox.showinfo("Success", f"Salary recorded for {selected_date}")

tk.Button(salary_form, text="Add Salary", command=add_salary, 
          bg=settings["btn_blue"], fg='white', 
          font=("Arial", 11)).grid(row=1, column=0, columnspan=4, pady=10)

columns_salary = ("Date", "Source", "Amount (USD)")
tree_salary = ttk.Treeview(frame_salary, columns=columns_salary, show="headings", height=8)
for col in columns_salary:
    tree_salary.heading(col, text=col)
tree_salary.column("Date", width=100, anchor="center")
tree_salary.column("Source", width=200, anchor="center")
tree_salary.column("Amount (USD)", width=150, anchor="center")
tree_salary.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

total_salary_frame = tk.Frame(frame_salary, bg=settings["bg_color"])
total_salary_frame.pack(fill=tk.X, padx=10, pady=5)
lbl_total_salary = tk.Label(total_salary_frame, text="", bg=settings["bg_color"], 
                            font=("Arial", 12, "bold"), fg=settings["btn_blue"])
lbl_total_salary.pack()

salary_btn_frame = tk.Frame(frame_salary, bg=settings["bg_color"])
salary_btn_frame.pack(pady=5)
tk.Button(salary_btn_frame, text="✏️ Edit Row", command=lambda: edit_selected_salary(),
          bg=settings["btn_orange"], fg='white', font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
tk.Button(salary_btn_frame, text="🗑 Delete Row",
          command=lambda: deleted_selected(tree_salary, data["salary"], "salary"),
          bg=settings["btn_red"], fg='white', font=("Arial", 10)).pack(side=tk.LEFT, padx=5)

def update_salary_list():
    """Refresh the salary list with current filter"""
    for row in tree_salary.get_children():
        tree_salary.delete(row)

    start_date, end_date = get_selected_date_range()
    filtered = [s for s in data["salary"] if _in_range(s["date"], start_date, end_date)]
    filtered.sort(key=lambda x: x["date"], reverse=True)

    total = sum(s["amount"] for s in filtered)
    for s in filtered:
        tree_salary.insert("", tk.END, values=(s["date"], s["source"], f"${s['amount']:,}"))
    lbl_total_salary.config(text=f"Total Salary: ${total:,}")

def edit_selected_salary():
    """Edit the selected salary entry"""
    selected = tree_salary.selection()
    if not selected:
        messagebox.showerror("Error", "Please select a row")
        return
    item = tree_salary.item(selected[0])
    values = item['values']
    index = tree_salary.index(selected[0])
    actual_index = -(index + 1)

    dialog = tk.Toplevel(root)
    dialog.title("Edit Salary")
    dialog.geometry("400x250")
    dialog.configure(bg=settings["bg_color"])
    dialog.transient(root)
    dialog.grab_set()

    tk.Label(dialog, text="Source:", bg=settings["bg_color"], 
            font=("Arial", 11)).grid(row=0, column=0, padx=10, pady=10, sticky='e')
    entry_edit_source = tk.Entry(dialog, width=30, font=("Arial", 11))
    entry_edit_source.insert(0, values[1])
    entry_edit_source.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(dialog, text="Amount (USD):", bg=settings["bg_color"], 
            font=("Arial", 11)).grid(row=1, column=0, padx=10, pady=10, sticky='e')
    entry_edit_amount = tk.Entry(dialog, width=20, font=("Arial", 11))
    entry_edit_amount.insert(0, values[2].replace("$", "").replace(",", ""))
    entry_edit_amount.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(dialog, text="Date:", bg=settings["bg_color"], 
            font=("Arial", 11)).grid(row=2, column=0, padx=10, pady=10, sticky='e')
    entry_edit_date = tk.Entry(dialog, width=20, font=("Arial", 11))
    entry_edit_date.insert(0, values[0])
    entry_edit_date.grid(row=2, column=1, padx=10, pady=10)

    def save_edit():
        new_source = entry_edit_source.get().strip()
        if not new_source:
            messagebox.showerror("Error", "Please enter a source")
            return
        new_amount = convert_to_number(entry_edit_amount.get())
        new_date = entry_edit_date.get().strip()
        old_amount = data["salary"][actual_index]["amount"]
        data["salary"][actual_index] = {"source": new_source, "amount": new_amount, "date": new_date}

        balance = get_current_month_balance() - old_amount + new_amount
        set_current_month_balance(balance)
        save_data(data)

        update_salary_list()
        update_monthly_report()
        update_yearly_report()
        update_balance()
        dialog.destroy()
        messagebox.showinfo("Success", "Salary updated")

    tk.Button(dialog, text="Save Changes", command=save_edit, 
             bg=settings["btn_green"], fg='white', 
             font=("Arial", 11)).grid(row=3, column=0, columnspan=2, pady=20)


# Savings Tab 

frame_savings = tk.Frame(notebook, bg=settings["bg_color"])
notebook.add(frame_savings, text="🏦 Savings")

savings_form = tk.Frame(frame_savings, bg=settings["bg_color"])
savings_form.pack(pady=10)

tk.Label(savings_form, text="Amount (USD):", bg=settings["bg_color"], 
         font=("Arial", 11)).grid(row=0, column=0, padx=10, pady=5)
entry_savings = tk.Entry(savings_form, width=20, font=("Arial", 11))
entry_savings.grid(row=0, column=1, padx=10, pady=5)

def add_savings():
    """Add savings entry"""
    amount = convert_to_number(entry_savings.get())
    if amount == 0:
        messagebox.showerror("Error", "Please enter a valid amount")
        return

    selected_date = select_date("Select Savings Date")
    if selected_date is None:
        return

    data["savings"].append({"amount": amount, "date": selected_date})
    balance = get_current_month_balance() - amount
    set_current_month_balance(balance)
    save_data(data)

    entry_savings.delete(0, tk.END)
    update_savings_list()
    update_yearly_report()
    update_balance()
    messagebox.showinfo("Success", f"Savings recorded for {selected_date}")

tk.Button(savings_form, text="Add Savings", command=add_savings, 
          bg=settings["btn_green"], fg='white', 
          font=("Arial", 11)).grid(row=0, column=2, padx=10, pady=5)

columns_savings = ("Date", "Amount (USD)")
tree_savings = ttk.Treeview(frame_savings, columns=columns_savings, show="headings", height=8)
for col in columns_savings:
    tree_savings.heading(col, text=col)
tree_savings.column("Date", width=150, anchor="center")
tree_savings.column("Amount (USD)", width=150, anchor="center")
tree_savings.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

total_savings_frame = tk.Frame(frame_savings, bg=settings["bg_color"])
total_savings_frame.pack(fill=tk.X, padx=10, pady=5)
lbl_total_savings = tk.Label(total_savings_frame, text="", bg=settings["bg_color"], 
                             font=("Arial", 12, "bold"), fg=settings["btn_green"])
lbl_total_savings.pack()

savings_btn_frame = tk.Frame(frame_savings, bg=settings["bg_color"])
savings_btn_frame.pack(pady=5)
tk.Button(savings_btn_frame, text="✏️ Edit Row", command=lambda: edit_selected_savings(),
          bg=settings["btn_orange"], fg='white', font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
tk.Button(savings_btn_frame, text="🗑 Delete Row",
          command=lambda: deleted_selected(tree_savings, data["savings"], "savings"),
          bg=settings["btn_red"], fg='white', font=("Arial", 10)).pack(side=tk.LEFT, padx=5)

def update_savings_list():
    """Refresh the savings list with current filter"""
    for row in tree_savings.get_children():
        tree_savings.delete(row)

    start_date, end_date = get_selected_date_range()
    filtered = [s for s in data["savings"] if _in_range(s["date"], start_date, end_date)]
    filtered.sort(key=lambda x: x["date"], reverse=True)

    total = sum(s["amount"] for s in filtered)
    for s in filtered:
        tree_savings.insert("", tk.END, values=(s["date"], f"${s['amount']:,}"))
    lbl_total_savings.config(text=f"Total Savings: ${total:,}")

def edit_selected_savings():
    """Edit the selected savings entry"""
    selected = tree_savings.selection()
    if not selected:
        messagebox.showerror("Error", "Please select a row")
        return
    item = tree_savings.item(selected[0])
    values = item['values']
    index = tree_savings.index(selected[0])
    actual_index = -(index + 1)

    dialog = tk.Toplevel(root)
    dialog.title("Edit Savings")
    dialog.geometry("350x200")
    dialog.configure(bg=settings["bg_color"])
    dialog.transient(root)
    dialog.grab_set()

    tk.Label(dialog, text="Amount (USD):", bg=settings["bg_color"], 
            font=("Arial", 11)).grid(row=0, column=0, padx=10, pady=10, sticky='e')
    entry_edit_amount = tk.Entry(dialog, width=20, font=("Arial", 11))
    entry_edit_amount.insert(0, values[1].replace("$", "").replace(",", ""))
    entry_edit_amount.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(dialog, text="Date:", bg=settings["bg_color"], 
            font=("Arial", 11)).grid(row=1, column=0, padx=10, pady=10, sticky='e')
    entry_edit_date = tk.Entry(dialog, width=20, font=("Arial", 11))
    entry_edit_date.insert(0, values[0])
    entry_edit_date.grid(row=1, column=1, padx=10, pady=10)

    def save_edit():
        new_amount = convert_to_number(entry_edit_amount.get())
        new_date = entry_edit_date.get().strip()
        old_amount = data["savings"][actual_index]["amount"]
        data["savings"][actual_index] = {"amount": new_amount, "date": new_date}

        balance = get_current_month_balance() + old_amount - new_amount
        set_current_month_balance(balance)
        save_data(data)

        update_savings_list()
        update_yearly_report()
        update_balance()
        dialog.destroy()
        messagebox.showinfo("Success", "Savings updated")

    tk.Button(dialog, text="Save Changes", command=save_edit, 
             bg=settings["btn_green"], fg='white', 
             font=("Arial", 11)).grid(row=2, column=0, columnspan=2, pady=20)


# Charity Tab

frame_charity = tk.Frame(notebook, bg=settings["bg_color"])
notebook.add(frame_charity, text="🤝 Charity")

charity_form = tk.Frame(frame_charity, bg=settings["bg_color"])
charity_form.pack(pady=10)

tk.Label(charity_form, text="Charity Name:", bg=settings["bg_color"], 
         font=("Arial", 11)).grid(row=0, column=0, padx=10, pady=5)
entry_charity_name = tk.Entry(charity_form, width=30, font=("Arial", 11))
entry_charity_name.grid(row=0, column=1, padx=10, pady=5)

tk.Label(charity_form, text="Amount (USD):", bg=settings["bg_color"], 
         font=("Arial", 11)).grid(row=0, column=2, padx=10, pady=5)
entry_charity_amount = tk.Entry(charity_form, width=20, font=("Arial", 11))
entry_charity_amount.grid(row=0, column=3, padx=10, pady=5)

def add_charity():
    """Add charity donation"""
    name = entry_charity_name.get().strip()
    if not name:
        messagebox.showerror("Error", "Please enter a charity name")
        return
    amount = convert_to_number(entry_charity_amount.get())

    selected_date = select_date("Select Charity Date")
    if selected_date is None:
        return

    data["charity"].append({"name": name, "amount": amount, "date": selected_date})
    balance = get_current_month_balance() - amount
    set_current_month_balance(balance)
    save_data(data)

    entry_charity_name.delete(0, tk.END)
    entry_charity_amount.delete(0, tk.END)
    update_charity_list()
    update_yearly_report()
    update_balance()
    messagebox.showinfo("Success", f"Charity recorded for {selected_date}")

tk.Button(charity_form, text="➕ Add Charity", command=add_charity, 
          bg=settings["btn_red"], fg='white', 
          font=("Arial", 11)).grid(row=1, column=0, columnspan=4, pady=10)

columns_charity = ("Date", "Charity Name", "Amount (USD)")
tree_charity = ttk.Treeview(frame_charity, columns=columns_charity, show="headings", height=8)
for col in columns_charity:
    tree_charity.heading(col, text=col)
tree_charity.column("Date", width=100)
tree_charity.column("Charity Name", width=250)
tree_charity.column("Amount (USD)", width=150)
tree_charity.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

total_charity_frame = tk.Frame(frame_charity, bg=settings["bg_color"])
total_charity_frame.pack(fill=tk.X, padx=10, pady=5)
lbl_total_charity = tk.Label(total_charity_frame, text="", bg=settings["bg_color"], 
                             font=("Arial", 12, "bold"), fg=settings["btn_red"])
lbl_total_charity.pack()

charity_btn_frame = tk.Frame(frame_charity, bg=settings["bg_color"])
charity_btn_frame.pack(pady=5)
tk.Button(charity_btn_frame, text="✏️ Edit Row", command=lambda: edit_selected_charity(),
          bg=settings["btn_orange"], fg='white', font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
tk.Button(charity_btn_frame, text="🗑 Delete Row",
          command=lambda: deleted_selected(tree_charity, data["charity"], "charity"),
          bg=settings["btn_red"], fg='white', font=("Arial", 10)).pack(side=tk.LEFT, padx=5)

def update_charity_list():
    """Refresh the charity list with current filter"""
    for row in tree_charity.get_children():
        tree_charity.delete(row)

    start_date, end_date = get_selected_date_range()
    filtered = [c for c in data["charity"] if _in_range(c["date"], start_date, end_date)]
    filtered.sort(key=lambda x: x["date"], reverse=True)

    total = sum(c["amount"] for c in filtered)
    for c in filtered:
        tree_charity.insert("", tk.END, values=(c["date"], c["name"], f"${c['amount']:,}"))
    lbl_total_charity.config(text=f"Total Charity: ${total:,}")

def edit_selected_charity():
    """Edit the selected charity entry"""
    selected = tree_charity.selection()
    if not selected:
        messagebox.showerror("Error", "Please select a row")
        return
    item = tree_charity.item(selected[0])
    values = item['values']
    index = tree_charity.index(selected[0])
    actual_index = -(index + 1)

    dialog = tk.Toplevel(root)
    dialog.title("Edit Charity")
    dialog.geometry("400x250")
    dialog.configure(bg=settings["bg_color"])
    dialog.transient(root)
    dialog.grab_set()

    tk.Label(dialog, text="Charity Name:", bg=settings["bg_color"], 
            font=("Arial", 11)).grid(row=0, column=0, padx=10, pady=10, sticky='e')
    entry_edit_name = tk.Entry(dialog, width=30, font=("Arial", 11))
    entry_edit_name.insert(0, values[1])
    entry_edit_name.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(dialog, text="Amount (USD):", bg=settings["bg_color"], 
            font=("Arial", 11)).grid(row=1, column=0, padx=10, pady=10, sticky='e')
    entry_edit_amount = tk.Entry(dialog, width=20, font=("Arial", 11))
    entry_edit_amount.insert(0, values[2].replace("$", "").replace(",", ""))
    entry_edit_amount.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(dialog, text="Date:", bg=settings["bg_color"], 
            font=("Arial", 11)).grid(row=2, column=0, padx=10, pady=10, sticky='e')
    entry_edit_date = tk.Entry(dialog, width=20, font=("Arial", 11))
    entry_edit_date.insert(0, values[0])
    entry_edit_date.grid(row=2, column=1, padx=10, pady=10)

    def save_edit():
        new_name = entry_edit_name.get().strip()
        if not new_name:
            messagebox.showerror("Error", "Please enter a charity name")
            return
        new_amount = convert_to_number(entry_edit_amount.get())
        new_date = entry_edit_date.get().strip()
        old_amount = data["charity"][actual_index]["amount"]
        data["charity"][actual_index] = {"name": new_name, "amount": new_amount, "date": new_date}

        balance = get_current_month_balance() + old_amount - new_amount
        set_current_month_balance(balance)
        save_data(data)

        update_charity_list()
        update_yearly_report()
        update_balance()
        dialog.destroy()
        messagebox.showinfo("Success", "Charity updated")

    tk.Button(dialog, text="Save Changes", command=save_edit, 
             bg=settings["btn_green"], fg='white', 
             font=("Arial", 11)).grid(row=3, column=0, columnspan=2, pady=20)

# Debt & Claim

frame_dc = tk.Frame(notebook, bg=settings["bg_color"])
notebook.add(frame_dc, text="💰 Debt & Claim")

dc_form = tk.Frame(frame_dc, bg=settings["bg_color"])
dc_form.pack(pady=10)

tk.Label(dc_form, text="Type:", bg=settings["bg_color"], 
         font=("Arial", 11)).grid(row=0, column=0, padx=10, pady=5)
dc_type_var = tk.StringVar(value="Debt")
ttk.Combobox(dc_form, textvariable=dc_type_var, values=["Debt", "Claim"], 
             width=10).grid(row=0, column=1, padx=10, pady=5)

tk.Label(dc_form, text="Person Name:", bg=settings["bg_color"], 
         font=("Arial", 11)).grid(row=0, column=2, padx=10, pady=5)
entry_person = tk.Entry(dc_form, width=20, font=("Arial", 11))
entry_person.grid(row=0, column=3, padx=10, pady=5)

tk.Label(dc_form, text="Amount (USD):", bg=settings["bg_color"], 
         font=("Arial", 11)).grid(row=1, column=0, padx=10, pady=5)
entry_dc_amount = tk.Entry(dc_form, width=20, font=("Arial", 11))
entry_dc_amount.grid(row=1, column=1, padx=10, pady=5)

tk.Label(dc_form, text="Description:", bg=settings["bg_color"], 
         font=("Arial", 11)).grid(row=1, column=2, padx=10, pady=5)
entry_desc = tk.Entry(dc_form, width=30, font=("Arial", 11))
entry_desc.grid(row=1, column=3, padx=10, pady=5)

def add_debt_claim():
    """Add a debt or claim"""
    person = entry_person.get().strip()
    if not person:
        messagebox.showerror("Error", "Please enter a person name")
        return
    amount = convert_to_number(entry_dc_amount.get())

    selected_date = select_date("Select Debt/Claim Date")
    if selected_date is None:
        return

    data["debt_claim"].append({
        "type": dc_type_var.get(),
        "person": person,
        "amount": amount,
        "description": entry_desc.get().strip(),
        "date": selected_date,
        "settled": False
    })
    save_data(data)

    entry_person.delete(0, tk.END)
    entry_dc_amount.delete(0, tk.END)
    entry_desc.delete(0, tk.END)
    update_debt_claim_list()
    messagebox.showinfo("Success", f"{dc_type_var.get()} recorded for {selected_date}. Will deduct from balance when settled.")

tk.Button(dc_form, text="➕ Add", command=add_debt_claim, 
          bg=settings["btn_purple"], fg='white', 
          font=("Arial", 11)).grid(row=2, column=0, columnspan=4, pady=10)

columns_dc = ("Date", "Type", "Person", "Amount (USD)", "Description", "Settled")
tree_dc = ttk.Treeview(frame_dc, columns=columns_dc, show="headings", height=8)
for col in columns_dc:
    tree_dc.heading(col, text=col)
tree_dc.column("Date", width=100, anchor="center")
tree_dc.column("Type", width=80, anchor="center")
tree_dc.column("Person", width=120, anchor="center")
tree_dc.column("Amount (USD)", width=120, anchor="center")
tree_dc.column("Description", width=180, anchor="center")
tree_dc.column("Settled", width=80, anchor="center")
tree_dc.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

total_dc_frame = tk.Frame(frame_dc, bg=settings["bg_color"])
total_dc_frame.pack(fill=tk.X, padx=10, pady=5)
lbl_total_debt = tk.Label(total_dc_frame, text="", bg=settings["bg_color"], 
                          font=("Arial", 11, "bold"), fg=settings["btn_red"])
lbl_total_debt.pack(side=tk.LEFT, padx=10)
lbl_total_claim = tk.Label(total_dc_frame, text="", bg=settings["bg_color"], 
                           font=("Arial", 11, "bold"), fg=settings["btn_green"])
lbl_total_claim.pack(side=tk.LEFT, padx=10)

dc_btn_frame = tk.Frame(frame_dc, bg=settings["bg_color"])
dc_btn_frame.pack(pady=5)
tk.Button(dc_btn_frame, text="✏️ Edit Row", command=lambda: edit_selected_dc(),
          bg=settings["btn_orange"], fg='white', font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
tk.Button(dc_btn_frame, text="🗑 Delete Row",
          command=lambda: deleted_selected(tree_dc, data["debt_claim"], None),
          bg=settings["btn_red"], fg='white', font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
tk.Button(dc_btn_frame, text="✅ Settle Debt", command=lambda: toggle_settle_debt(tree_dc),
          bg=settings["btn_green"], fg='white', font=("Arial", 10)).pack(side=tk.LEFT, padx=5)

def toggle_settle_debt(tree):
    """Settle a debt and deduct from balance"""
    selected = tree.selection()
    if not selected:
        messagebox.showerror("Error", "Please select a row")
        return

    index = tree.index(selected[0])
    actual_index = -(index + 1)
    current = data["debt_claim"][actual_index]

    if current["type"] == "Claim":
        messagebox.showwarning("Not Allowed", "This is a claim, only debts can be settled.")
        return

    if not current["settled"]:
        current["settled"] = True
        balance = get_current_month_balance() - current["amount"]
        set_current_month_balance(balance)
        save_data(data)
        update_debt_claim_list()
        update_balance()
        messagebox.showinfo("Settled", f"Debt of {current['person']} for ${current['amount']:,} settled.")
    else:
        messagebox.showwarning("Already Settled", "This debt has already been settled.")

def update_debt_claim_list():
    """Refresh the debt/claim list with current filter"""
    for row in tree_dc.get_children():
        tree_dc.delete(row)

    start_date, end_date = get_selected_date_range()
    filtered = [i for i in data["debt_claim"] if _in_range(i["date"], start_date, end_date)]
    filtered.sort(key=lambda x: x["date"], reverse=True)

    total_debt = sum(i["amount"] for i in filtered if i["type"] == "Debt")
    total_claim = sum(i["amount"] for i in filtered if i["type"] == "Claim")

    for item in filtered:
        settled_text = "✅" if item.get("settled", False) else "❌"
        tree_dc.insert("", tk.END, values=(
            item["date"], item["type"], item["person"],
            f"${item['amount']:,}", item.get("description", ""), settled_text
        ))
    lbl_total_debt.config(text=f"Total Debt: ${total_debt:,}")
    lbl_total_claim.config(text=f"Total Claim: ${total_claim:,}")

def edit_selected_dc():
    """Edit the selected debt/claim entry"""
    selected = tree_dc.selection()
    if not selected:
        messagebox.showerror("Error", "Please select a row")
        return
    item = tree_dc.item(selected[0])
    values = item['values']
    index = tree_dc.index(selected[0])
    actual_index = -(index + 1)

    dialog = tk.Toplevel(root)
    dialog.title("Edit Entry")
    dialog.geometry("450x300")
    dialog.configure(bg=settings["bg_color"])
    dialog.transient(root)
    dialog.grab_set()

    tk.Label(dialog, text="Type:", bg=settings["bg_color"], 
            font=("Arial", 11)).grid(row=0, column=0, padx=10, pady=10, sticky='e')
    type_var = tk.StringVar(value=values[1])
    ttk.Combobox(dialog, textvariable=type_var, values=["Debt", "Claim"], 
                 width=15).grid(row=0, column=1, padx=10, pady=10)

    tk.Label(dialog, text="Person Name:", bg=settings["bg_color"], 
            font=("Arial", 11)).grid(row=1, column=0, padx=10, pady=10, sticky='e')
    entry_edit_person = tk.Entry(dialog, width=25, font=("Arial", 11))
    entry_edit_person.insert(0, values[2])
    entry_edit_person.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(dialog, text="Amount (USD):", bg=settings["bg_color"], 
            font=("Arial", 11)).grid(row=2, column=0, padx=10, pady=10, sticky='e')
    entry_edit_amount = tk.Entry(dialog, width=20, font=("Arial", 11))
    entry_edit_amount.insert(0, values[3].replace("$", "").replace(",", ""))
    entry_edit_amount.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(dialog, text="Description:", bg=settings["bg_color"], 
            font=("Arial", 11)).grid(row=3, column=0, padx=10, pady=10, sticky='e')
    entry_edit_desc = tk.Entry(dialog, width=30, font=("Arial", 11))
    entry_edit_desc.insert(0, values[4])
    entry_edit_desc.grid(row=3, column=1, padx=10, pady=10)

    tk.Label(dialog, text="Date:", bg=settings["bg_color"], 
            font=("Arial", 11)).grid(row=4, column=0, padx=10, pady=10, sticky='e')
    entry_edit_date = tk.Entry(dialog, width=20, font=("Arial", 11))
    entry_edit_date.insert(0, values[0])
    entry_edit_date.grid(row=4, column=1, padx=10, pady=10)

    def save_edit():
        data["debt_claim"][actual_index] = {
            "type": type_var.get(),
            "person": entry_edit_person.get().strip(),
            "amount": convert_to_number(entry_edit_amount.get()),
            "description": entry_edit_desc.get().strip(),
            "date": entry_edit_date.get().strip(),
            "settled": data["debt_claim"][actual_index].get("settled", False)
        }
        save_data(data)
        update_debt_claim_list()
        update_balance()
        dialog.destroy()
        messagebox.showinfo("Success", "Entry updated")

    tk.Button(dialog, text="Save Changes", command=save_edit, 
             bg=settings["btn_green"], fg='white', 
             font=("Arial", 11)).grid(row=5, column=0, columnspan=2, pady=20)


# Installments Tab 
 
frame_installment = tk.Frame(notebook, bg=settings["bg_color"])
notebook.add(frame_installment, text="📅 Installments")

installment_form = tk.Frame(frame_installment, bg=settings["bg_color"])
installment_form.pack(pady=10)

tk.Label(installment_form, text="Installment Title:", bg=settings["bg_color"], 
         font=("Arial", 11)).grid(row=0, column=0, padx=10, pady=5)
entry_installment_title = tk.Entry(installment_form, width=25, font=("Arial", 11))
entry_installment_title.grid(row=0, column=1, padx=10, pady=5)

tk.Label(installment_form, text="Amount (USD):", bg=settings["bg_color"], 
         font=("Arial", 11)).grid(row=0, column=2, padx=10, pady=5)
entry_installment_amount = tk.Entry(installment_form, width=15, font=("Arial", 11))
entry_installment_amount.grid(row=0, column=3, padx=10, pady=5)

tk.Label(installment_form, text="Due Date:", bg=settings["bg_color"], 
         font=("Arial", 11)).grid(row=1, column=0, padx=10, pady=5)
tk.Label(installment_form, text="Day:", bg=settings["bg_color"]).grid(row=1, column=1, padx=5, sticky='e')
installment_day = ttk.Combobox(installment_form, values=[f"{i:02d}" for i in range(1, 32)], width=5)
installment_day.set(datetime.date.today().strftime("%d"))
installment_day.grid(row=1, column=1, padx=40, pady=5)

tk.Label(installment_form, text="Month:", bg=settings["bg_color"]).grid(row=1, column=2, padx=5, sticky='e')
installment_month = ttk.Combobox(installment_form, values=GREGORIAN_MONTHS, width=8)
installment_month.set(current_month)
installment_month.grid(row=1, column=2, padx=40, pady=5)

tk.Label(installment_form, text="Year:", bg=settings["bg_color"]).grid(row=1, column=3, padx=5, sticky='e')
installment_year = ttk.Combobox(installment_form, values=[str(i) for i in range(2020, 2035)], width=6)
installment_year.set(str(datetime.date.today().year))
installment_year.grid(row=1, column=3, padx=40, pady=5)

def update_installments_list():
    """Refresh the installments list with current filter"""
    for row in tree_installment.get_children():
        tree_installment.delete(row)

    start_date, end_date = get_selected_date_range()
    for inst in data["installments"]:
        if not _in_range(inst["due_date"], start_date, end_date):
            continue
        status = "Paid ✅" if inst["is_paid"] else "Unpaid ❌"
        paid_date = inst["paid_date"] if inst["paid_date"] else "---"
        tree_installment.insert("", tk.END, values=(
            inst["title"], f"${inst['amount']:,}", inst["due_date"], status, paid_date
        ))

def _get_selected_installment():
    """Get the selected installment data"""
    selected = tree_installment.selection()
    if not selected:
        return None, None
    values = tree_installment.item(selected[0])["values"]
    due_date_in_row = values[2]
    title_in_row = values[0]
    for i, inst in enumerate(data["installments"]):
        if inst["title"] == title_in_row and inst["due_date"] == due_date_in_row:
            return i, inst
    return None, None

def add_installment():
    """Add a new installment"""
    title = entry_installment_title.get().strip()
    if not title:
        messagebox.showerror("Error", "Please enter an installment title")
        return
    amount = convert_to_number(entry_installment_amount.get())
    if amount == 0:
        messagebox.showerror("Error", "Please enter a valid amount")
        return

    year = int(installment_year.get())
    month_name = installment_month.get()
    month_num = MONTHS_MAP[month_name]
    day = int(installment_day.get())

    try:
        due_date_str = datetime.date(year, month_num, day).strftime("%Y/%m/%d")
    except:
        messagebox.showerror("Error", "Invalid date")
        return

    data["installments"].append({
        "title": title, "amount": amount, "due_date": due_date_str, 
        "is_paid": False, "paid_date": None
    })
    save_data(data)
    entry_installment_title.delete(0, tk.END)
    entry_installment_amount.delete(0, tk.END)
    update_installments_list()
    messagebox.showinfo("Success", f"Installment '{title}' for ${amount:,} due on {due_date_str} recorded")

def mark_installment_paid():
    """Mark an installment as paid"""
    selected = tree_installment.selection()
    if not selected:
        messagebox.showerror("Error", "Please select an installment")
        return

    real_index, inst = _get_selected_installment()
    if real_index is None:
        return

    if inst["is_paid"]:
        messagebox.showwarning("Already Paid", "This installment is already paid")
        return

    inst["is_paid"] = True
    inst["paid_date"] = get_today_date()

    balance = get_current_month_balance() - inst["amount"]
    set_current_month_balance(balance)
    save_data(data)

    update_installments_list()
    update_balance()
    messagebox.showinfo("Success", f"Installment '{inst['title']}' for ${inst['amount']:,} marked as paid")

def delete_installment():
    """Delete the selected installment"""
    selected = tree_installment.selection()
    if not selected:
        messagebox.showerror("Error", "Please select an installment")
        return
    if messagebox.askyesno("Confirm", "Are you sure you want to delete this installment?"):
        real_index, inst = _get_selected_installment()
        if real_index is None:
            return
        del data["installments"][real_index]
        save_data(data)
        update_installments_list()

tk.Button(installment_form, text="➕ Add Installment", command=add_installment,
          bg=settings["btn_purple"], fg='white', 
          font=("Arial", 11), padx=20, pady=5).grid(row=2, column=0, columnspan=4, pady=10)

columns_installment = ("Title", "Amount", "Due Date", "Status", "Payment Date")
tree_installment = ttk.Treeview(frame_installment, columns=columns_installment, show="headings", height=10)
for col in columns_installment:
    tree_installment.heading(col, text=col)
tree_installment.column("Title", width=200, anchor="center")
tree_installment.column("Amount", width=120, anchor="center")
tree_installment.column("Due Date", width=120, anchor="center")
tree_installment.column("Status", width=120, anchor="center")
tree_installment.column("Payment Date", width=120, anchor="center")
tree_installment.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

inst_btn_frame = tk.Frame(frame_installment, bg=settings["bg_color"])
inst_btn_frame.pack(pady=5)
tk.Button(inst_btn_frame, text="✅ Mark Paid", command=mark_installment_paid,
          bg=settings["btn_green"], fg='white', font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
tk.Button(inst_btn_frame, text="🗑 Delete", command=delete_installment,
          bg=settings["btn_red"], fg='white', font=("Arial", 10)).pack(side=tk.LEFT, padx=5)


# Note Tab 

frame_notes = tk.Frame(notebook, bg=settings["bg_color"])
notebook.add(frame_notes, text="📝 Notes")

notes_header = tk.Frame(frame_notes, bg=settings["bg_color"])
notes_header.pack(fill=tk.X, padx=10, pady=5)

lbl_notes_month = tk.Label(notes_header, text="", bg=settings["bg_color"],
                            font=("Arial", 12, "bold"), fg=settings["btn_blue"])
lbl_notes_month.pack(side=tk.LEFT, padx=5)

notes_text = tk.Text(frame_notes, font=("Arial", 12), bg=settings["table_bg"],
                     wrap=tk.WORD, padx=10, pady=10)
notes_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

notes_btn_frame = tk.Frame(frame_notes, bg=settings["bg_color"])
notes_btn_frame.pack(pady=5)

def save_notes():
    """Save notes for the current month"""
    key = get_month_key()
    content = notes_text.get("1.0", tk.END).rstrip()
    if content:
        data["notes"][key] = content
    elif key in data["notes"]:
        del data["notes"][key]
    save_data(data)
    messagebox.showinfo("Success", "Notes saved")

def update_notes():
    """Load notes for the current month"""
    key = get_month_key()
    notes_text.delete("1.0", tk.END)
    content = data["notes"].get(key, "")
    if content:
        notes_text.insert("1.0", content)
    month_label = f"Notes for {filter_month.get()} {filter_year.get()}"
    lbl_notes_month.config(text=month_label)

tk.Button(notes_btn_frame, text="💾 Save Notes", command=save_notes,
          bg=settings["btn_blue"], fg='white', 
          font=("Arial", 11), padx=20, pady=5).pack(side=tk.LEFT, padx=5)
tk.Button(notes_btn_frame, text="🗑 Clear", command=lambda: notes_text.delete("1.0", tk.END),
          bg=settings["btn_red"], fg='white', 
          font=("Arial", 10), padx=15, pady=5).pack(side=tk.LEFT, padx=5)

tk.Label(frame_notes, text="💡 Notes are saved separately for each month",
         bg=settings["bg_color"], font=("Arial", 9, "italic"), fg="gray").pack(pady=3)


# Yearly Report Tab 

frame_yearly = tk.Frame(notebook, bg=settings["bg_color"])
notebook.add(frame_yearly, text="📊 Yearly Report")

tree_yearly = ttk.Treeview(frame_yearly, columns=("Month", "Total Expense", "Total Salary", "Total Savings"), 
                           show="headings", height=10)
tree_yearly.heading("Month", text="Month")
tree_yearly.heading("Total Expense", text="Total Expense (USD)")
tree_yearly.heading("Total Salary", text="Total Salary (USD)")
tree_yearly.heading("Total Savings", text="Total Savings (USD)")
tree_yearly.column("Month", width=120, anchor="center")
tree_yearly.column("Total Expense", width=180, anchor="center")
tree_yearly.column("Total Salary", width=180, anchor="center")
tree_yearly.column("Total Savings", width=180, anchor="center")
tree_yearly.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

def update_yearly_report():
    """Generate and display the yearly report"""
    for row in tree_yearly.get_children():
        tree_yearly.delete(row)

    year = int(filter_year.get())
    for month_num, month_name in enumerate(GREGORIAN_MONTHS, start=1):
        start_date = datetime.date(year, month_num, 1)
        end_date = datetime.date(year, month_num, get_last_day_of_month(year, month_num))

        total_expense = sum(t["amount"] for t in data["transactions"] if _in_range(t["date"], start_date, end_date))
        total_salary = sum(s["amount"] for s in data["salary"] if _in_range(s["date"], start_date, end_date))
        total_savings = sum(sv["amount"] for sv in data["savings"] if _in_range(sv["date"], start_date, end_date))

        tree_yearly.insert("", tk.END, values=(
            month_name, f"${total_expense:,}", f"${total_salary:,}", f"${total_savings:,}"
        ))

tk.Button(frame_yearly, text="🔄 Refresh Yearly Report", command=update_yearly_report,
          bg=settings["btn_blue"], fg='white', font=("Arial", 11)).pack(pady=5)


# Settings Tab
 
frame_settings = tk.Frame(notebook, bg=settings["bg_color"])
notebook.add(frame_settings, text="⚙️ Settings")

settings_frame = tk.Frame(frame_settings, bg=settings["bg_color"])
settings_frame.pack(pady=20, padx=20, anchor="center")

# Auto date setting
auto_date_var = tk.BooleanVar(value=settings["auto_date"])
tk.Checkbutton(settings_frame, text="Auto-fill Today's Date", variable=auto_date_var, 
               bg=settings["bg_color"], font=("Arial", 11)).grid(row=0, column=0, columnspan=2, pady=10, sticky='w')

def toggle_auto_date():
    settings["auto_date"] = auto_date_var.get()
    save_settings(settings)
    messagebox.showinfo("Settings", "Settings saved")

tk.Button(settings_frame, text="Save Date Settings", command=toggle_auto_date, 
          bg=settings["btn_green"], fg='white').grid(row=1, column=0, columnspan=2, pady=10)

# Salary to balance setting
add_salary_var = tk.BooleanVar(value=settings["add_salary_to_balance"])
tk.Checkbutton(settings_frame, text="Add salary to balance and deduct expenses from balance",
               variable=add_salary_var, bg=settings["bg_color"], 
               font=("Arial", 11)).grid(row=2, column=0, columnspan=2, pady=10, sticky='w')

def toggle_add_salary():
    settings["add_salary_to_balance"] = add_salary_var.get()
    save_settings(settings)
    messagebox.showinfo("Settings", "Settings saved")

tk.Button(settings_frame, text="Save Balance Settings", command=toggle_add_salary, 
          bg=settings["btn_green"], fg='white').grid(row=3, column=0, columnspan=2, pady=10)

# Color Customization
def change_bg_color():
    color = colorchooser.askcolor(title="Choose Background Color")[1]
    if color:
        settings["bg_color"] = color
        save_settings(settings)
        messagebox.showinfo("Settings", "Restart the application for changes to take effect")

tk.Button(settings_frame, text="Change Background Color", command=change_bg_color, 
          bg=settings["btn_orange"], fg='white').grid(row=4, column=0, pady=10, padx=5)

def change_table_color():
    color = colorchooser.askcolor(title="Choose Table Color")[1]
    if color:
        settings["table_bg"] = color
        save_settings(settings)
        messagebox.showinfo("Settings", "Restart the application for changes to take effect")

tk.Button(settings_frame, text="Change Table Color", command=change_table_color, 
          bg=settings["btn_blue"], fg='white').grid(row=4, column=1, pady=10, padx=5)

# Password management
tk.Button(settings_frame, text="Change Password", command=change_password_dialog,
          bg=settings["btn_purple"], fg='white', 
          font=("Arial", 10), padx=15, pady=5).grid(row=5, column=0, columnspan=2, pady=10)

tk.Button(settings_frame, text="Forgot Password", command=show_forgot_password_dialog,
          bg=settings["btn_red"], fg='white', 
          font=("Arial", 10), padx=15, pady=5).grid(row=6, column=0, columnspan=2, pady=10)

# Delete all Data
def delete_all_data():
    if messagebox.askyesno("Warning", "Are you sure you want to delete all data?"):
        empty = {
            "transactions": [], "salary": [], "savings": [], "charity": [],
            "debt_claim": [], "installments": [], "balance": 0,
            "initial_balance": 0, "monthly_balances": {}, "notes": {}
        }
        data.clear()
        data.update(empty)
        save_data(data)
        for fn in [update_transactions, update_salary_list, update_savings_list, update_charity_list,
                   update_debt_claim_list, update_monthly_report, update_yearly_report,
                   update_installments_list, update_balance, update_notes]:
            fn()
        messagebox.showinfo("Success", "All data deleted")

tk.Button(settings_frame, text="🗑 Delete All Data", command=delete_all_data, 
          bg=settings["btn_red"], fg='white').grid(row=7, column=0, columnspan=2, pady=20)

# Signature
tk.Label(frame_settings, text="Made By A.M.H - ver 2.0", bg=settings["bg_color"],
         font=("Arial", 10, "italic", "bold"), fg="black").pack(side=tk.BOTTOM, pady=10)

# ============================================================
# ============ UTILITY FUNCTIONS ============
# ============================================================

def deleted_selected(tree, data_list, data_type=None):
    """Delete the selected row from any treeview"""
    selected = tree.selection()
    if not selected:
        messagebox.showerror("Error", "Please select a row")
        return
    if messagebox.askyesno("Confirm", "Are you sure you want to delete this row?"):
        index = tree.index(selected[0])
        deleted_item = data_list[-(index + 1)]

        balance = get_current_month_balance()
        if data_type == "transaction":
            balance += deleted_item["amount"]
        elif data_type == "salary":
            balance -= deleted_item["amount"]
        elif data_type == "savings":
            balance += deleted_item["amount"]
        elif data_type == "charity":
            balance += deleted_item["amount"]
        set_current_month_balance(balance)

        del data_list[-(index + 1)]
        save_data(data)

        if tree == tree_trans:
            update_transactions()
            update_monthly_report()
            update_yearly_report()
        elif tree == tree_salary:
            update_salary_list()
        elif tree == tree_savings:
            update_savings_list()
        elif tree == tree_charity:
            update_charity_list()
        elif tree == tree_dc:
            update_debt_claim_list()
        elif tree == tree_installment:
            update_installments_list()

        update_balance()
        messagebox.showinfo("Success", "Row deleted")

# KEYBOARD SHORTCUTS

def on_enter_pressed(event):
    """Handle Enter key press for form submission"""
    current_tab = notebook.index(notebook.select())
    checks = [
        (entry_title, entry_amount, add_transaction),
        (entry_salary_source, entry_salary, add_salary),
        (entry_savings, None, add_savings),
        (entry_charity_name, entry_charity_amount, add_charity),
        (entry_person, entry_dc_amount, add_debt_claim),
        (entry_installment_title, entry_installment_amount, add_installment),
    ]
    if current_tab < len(checks):
        first, second, fn = checks[current_tab]
        if first.get().strip() and (second is None or second.get().strip()):
            fn()
        else:
            messagebox.showwarning("Error", "Please fill in all required fields")

root.bind("<Return>", on_enter_pressed)


# ============ INITIALIZATION ============


# Ensure all required fields exist
if "installments" not in data:
    data["installments"] = []
if "monthly_balances" not in data:
    data["monthly_balances"] = {}
if "notes" not in data:
    data["notes"] = {}
save_data(data)

# Initialize all views
update_transactions()
update_salary_list()
update_savings_list()
update_charity_list()
update_debt_claim_list()
update_monthly_report()
update_yearly_report()
update_installments_list()
update_notes()
update_balance()

# Start the application
if __name__ == "__main__":
    root.mainloop()