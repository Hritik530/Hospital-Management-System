import tkinter as tk
from tkinter import messagebox

class LoginFrame(tk.Frame):
    def __init__(self, parent, db, on_login, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.db = db
        self.on_login = on_login
        self._build()

    def _build(self):
        frame = tk.Frame(self, padx=24, pady=24)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tk.Label(frame, text="Hospital Management System", font=("Segoe UI", 20, "bold")).pack(pady=(0, 18))
        tk.Label(frame, text="Sign in to continue", font=("Segoe UI", 12)).pack(pady=(0, 14))

        form = tk.Frame(frame)
        form.pack()

        tk.Label(form, text="Username", anchor="w").grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.username_entry = tk.Entry(form, width=32)
        self.username_entry.grid(row=1, column=0, pady=(0, 12))

        tk.Label(form, text="Password", anchor="w").grid(row=2, column=0, sticky="w", pady=(0, 4))
        self.password_entry = tk.Entry(form, width=32, show="*")
        self.password_entry.grid(row=3, column=0, pady=(0, 16))

        login_button = tk.Button(frame, text="Login", width=26, command=self._login, bg="#4a90e2", fg="white")
        login_button.pack(pady=(0, 10))

        tk.Label(frame, text="Use admin/admin123 or doctor/docpass", fg="#555", font=("Segoe UI", 9)).pack(pady=(10, 0))

    def _login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        user = self.db.authenticate(username, password)
        if user:
            self.on_login(user)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")
