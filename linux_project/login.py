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

# Apni existing 2Factor API key yahan paste karo
API_KEY = "291264d1-a69c-11f1-9cb1-0200cd936042"


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

heading = tk.Label(window, text="Secure Login", font=("Arial", 24, "bold"))
heading.pack(pady=20)

# EMAIL
tk.Label(window, text="Email", font=("Arial", 12)).pack()
email_entry = tk.Entry(window, width=35)
email_entry.pack(pady=7)

# PASSWORD
tk.Label(window, text="Password", font=("Arial", 12)).pack()
password_entry = tk.Entry(window, width=35, show="*")
password_entry.pack(pady=7)

# CAPTCHA
tk.Label(window, text="Enter CAPTCHA", font=("Arial", 12)).pack(pady=(15, 5))
captcha_label = tk.Label(window, text=captcha_code, font=("Arial", 18, "bold"))
captcha_label.pack()
captcha_entry = tk.Entry(window, width=20)
captcha_entry.pack(pady=7)

reload_button = tk.Button(window, text="🔄 Reload CAPTCHA", command=reload_captcha)
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

    tk.Label(
        security_window,
        text="Security Verification",
        font=("Arial", 20, "bold")
    ).pack(pady=25)

    tk.Label(
        security_window,
        text="Your Security Question:",
        font=("Arial", 12)
    ).pack(pady=10)

    tk.Label(
        security_window,
        text=security_question_from_db,
        font=("Arial", 13, "bold"),
        wraplength=420
    ).pack(pady=10)

    tk.Label(
        security_window,
        text="Enter your answer:",
        font=("Arial", 12)
    ).pack(pady=5)

    answer_entry = tk.Entry(security_window, width=35)
    answer_entry.pack(pady=10)

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

    tk.Button(
        security_window,
        text="Verify Answer",
        command=verify_security_answer,
        width=18
    ).pack(pady=15)


# =========================================================
# OTP WINDOW
# =========================================================

def open_otp_window():

    global generated_otp

    otp_window = tk.Toplevel(window)
    otp_window.title("OTP Verification")
    otp_window.geometry("450x400")

    tk.Label(
        otp_window,
        text="OTP Verification",
        font=("Arial", 22, "bold")
    ).pack(pady=25)

    tk.Label(
        otp_window,
        text=f"OTP will be sent to:\n{phone_number_for_otp}",
        font=("Arial", 11)
    ).pack(pady=10)

    tk.Label(
        otp_window,
        text="Enter 6 digit OTP",
        font=("Arial", 12)
    ).pack(pady=10)

    otp_entry = tk.Entry(otp_window, width=25)
    otp_entry.pack(pady=10)

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

    tk.Button(
        otp_window,
        text="📱 Send OTP by SMS",
        command=send_sms,
        width=22,
        font=("Arial", 11)
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

    tk.Button(
        otp_window,
        text="Verify OTP",
        command=verify_otp,
        width=18,
        font=("Arial", 11)
    ).pack(pady=15)


# =========================================================
# LOGIN BUTTON
# =========================================================

login_button = tk.Button(
    window,
    text="Login",
    command=login,
    width=18,
    font=("Arial", 12)
)

login_button.pack(pady=20)


# =========================================================
# MAIN LOOP
# =========================================================

window.mainloop()
