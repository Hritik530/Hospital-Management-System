import tkinter as tk
from tkinter import messagebox, ttk

class AppointmentFrame(tk.Frame):
    def __init__(self, parent, db, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.db = db
        self.tree = None
        self._build()

    def _build(self):
        frame = tk.Frame(self, padx=18, pady=18, bg="white")
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Appointments", font=("Segoe UI", 16, "bold"), bg="white").pack(anchor="w")
        tk.Button(frame, text="Schedule Appointment", command=self._open_new_appointment, bg="#4a90e2", fg="white").pack(anchor="w", pady=10)

        columns = ("id", "patient_name", "doctor", "date", "time", "notes")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=130, anchor="center")
        self.tree.column("notes", width=220)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for appointment in self.db.get_appointments():
            self.tree.insert(
                "",
                tk.END,
                values=(
                    appointment["id"],
                    appointment["patient_name"],
                    appointment["doctor"],
                    appointment["date"],
                    appointment["time"],
                    appointment["notes"],
                ),
            )

    def _open_new_appointment(self):
        dialog = tk.Toplevel(self)
        dialog.title("Schedule Appointment")
        dialog.geometry("420x380")
        dialog.resizable(False, False)

        form = tk.Frame(dialog, padx=16, pady=16)
        form.pack(fill=tk.BOTH, expand=True)

        patients = self.db.get_patients()
        patient_names = [f"{row['id']} - {row['name']}" for row in patients]

        tk.Label(form, text="Patient", anchor="w").grid(row=0, column=0, sticky="w", pady=(0, 4))
        patient_combo = ttk.Combobox(form, values=patient_names, state="readonly", width=36)
        patient_combo.grid(row=1, column=0, pady=(0, 10))

        tk.Label(form, text="Doctor", anchor="w").grid(row=2, column=0, sticky="w", pady=(0, 4))
        doctor_entry = tk.Entry(form, width=38)
        doctor_entry.grid(row=3, column=0, pady=(0, 10))

        tk.Label(form, text="Date (YYYY-MM-DD)", anchor="w").grid(row=4, column=0, sticky="w", pady=(0, 4))
        date_entry = tk.Entry(form, width=38)
        date_entry.grid(row=5, column=0, pady=(0, 10))

        tk.Label(form, text="Time (HH:MM)", anchor="w").grid(row=6, column=0, sticky="w", pady=(0, 4))
        time_entry = tk.Entry(form, width=38)
        time_entry.grid(row=7, column=0, pady=(0, 10))

        tk.Label(form, text="Notes", anchor="w").grid(row=8, column=0, sticky="w", pady=(0, 4))
        notes_entry = tk.Text(form, height=4, width=36)
        notes_entry.grid(row=9, column=0, pady=(0, 10))

        def save_appointment():
            patient = patient_combo.get()
            if not patient:
                messagebox.showwarning("Validation", "Select a patient first.")
                return
            patient_id = int(patient.split(" - ")[0])
            self.db.add_appointment(
                (
                    patient_id,
                    doctor_entry.get().strip(),
                    date_entry.get().strip(),
                    time_entry.get().strip(),
                    notes_entry.get("1.0", tk.END).strip(),
                )
            )
            messagebox.showinfo("Saved", "Appointment scheduled successfully.")
            dialog.destroy()
            self.refresh()

        tk.Button(form, text="Save Appointment", command=save_appointment, bg="#28a745", fg="white").grid(row=10, column=0, pady=(8, 0))
