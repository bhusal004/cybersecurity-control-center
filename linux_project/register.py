import tkinter as tk
from tkinter import ttk, messagebox

from database import conn, cursor


# ---------------- COLORS ----------------

BG_COLOR = "#1e293b"
PRIMARY_COLOR = "#2563eb"
PRIMARY_HOVER = "#1d4ed8"
TEXT_COLOR = "#f1f5f9"
ENTRY_BG = "#334155"
ENTRY_FG = "#ffffff"


# ---------------- WINDOW ----------------

window = tk.Tk()
window.title("Registration Form")
window.geometry("500x680")
window.configure(bg=BG_COLOR)


# ---------------- TTK STYLE FOR COMBOBOX ----------------

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Custom.TCombobox",
    fieldbackground=ENTRY_BG,
    background=ENTRY_BG,
    foreground=ENTRY_FG,
    arrowcolor=TEXT_COLOR,
    bordercolor=ENTRY_BG,
    lightcolor=ENTRY_BG,
    darkcolor=ENTRY_BG,
    padding=5
)

style.map(
    "Custom.TCombobox",
    fieldbackground=[("readonly", ENTRY_BG)],
    foreground=[("readonly", ENTRY_FG)],
    background=[("readonly", ENTRY_BG)]
)

# Fix dropdown list colors
window.option_add("*TCombobox*Listbox.background", ENTRY_BG)
window.option_add("*TCombobox*Listbox.foreground", ENTRY_FG)
window.option_add("*TCombobox*Listbox.selectBackground", PRIMARY_COLOR)
window.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")


# ---------------- HELPER: STYLED BUTTON WITH HOVER ----------------

def make_button(parent, text, command, bg=PRIMARY_COLOR, hover=PRIMARY_HOVER, width=15):

    btn = tk.Button(
        parent,
        text=text,
        command=command,
        width=width,
        font=("Segoe UI", 11, "bold"),
        bg=bg,
        fg="white",
        activebackground=hover,
        activeforeground="white",
        relief="flat",
        bd=0,
        cursor="hand2",
        padx=6,
        pady=6
    )

    btn.bind("<Enter>", lambda e: btn.config(bg=hover))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))

    return btn


def make_entry(parent, width=30, show=None):

    kwargs = dict(
        width=width,
        font=("Segoe UI", 11),
        bg=ENTRY_BG,
        fg=ENTRY_FG,
        insertbackground=ENTRY_FG,
        relief="flat",
        bd=6
    )

    if show:
        kwargs["show"] = show

    return tk.Entry(parent, **kwargs)


def make_label(parent, text):

    return tk.Label(
        parent,
        text=text,
        font=("Segoe UI", 12),
        bg=BG_COLOR,
        fg=TEXT_COLOR
    )


# ---------------- HEADING ----------------

heading = tk.Label(
    window,
    text="📝 Registration Form",
    font=("Segoe UI", 24, "bold"),
    bg=BG_COLOR,
    fg=TEXT_COLOR
)
heading.grid(row=0, column=0, columnspan=2, pady=25)


# ---------------- FORM FRAME ----------------

form = tk.Frame(window, bg=BG_COLOR)
form.grid(row=1, column=0, columnspan=2, padx=30)


# Name
make_label(form, "Name").grid(row=0, column=0, sticky="w", pady=8)
name_entry = make_entry(form)
name_entry.grid(row=0, column=1, sticky="e", pady=8, ipady=3)


# Email
make_label(form, "Email").grid(row=1, column=0, sticky="w", pady=8)
email_entry = make_entry(form)
email_entry.grid(row=1, column=1, sticky="e", pady=8, ipady=3)


# Password
make_label(form, "Password").grid(row=2, column=0, sticky="w", pady=8)
password_entry = make_entry(form, show="*")
password_entry.grid(row=2, column=1, sticky="e", pady=8, ipady=3)


# Phone
make_label(form, "Phone Number").grid(row=3, column=0, sticky="w", pady=8)
phone_entry = make_entry(form)
phone_entry.grid(row=3, column=1, sticky="e", pady=8, ipady=3)


# Course
make_label(form, "Course").grid(row=4, column=0, sticky="w", pady=8)
course_entry = make_entry(form)
course_entry.grid(row=4, column=1, sticky="e", pady=8, ipady=3)


# Gender
make_label(form, "Gender").grid(row=5, column=0, sticky="w", pady=8)

gender_var = tk.StringVar(value="Male")

gender_box = ttk.Combobox(
    form,
    textvariable=gender_var,
    values=["Male", "Female", "Other"],
    width=27,
    state="readonly",
    style="Custom.TCombobox"
)
gender_box.grid(row=5, column=1, sticky="e", pady=8)


# Security Question
make_label(form, "Security Question").grid(row=6, column=0, sticky="w", pady=8)

question_var = tk.StringVar()

question_box = ttk.Combobox(
    form,
    textvariable=question_var,
    values=[
        "What is your favourite color?",
        "What is your pet's name?",
        "What is your favourite food?"
    ],
    width=27,
    state="readonly",
    style="Custom.TCombobox"
)
question_box.grid(row=6, column=1, sticky="e", pady=8)


# Security Answer
make_label(form, "Security Answer").grid(row=7, column=0, sticky="w", pady=8)

answer_entry = make_entry(form)
answer_entry.grid(row=7, column=1, sticky="e", pady=8, ipady=3)


# ---------------- REGISTER FUNCTION ----------------

def register():

    name = name_entry.get().strip()
    email = email_entry.get().strip()
    password = password_entry.get().strip()
    phone = phone_entry.get().strip()
    course = course_entry.get().strip()
    gender = gender_var.get().strip()

    security_question = question_var.get().strip()
    security_answer = answer_entry.get().strip()


    # Check all fields
    if not all([
        name,
        email,
        password,
        phone,
        course,
        gender,
        security_question,
        security_answer
    ]):
        messagebox.showwarning(
            "Warning",
            "Please fill in all fields"
        )
        return


    # Password validation
    if len(password) < 4:
        messagebox.showwarning(
            "Warning",
            "Password should be at least 4 characters"
        )
        return


    # Insert data into database
    query = """
        INSERT INTO register_form
        (
            name,
            email,
            password,
            phone,
            gender,
            course,
            security_question,
            security_answer
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        name,
        email,
        password,
        phone,
        gender,
        course,
        security_question,
        security_answer
    )


    try:

        cursor.execute(query, values)
        conn.commit()

        messagebox.showinfo(
            "Success",
            "Registration successful! You can now login."
        )


        # Clear fields
        name_entry.delete(0, tk.END)
        email_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
        phone_entry.delete(0, tk.END)
        course_entry.delete(0, tk.END)

        gender_var.set("Male")
        question_var.set("")
        answer_entry.delete(0, tk.END)


    except Exception as e:

        messagebox.showerror(
            "Database Error",
            str(e)
        )


# ---------------- REGISTER BUTTON ----------------

register_button = make_button(
    window, "Register", register, width=15
)

register_button.grid(
    row=2,
    column=0,
    columnspan=2,
    pady=25
)


# ---------------- MAIN LOOP ----------------

window.mainloop()
