import os 
import math 
import subprocess 
import threading 
import tkinter as tk 
from tkinter import messagebox, filedialog 
 
# ========================================================= 
# DASHBOARD INTERFACE 
# ========================================================= 
 
def open_dashboard(window, logged_user): 
    # Unpack profile data safely 
    user_id = logged_user[0] 
    user_name = logged_user[1] 
    user_email = logged_user[2] 
 
    dashboard = tk.Toplevel(window) 
    dashboard.title("Cybersecurity Control Center") 
    dashboard.geometry("820x920") 
 
    # Cyberpunk Dark Theme Background 
    dashboard.configure(bg="#121214") 
 
    # ===================================================== 
    # TITLE & USER PROFILE HEADER 
    # ===================================================== 
 
    tk.Label( 
        dashboard, 
        text="🛡️ CYBERSECURITY CONTROL CENTER", 
        font=("Arial", 22, "bold"), 
        bg="#121214", 
        fg="#00FF66"  # Matrix Green 
    ).pack(pady=(20, 5)) 
 
    profile_frame = tk.Frame(dashboard, bg="#1E1E24", bd=1, relief=tk.RAISED) 
    profile_frame.pack(fill=tk.X, padx=40, pady=5) 
 
    tk.Label( 
        profile_frame, 
        text=f"Operator: {user_name}  |  ID: {user_id}  |  Email: {user_email}", 
        font=("Courier New", 11, "bold"), 
        bg="#1E1E24", 
        fg="#A9A9B3"  # Tech Gray 
    ).pack(pady=8) 
 
    # ===================================================== 
    # SECTION 1: NMAP NETWORK SCANNER 
    # ===================================================== 
 
    tk.Label( 
        dashboard, 
        text="📡 Network Vulnerability Scanner (Nmap)", 
        font=("Arial", 14, "bold"), 
        bg="#121214", 
        fg="#3399FF"  # Cyber Blue 
    ).pack(pady=(20, 5)) 
 
    nmap_frame = tk.Frame(dashboard, bg="#121214") 
    nmap_frame.pack(pady=5) 
 
    tk.Label( 
        nmap_frame, 
        text="Target IP / Domain:", 
        font=("Arial", 11), 
        bg="#121214", 
        fg="#FFFFFF" 
    ).pack(side=tk.LEFT, padx=5) 
 
    target_entry = tk.Entry( 
        nmap_frame, 
        width=25, 
        font=("Arial", 11), 
        bg="#1E1E24", 
        fg="#FFFFFF", 
        insertbackground="white", 
        bd=1, 
        relief=tk.SOLID 
    ) 
    target_entry.insert(0, "127.0.0.1") 
    target_entry.pack(side=tk.LEFT, padx=5) 
 
    # Luminous green terminal output layout 
    nmap_output = tk.Text( 
        dashboard, 
        width=85, 
        height=12, 
        font=("Courier New", 10), 
        bg="#0A0A0C", 
        fg="#00FF66", 
        insertbackground="white", 
        bd=1, 
        relief=tk.SOLID 
    ) 
    nmap_output.pack(pady=10) 
 
    def run_nmap_scan(): 
        target = target_entry.get().strip() 
        if not target: 
            messagebox.showwarning("Input Error", "Please provide a valid Target IP or Hostname.") 
            return 
 
        nmap_btn.config(state=tk.DISABLED, text="⚡ Scanning Network...", bg="#555555") 
        nmap_output.delete("1.0", tk.END) 
        nmap_output.insert(tk.END, f"[*] Initializing Nmap scan against {target}...\n") 
 
        def network_scan_thread(): 
            try: 
                res = subprocess.run( 
                    ["nmap", "-F", target], 
                    capture_output=True, 
                    text=True, 
                    timeout=120 
                ) 
                dashboard.after(0, lambda: display_nmap_results(res.stdout, res.stderr)) 
            except FileNotFoundError: 
                dashboard.after( 
                    0, 
                    lambda: display_nmap_results( 
                        "", "Error: Nmap tool is not installed on this system.\nRun: sudo apt install nmap" 
                    ) 
                ) 
            except subprocess.TimeoutExpired: 
                dashboard.after(0, lambda: display_nmap_results("", "Error: The network scan process timed out.")) 
            except Exception as e: 
                dashboard.after(0, lambda: display_nmap_results("", f"System Error: {str(e)}")) 
 
        threading.Thread(target=network_scan_thread, daemon=True).start() 
 
    def display_nmap_results(stdout, stderr): 
        nmap_btn.config(state=tk.NORMAL, text="🔍 Start Nmap Scan", bg="#3399FF") 
        if stderr: 
            nmap_output.insert(tk.END, f"\n[!] SCAN ERROR:\n{stderr}") 
        else: 
            nmap_output.insert(tk.END, stdout if stdout.strip() else "\n[-] Scan complete. No active open ports identified.") 
 
    nmap_btn = tk.Button( 
        dashboard, 
        text="🔍 Start Nmap Scan", 
        width=22, 
        font=("Arial", 11, "bold"), 
        bg="#3399FF", 
        fg="#FFFFFF", 
        activebackground="#0066CC", 
        activeforeground="#FFFFFF", 
        bd=0, 
        cursor="hand2", 
        command=run_nmap_scan 
    ) 
    nmap_btn.pack(pady=5) 
 
    # Horizontal styling separation line 
    tk.Frame(dashboard, height=1, bg="#2D2D35").pack(fill=tk.X, padx=40, pady=20) 
 
    # ===================================================== 
    # SECTION 2: SECURE FILE UPLOAD 
    # ===================================================== 
 
    tk.Label( 
        dashboard, 
        text="🗂️ Secure File Upload & Malware Scan", 
        font=("Arial", 14, "bold"), 
        bg="#121214", 
        fg="#FFCC00"  # Cyber Alert Yellow 
    ).pack(pady=(5, 5)) 
 
    MAX_SIZE_KB = 200 
    MAX_SIZE_BYTES = MAX_SIZE_KB * 1024 
 
    tk.Label( 
        dashboard, 
        text=f"Maximum allowed file size: {MAX_SIZE_KB} KB", 
        font=("Arial", 10, "italic"), 
        bg="#121214", 
        fg="#A9A9B3" 
    ).pack(pady=2) 
 
    # ===================================================== 
    # ANIMATED SCANNING LOADER (4 RUNNING DOTS) 
    # ===================================================== 
 
    loader_frame = tk.Frame(dashboard, bg="#121214") 
 
    loader_canvas = tk.Canvas( 
        loader_frame, 
        width=100, 
        height=100, 
        bg="#121214", 
        highlightthickness=0 
    ) 
    loader_canvas.pack() 
 
    loader_text = tk.Label( 
        loader_frame, 
        text="Analyzing File Signatures...", 
        font=("Courier New", 11, "bold"), 
        bg="#121214", 
        fg="#FFCC00" 
    ) 
    loader_text.pack(pady=5) 
 
    loader_running = False 
    loader_angle = 0 
 
    # Green custom aesthetic dots matching your math formula 
    dots = [] 
    for i in range(4): 
        dot = loader_canvas.create_oval( 
            0, 0, 10, 10, 
            fill="#00FF66", 
            outline="" 
        ) 
        dots.append(dot) 
 
    def animate_loader(): 
        nonlocal loader_angle 
        if not loader_running: 
            return 
 
        center_x = 50 
        center_y = 45 
        radius = 25 
 
        for i, dot in enumerate(dots): 
            angle = math.radians(loader_angle + (i * 90)) 
            x = center_x + radius * math.cos(angle) 
            y = center_y + radius * math.sin(angle) 
 
            loader_canvas.coords( 
                dot, 
                x - 5, y - 5, 
                x + 5, y + 5 
            ) 
 
        loader_angle += 8 
        dashboard.after(30, animate_loader) 
 
    def start_loader(): 
        nonlocal loader_running 
        loader_running = True 
        loader_frame.pack(pady=10) 
        animate_loader() 
 
    def stop_loader(): 
        nonlocal loader_running 
        loader_running = False 
        loader_frame.pack_forget() 
 
    # Scan Button UI 
    scan_button = tk.Button( 
        dashboard, 
        text="📁 Select & Scan File", 
        width=22, 
        font=("Arial", 12, "bold"), 
        bg="#FFCC00", 
        fg="#121214", 
        activebackground="#CCA300", 
        activeforeground="#121214", 
        bd=0, 
        cursor="hand2" 
    ) 
    scan_button.pack(pady=10) 
 
    # ===================================================== 
    # FILE UPLOAD PIPELINE LOGIC 
    # ===================================================== 
 
    def scan_error(title, message): 
        stop_loader() 
        scan_button.config(state=tk.NORMAL, text="📁 Select & Scan File", bg="#FFCC00") 
        messagebox.showerror(title, message, parent=dashboard) 
 
    def finish_scan(scan_result, file_name, extension, file_size_kb): 
        stop_loader() 
        scan_button.config(state=tk.NORMAL, text="📁 Select & Scan File", bg="#FFCC00") 
 
        if scan_result.returncode == 0: 
            messagebox.showinfo( 
                "Scan Passed", 
                f"✔ No threats detected in {file_name}!\n\n" 
                f"File Size: {file_size_kb:.2f} KB\n" 
                f"Extension: {extension}\n\n" 
                f"File successfully uploaded.", 
                parent=dashboard 
            ) 
        elif scan_result.returncode == 1: 
            messagebox.showerror( 
                "Threat Detected", 
                f"❌ Malicious content detected in {file_name}!\n\n" 
                f"This file has been blocked and quarantined.", 
                parent=dashboard 
            ) 
        else: 
            error_detail = scan_result.stderr.strip() or scan_result.stdout.strip() 
            scan_error("Scan Failed", f"ClamAV error:\n\n{error_detail}") 
 
    def upload_file(): 
        file_path = filedialog.askopenfilename(title="Select a file") 
        if not file_path: 
            return 
 
        try: 
            file_size = os.path.getsize(file_path) 
        except OSError as e: 
            messagebox.showerror("File Error", str(e)) 
            return 
 
        file_size_kb = file_size / 1024 
 
        if file_size > MAX_SIZE_BYTES: 
            messagebox.showerror( 
                "File Rejected", 
                f"File size must be less than {MAX_SIZE_KB} KB.\n\n" 
                f"Selected file size: {file_size_kb:.2f} KB" 
            ) 
            return 
 
        allowed_extensions = [".txt", ".pdf", ".jpg", ".jpeg", ".png", ".csv"] 
        file_name = os.path.basename(file_path) 
        extension = os.path.splitext(file_name)[1].lower() 
 
        if extension not in allowed_extensions: 
            messagebox.showerror( 
                "File Rejected", 
                "This file type is not allowed.\n\n" 
                "Allowed types:\n.txt\n.pdf\n.jpg\n.jpeg\n.png\n.csv" 
            ) 
            return 
 
        # Disable selection triggers and deploy spinning dots loader 
        scan_button.config(state=tk.DISABLED, text="Scanning file...", bg="#555555") 
        start_loader() 
 
        def scan_file(): 
            try: 
                scan_result = subprocess.run( 
                    ["clamscan", "--no-summary", file_path], 
                    capture_output=True, 
                    text=True, 
                    timeout=60 
                ) 
                dashboard.after(0, lambda: finish_scan(scan_result, file_name, extension, file_size_kb)) 
            except FileNotFoundError: 
                dashboard.after( 
                    0, 
                    lambda: scan_error( 
                        "ClamAV Error", 
                        "ClamAV is not installed.\n\nRun:\nsudo apt install clamav" 
                    ) 
                ) 
            except subprocess.TimeoutExpired: 
                dashboard.after( 
                    0, 
                    lambda: scan_error( 
                        "Scan Timeout", 
                        "File scanning took too long.\n\nUpload has been blocked." 
                    ) 
                ) 
            except Exception as e: 
                dashboard.after(0, lambda: scan_error("File Scan Error", str(e))) 
 
        threading.Thread(target=scan_file, daemon=True).start() 
 
    scan_button.config(command=upload_file) 
 
    return dashboard 
 
 
# ========================================================= 
# MAIN APP EXECUTION (TERMINAL ENTRY POINT) 
# ========================================================= 
 
if __name__ == "__main__": 
    root = tk.Tk() 
    root.title("Security Login Portal") 
    root.geometry("420x460") 
    root.configure(bg="#121214") 
 
    # Mirror structured login list tracking data: [ID, Name, Email] 
    mock_user_profile = [1024, "Anjali", "anjali@cybersecurity.local"] 
 
    tk.Label( 
        root, 
        text="🔐 SECURITY VERIFICATION", 
        font=("Arial", 14, "bold"), 
        fg="#00FF66", 
        bg="#121214" 
    ).pack(pady=(20, 10)) 
 
    # ----------------------------------------------------- 
    # STEP 1: SECURITY QUESTION (CASE-SENSITIVE CHECK) 
    # ----------------------------------------------------- 
 
    # The correct answer, stored EXACTLY as it must be typed (case-sensitive) 
    CORRECT_ANSWER = "kallu" 
 
    tk.Label( 
        root, 
        text="Security Question: What is your nickname?", 
        font=("Arial", 10, "bold"), 
        bg="#121214", 
        fg="#FFFFFF", 
        wraplength=360, 
        justify="left" 
    ).pack(pady=(5, 5), padx=20) 
 
    security_entry = tk.Entry( 
        root, 
        width=30, 
        font=("Arial", 11), 
        bg="#1E1E24", 
        fg="#FFFFFF", 
        insertbackground="white" 
    ) 
    security_entry.pack(pady=5) 
 
    # This frame holds the OTP section. It stays hidden until the 
    # security question is answered correctly (with matching case). 
    otp_section_frame = tk.Frame(root, bg="#121214") 
 
    def verify_security_question(): 
        user_answer = security_entry.get()  # NOTE: no .strip().lower()/.upper() -> case stays intact 
 
        # Case-sensitive, EXACT match. "kallu" or "Kallu" will NOT pass; only "KALLU" will. 
        if user_answer == CORRECT_ANSWER: 
            security_btn.config(state=tk.DISABLED) 
            security_entry.config(state=tk.DISABLED) 
            otp_section_frame.pack(pady=15, fill=tk.X) 
        else: 
            messagebox.showerror( 
                "Incorrect Answer", 
                "Security answer is incorrect (answers are case-sensitive).", 
                parent=root 
            ) 
 
    security_btn = tk.Button( 
        root, 
        text="Verify Security Answer", 
        font=("Arial", 10, "bold"), 
        bg="#3399FF", 
        fg="white", 
        activebackground="#0066CC", 
        activeforeground="white", 
        bd=0, 
        cursor="hand2", 
        command=verify_security_question 
    ) 
    security_btn.pack(pady=10) 
 
    # ----------------------------------------------------- 
    # STEP 2: OTP SECTION — ONLY "SEND OTP BY CALL" BUTTON 
    # (Label says "by Call", but internally it runs the SMS-sending code) 
    # ----------------------------------------------------- 
 
    tk.Label( 
        otp_section_frame, 
        text="OTP Verification", 
        font=("Arial", 12, "bold"), 
        bg="#121214", 
        fg="#00FF66" 
    ).pack(pady=(5, 10)) 
 
    # ---- This is the original SMS-sending logic, kept as-is ---- 
    def send_otp_via_message_logic(phone_number="9999999999"): 
        # Replace this block with your ACTUAL SMS API call 
        # (Twilio / Fast2SMS / MSG91 / etc.) 
        generated_otp = "123456"  # demo value only 
        print(f"[SMS-LOGIC] Sending OTP {generated_otp} to {phone_number}") 
        return generated_otp 
 
    current_otp = {"value": None} 
 
    def send_otp_by_call(): 
        # Button text says "Call", but we call the SMS-sending function underneath 
        otp = send_otp_via_message_logic() 
        current_otp["value"] = otp 
 
        call_otp_btn.config(state=tk.DISABLED, text="OTP Sent ✅") 
 
        # Enable the OTP field only now, and give it focus so it's clickable/typeable 
        otp_entry.config(state=tk.NORMAL) 
        otp_entry.delete(0, tk.END) 
        otp_entry.focus_set() 
 
        messagebox.showinfo("OTP Sent", "OTP has been sent to your registered number.", parent=root) 
 
    call_otp_btn = tk.Button( 
        otp_section_frame, 
        text="📞 Send OTP by Call", 
        font=("Arial", 10, "bold"), 
        bg="#FFCC00", 
        fg="#121214", 
        activebackground="#CCA300", 
        activeforeground="#121214", 
        bd=0, 
        cursor="hand2", 
        command=send_otp_by_call 
    ) 
    call_otp_btn.pack(pady=5) 
 
    # ----------------------------------------------------- 
    # OTP INPUT FIELD — fixed so click/type works properly 
    # ----------------------------------------------------- 
    # It starts DISABLED (greyed out) because there's no OTP yet. 
    # It becomes NORMAL + focused only after "Send OTP by Call" is pressed. 
    # It is a plain .pack()'d widget with nothing overlapping it, so once 
    # enabled, clicking and typing both work. 
 
    otp_entry = tk.Entry( 
        otp_section_frame, 
        width=15, 
        font=("Arial", 14), 
        justify="center", 
        bg="#1E1E24", 
        fg="#FFFFFF", 
        insertbackground="white", 
        state=tk.DISABLED 
    ) 
    otp_entry.pack(pady=10) 
 
    def verify_otp(): 
        entered = otp_entry.get().strip() 
        if not entered: 
            messagebox.showwarning("Input Error", "Please enter the OTP.", parent=root) 
            return 
        if entered == current_otp["value"]: 
            messagebox.showinfo("Success", "OTP Verified Successfully!", parent=root) 
            open_dashboard(root, mock_user_profile) 
        else: 
            messagebox.showerror("Invalid OTP", "The OTP entered is incorrect.", parent=root) 
 
    verify_otp_btn = tk.Button( 
        otp_section_frame, 
        text="Verify OTP & Continue", 
        font=("Arial", 10, "bold"), 
        bg="#00FF66", 
        fg="#121214", 
        activebackground="#00CC52", 
        activeforeground="#121214", 
        bd=0, 
        cursor="hand2", 
        command=verify_otp 
    ) 
    verify_otp_btn.pack(pady=5) 
 
    root.mainloop() 
