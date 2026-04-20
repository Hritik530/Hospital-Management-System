import datetime
import tkinter as tk
from database import HospitalDB
from login import LoginFrame
from patients import PatientFrame
from appointments import AppointmentFrame
from BILLING import BillingFrame
from rooms import RoomFrame

class SummaryFrame(tk.Frame):
    def __init__(self, parent, db, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.db = db
        self.stats_labels = []
        self._build()

    def _build(self):
        frame = tk.Frame(self, padx=22, pady=22, bg="white")
        frame.pack(fill=tk.BOTH, expand=True)

        self.summary_title = tk.Label(frame, text="Hospital Management Dashboard", font=("Segoe UI", 16, "bold"), bg="white")
        self.summary_title.pack(anchor="w", pady=(0, 12))

        self.cards_frame = tk.Frame(frame, bg="white")
        self.cards_frame.pack(fill=tk.X)

        labels = ["Patients", "Appointments", "Pending Billing", "Occupied Rooms"]
        for idx, label in enumerate(labels):
            card = tk.Frame(self.cards_frame, bg="#eef3fb", padx=18, pady=18)
            card.grid(row=0, column=idx, padx=12, pady=12, sticky="nsew")
            tk.Label(card, text=label, font=("Segoe UI", 12), bg="#eef3fb").pack(anchor="w")
            value_label = tk.Label(card, text="0", font=("Segoe UI", 20, "bold"), bg="#eef3fb")
            value_label.pack(anchor="w", pady=(12, 0))
            self.stats_labels.append(value_label)
            self.cards_frame.grid_columnconfigure(idx, weight=1)

        tk.Label(frame, text="Use the side menu to manage patients, appointments, billing, and rooms.", font=("Segoe UI", 11), bg="white", fg="#555").pack(anchor="w", pady=(16, 0))

    def refresh(self):
        patients = len(self.db.get_patients())
        appointments = len(self.db.get_appointments())
        unpaid = self.db.get_unpaid_total()
        rooms = self.db.get_rooms()
        occupied = sum(1 for room in rooms if room[3] == "Occupied")

        values = [
            patients,
            appointments,
            f"${unpaid:.2f}",
            f"{occupied}/{len(rooms)}",
        ]

        for label, value in zip(self.stats_labels, values):
            label.config(text=value)

class HospitalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hospital Management System")
        self.geometry("980x620")
        self.resizable(False, False)
        self.db = HospitalDB()
        self.user = None
        self.frames = {}
        self._build_login_screen()

    def _clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def _build_login_screen(self):
        self._clear_window()
        login_frame = LoginFrame(self, self.db, self._on_login)
        login_frame.pack(fill=tk.BOTH, expand=True)

    def _on_login(self, user):
        self.user = user
        self._build_dashboard()

    def _build_dashboard(self):
        self._clear_window()

        header = tk.Frame(self, bg="#2f3b52", height=72)
        header.pack(fill=tk.X)
        tk.Label(header, text=f"Welcome, {self.user['role']}", bg="#2f3b52", fg="white", font=("Segoe UI", 16, "bold")).place(x=24, y=20)
        tk.Button(header, text="Logout", command=self._build_login_screen, bg="#d9534f", fg="white", padx=14).place(x=860, y=20)

        menu = tk.Frame(self, width=220, bg="#f2f4f7")
        menu.pack(side=tk.LEFT, fill=tk.Y)
        content = tk.Frame(self, bg="white")
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=1)
        self.content_area = content

        menu_buttons = [
            ("Summary", self._show_summary),
            ("Patient Registry", self._show_patients),
            ("Appointments", self._show_appointments),
            ("Billing", self._show_billing),
            ("Room Management", self._show_rooms),
        ]

        for text, command in menu_buttons:
            button = tk.Button(menu, text=text, width=24, anchor="w", pady=12, command=command, bg="white")
            button.pack(pady=4, padx=12)

        self.frames = {
            "summary": SummaryFrame(self.content_area, self.db),
            "patients": PatientFrame(self.content_area, self.db),
            "appointments": AppointmentFrame(self.content_area, self.db),
            "billing": BillingFrame(self.content_area, self.db),
            "rooms": RoomFrame(self.content_area, self.db),
        }

        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

        self._show_summary()

    def _show_frame(self, name):
        frame = self.frames[name]
        frame.refresh()
        frame.tkraise()

    def _show_summary(self):
        self._show_frame("summary")

    def _show_patients(self):
        self._show_frame("patients")

    def _show_appointments(self):
        self._show_frame("appointments")

    def _show_billing(self):
        self._show_frame("billing")

    def _show_rooms(self):
        self._show_frame("rooms")

if __name__ == "__main__":
    app = HospitalApp()
    app.mainloop()
