import tkinter as tk
from tkinter import messagebox, ttk

class RoomFrame(tk.Frame):
    def __init__(self, parent, db, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.db = db
        self.tree = None
        self._build()

    def _build(self):
        frame = tk.Frame(self, padx=18, pady=18, bg="white")
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Room Management", font=("Segoe UI", 16, "bold"), bg="white").pack(anchor="w")
        tk.Button(frame, text="Release Selected Room", command=lambda: self._change_room_status(False), bg="#d9534f", fg="white").pack(anchor="w", pady=10)
        tk.Button(frame, text="Assign Selected Room", command=lambda: self._change_room_status(True), bg="#28a745", fg="white").pack(anchor="w", pady=(0, 10))

        columns = ("id", "room_number", "room_type", "status", "patient_name")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=130, anchor="center")
        self.tree.column("patient_name", width=180)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for room in self.db.get_rooms():
            self.tree.insert(
                "",
                tk.END,
                values=(
                    room["id"],
                    room["room_number"],
                    room["room_type"],
                    room["status"],
                    room["patient_name"] or "None",
                ),
            )

    def _change_room_status(self, assign):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Select a room first.")
            return
        item = self.tree.item(selected[0])
        room_id = item["values"][0]
        if assign:
            if not self.db.get_patients():
                messagebox.showwarning("No Patients", "Register a patient before assigning a room.")
                return
            self._assign_room_dialog(room_id)
        else:
            self.db.release_room(room_id)
            messagebox.showinfo("Released", "Room released successfully.")
            self.refresh()

    def _assign_room_dialog(self, room_id):
        dialog = tk.Toplevel(self)
        dialog.title("Assign Room")
        dialog.geometry("420x240")
        dialog.resizable(False, False)

        form = tk.Frame(dialog, padx=16, pady=16)
        form.pack(fill=tk.BOTH, expand=True)

        patients = self.db.get_patients()
        patient_names = [f"{row['id']} - {row['name']}" for row in patients]

        tk.Label(form, text="Patient", anchor="w").grid(row=0, column=0, sticky="w", pady=(0, 4))
        patient_combo = ttk.Combobox(form, values=patient_names, state="readonly", width=36)
        patient_combo.grid(row=1, column=0, pady=(0, 10))

        def assign_room():
            patient = patient_combo.get()
            if not patient:
                messagebox.showwarning("Validation", "Select a patient first.")
                return
            patient_id = int(patient.split(" - ")[0])
            self.db.assign_room(room_id, patient_id)
            messagebox.showinfo("Assigned", "Room assigned successfully.")
            dialog.destroy()
            self.refresh()

        tk.Button(form, text="Assign Room", command=assign_room, bg="#28a745", fg="white").grid(row=2, column=0, pady=(8, 0))
