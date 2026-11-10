import string
import random
import platform
import requests
import subprocess
import tkinter as tk
from tkinter import messagebox

from database import conn, cursor
from dashboard import open_dashboard


# =========================================================
# CONFIG
# =========================================================

API_KEY = "291264d1-a69c-11f1-9cb1-0200cd936042"

# COLORS
BG_COLOR = "#1e293b"        # dark slate background
CARD_COLOR = "#f8fafc"      # light card-like inner area (not used as separate widget, kept simple)
PRIMARY_COLOR = "#2563eb"   # blue accent
PRIMARY_HOVER = "#1d4ed8"
DANGER_COLOR = "#dc2626"
TEXT_COLOR = "#f1f5f9"
ENTRY_BG = "#334155"
ENTRY_FG = "#ffffff"


# =========================================================
# SMS OTP
# =========================================================

def send_otp_sms(phone_number, otp):

    url = f"https://2factor.in/API/V1/{API_KEY}/SMS/{phone_number}/{otp}/OTP1"

    try:
        response = requests.get(url, timeout=10)
        result = response.json()
        return result.get("Status") == "Success", result

    except Exception as e:
        return False, str(e)


# =========================================================
# MAIN WINDOW
# =========================================================

window = tk.Tk()
window.title("Secure Login")
window.geometry("520x650")
window.configure(bg=BG_COLOR)


# =========================================================
# HELPER: STYLED BUTTON WITH HOVER
# =========================================================

def make_button(parent, text, command, bg=PRIMARY_COLOR, hover=PRIMARY_HOVER, width=18):

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


# =========================================================
# CAPTCHA
# =========================================================

def generate_captcha():
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=6))


captcha_code = generate_captcha()


def reload_captcha():
    global captcha_code
    captcha_code = generate_captcha()
    captcha_label.config(text=captcha_code)
    captcha_entry.delete(0, tk.END)


# =========================================================
# INTERNET CHECK
# =========================================================

def check_internet():
    try:
        count_flag = "-n" if platform.system().lower() == "windows" else "-c"
        result = subprocess.run(
            ["ping", count_flag, "1", "8.8.8.8"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


# =========================================================
# VARIABLES
# =========================================================

generated_otp = None
logged_user = None
security_question_from_db = None
phone_number_for_otp = None


# =========================================================
# UI
# =========================================================

heading = tk.Label(
    window,
    text="🔐 Secure Login",
    font=("Segoe UI", 26, "bold"),
    bg=BG_COLOR,
    fg=TEXT_COLOR
)
heading.pack(pady=25)

# EMAIL
tk.Label(
    window, text="Email", font=("Segoe UI", 12), bg=BG_COLOR, fg=TEXT_COLOR
).pack()

email_entry = tk.Entry(
    window, width=35, font=("Segoe UI", 11),
    bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=ENTRY_FG,
    relief="flat", bd=6
)
email_entry.pack(pady=7, ipady=4)

# PASSWORD
tk.Label(
    window, text="Password", font=("Segoe UI", 12), bg=BG_COLOR, fg=TEXT_COLOR
).pack()

password_entry = tk.Entry(
    window, width=35, show="*", font=("Segoe UI", 11),
    bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=ENTRY_FG,
    relief="flat", bd=6
)
password_entry.pack(pady=7, ipady=4)

# CAPTCHA
tk.Label(
    window, text="Enter CAPTCHA", font=("Segoe UI", 12), bg=BG_COLOR, fg=TEXT_COLOR
).pack(pady=(15, 5))

captcha_label = tk.Label(
    window, text=captcha_code, font=("Consolas", 20, "bold"),
    bg=BG_COLOR, fg=PRIMARY_COLOR
)
captcha_label.pack()

captcha_entry = tk.Entry(
    window, width=20, font=("Segoe UI", 11),
    bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=ENTRY_FG,
    relief="flat", bd=6, justify="center"
)
captcha_entry.pack(pady=7, ipady=4)

reload_button = make_button(
    window, "🔄 Reload CAPTCHA", reload_captcha,
    bg="#475569", hover="#64748b", width=20
)
reload_button.pack(pady=5)


# =========================================================
# LOGIN FUNCTION
# =========================================================

def login():
    global logged_user
    global generated_otp
    global security_question_from_db
    global phone_number_for_otp

    email = email_entry.get().strip()
    password = password_entry.get()
    entered_captcha = captcha_entry.get().strip()

    if not email:
        messagebox.showwarning("Warning", "Please enter your email")
        return

    if not password:
        messagebox.showwarning("Warning", "Please enter your password")
        return

    if not entered_captcha:
        messagebox.showwarning("Warning", "Please enter CAPTCHA")
        return

    if entered_captcha.upper() != captcha_code:
        messagebox.showerror("CAPTCHA Error", "Wrong CAPTCHA!")
        reload_captcha()
        return

    query = """
        SELECT
            s_no,
            name,
            email,
            phone,
            security_question,
            security_answer
        FROM register_form
        WHERE email = %s
        AND password = %s
    """

    values = (email, password)

    try:
        cursor.execute(query, values)
        user = cursor.fetchone()

        if not user:
            messagebox.showerror("Login Failed", "Invalid email or password")
            return

        logged_user = user
        phone_number_for_otp = user[3]
        security_question_from_db = user[4]

        open_security_question_window()

    except Exception as e:
        messagebox.showerror("Database Error", str(e))


# =========================================================
# SECURITY QUESTION WINDOW
# =========================================================

def open_security_question_window():

    security_window = tk.Toplevel(window)
    security_window.title("Security Verification")
    security_window.geometry("500x350")
    security_window.configure(bg=BG_COLOR)

    tk.Label(
        security_window,
        text="Security Verification",
        font=("Segoe UI", 20, "bold"),
        bg=BG_COLOR, fg=TEXT_COLOR
    ).pack(pady=25)

    tk.Label(
        security_window,
        text="Your Security Question:",
        font=("Segoe UI", 12),
        bg=BG_COLOR, fg=TEXT_COLOR
    ).pack(pady=10)

    tk.Label(
        security_window,
        text=security_question_from_db,
        font=("Segoe UI", 13, "bold"),
        wraplength=420,
        bg=BG_COLOR, fg=PRIMARY_COLOR
    ).pack(pady=10)

    tk.Label(
        security_window,
        text="Enter your answer:",
        font=("Segoe UI", 12),
        bg=BG_COLOR, fg=TEXT_COLOR
    ).pack(pady=5)

    answer_entry = tk.Entry(
        security_window, width=35, font=("Segoe UI", 11),
        bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=ENTRY_FG,
        relief="flat", bd=6
    )
    answer_entry.pack(pady=10, ipady=4)

    def verify_security_answer():

        answer = answer_entry.get().strip()

        if not answer:
            messagebox.showwarning(
                "Warning",
                "Please enter your security answer",
                parent=security_window
            )
            return

        correct_answer = logged_user[5]

        if answer == correct_answer:
            messagebox.showinfo(
                "Verified",
                "Security answer verified!",
                parent=security_window
            )
            security_window.destroy()
            open_otp_window()
        else:
            messagebox.showerror(
                "Security Error",
                "Wrong security answer!",
                parent=security_window
            )

    make_button(
        security_window, "Verify Answer", verify_security_answer, width=18
    ).pack(pady=15)


# =========================================================
# OTP WINDOW
# =========================================================

def open_otp_window():

    global generated_otp

    otp_window = tk.Toplevel(window)
    otp_window.title("OTP Verification")
    otp_window.geometry("450x400")
    otp_window.configure(bg=BG_COLOR)

    tk.Label(
        otp_window,
        text="OTP Verification",
        font=("Segoe UI", 22, "bold"),
        bg=BG_COLOR, fg=TEXT_COLOR
    ).pack(pady=25)

    tk.Label(
        otp_window,
        text=f"OTP will be sent to:\n{phone_number_for_otp}",
        font=("Segoe UI", 11),
        bg=BG_COLOR, fg=TEXT_COLOR
    ).pack(pady=10)

    tk.Label(
        otp_window,
        text="Enter 6 digit OTP",
        font=("Segoe UI", 12),
        bg=BG_COLOR, fg=TEXT_COLOR
    ).pack(pady=10)

    otp_entry = tk.Entry(
        otp_window, width=25, font=("Segoe UI", 11),
        bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=ENTRY_FG,
        relief="flat", bd=6, justify="center"
    )
    otp_entry.pack(pady=10, ipady=4)

    def send_sms():
        global generated_otp

        if not check_internet():
            messagebox.showerror(
                "Network Error",
                "No internet connection.",
                parent=otp_window
            )
            return

        generated_otp = random.randint(100000, 999999)

        sent, result = send_otp_sms(phone_number_for_otp, generated_otp)

        if sent:
            messagebox.showinfo(
                "SMS OTP",
                "OTP sent successfully by SMS.",
                parent=otp_window
            )
        else:
            generated_otp = None
            messagebox.showerror(
                "SMS Failed",
                f"SMS could not be sent.\n\n{result}",
                parent=otp_window
            )

    make_button(
        otp_window, "📱 Send OTP by SMS", send_sms,
        bg="#059669", hover="#047857", width=22
    ).pack(pady=12)

    def verify_otp():

        entered_otp = otp_entry.get().strip()

        if not entered_otp:
            messagebox.showwarning("Warning", "Please enter OTP", parent=otp_window)
            return

        if generated_otp is None:
            messagebox.showwarning(
                "Warning",
                "First send OTP by SMS.",
                parent=otp_window
            )
            return

        if entered_otp == str(generated_otp):
            messagebox.showinfo(
                "Login Successful",
                f"Welcome {logged_user[1]}!",
                parent=otp_window
            )

            otp_window.destroy()
            window.withdraw()

            open_dashboard(window, logged_user)

        else:
            messagebox.showerror("OTP Error", "Invalid OTP.", parent=otp_window)

    make_button(
        otp_window, "Verify OTP", verify_otp, width=18
    ).pack(pady=15)


# =========================================================
# LOGIN BUTTON
# =========================================================

login_button = make_button(window, "Login", login, width=18)
login_button.pack(pady=20)


# =========================================================
# MAIN LOOP
# =========================================================

window.mainloop()
