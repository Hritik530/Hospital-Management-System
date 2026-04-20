import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

class PatientFrame(tk.Frame):
    def __init__(self, parent, db, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.db = db
        self.tree = None
        self._build()

    def _build(self):
        frame = tk.Frame(self, padx=18, pady=18, bg="white")
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Patient Registry", font=("Segoe UI", 16, "bold"), bg="white").pack(anchor="w")

        control = tk.Frame(frame, bg="white")
        control.pack(anchor="w", pady=10)
        tk.Button(control, text="New Patient", command=self._open_new_patient, bg="#4a90e2", fg="white").pack()

        columns = ("id", "name", "age", "gender", "phone", "diagnosis", "admitted_on")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=110, anchor="center")
        self.tree.column("name", width=160)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for patient in self.db.get_patients():
            self.tree.insert(
                "",
                tk.END,
                values=(
                    patient["id"],
                    patient["name"],
                    patient["age"],
                    patient["gender"],
                    patient["phone"],
                    patient["diagnosis"],
                    patient["admitted_on"],
                ),
            )

    def _open_new_patient(self):
        dialog = tk.Toplevel(self)
        dialog.title("New Patient")
        dialog.geometry("420x420")
        dialog.resizable(False, False)

        form = tk.Frame(dialog, padx=16, pady=16)
        form.pack(fill=tk.BOTH, expand=True)

        labels = ["Name", "Age", "Gender", "Phone", "Address", "Diagnosis"]
        fields = {}
        for idx, label in enumerate(labels):
            tk.Label(form, text=label, anchor="w").grid(row=idx * 2, column=0, sticky="w", pady=(0, 4))
            if label == "Gender":
                combo = ttk.Combobox(form, values=["Male", "Female", "Other"], state="readonly")
                combo.grid(row=idx * 2 + 1, column=0, sticky="ew", pady=(0, 10))
                fields[label] = combo
            elif label == "Address":
                text = tk.Text(form, height=3, width=36)
                text.grid(row=idx * 2 + 1, column=0, pady=(0, 10))
                fields[label] = text
            else:
                entry = tk.Entry(form, width=38)
                entry.grid(row=idx * 2 + 1, column=0, pady=(0, 10))
                fields[label] = entry

        def save_patient():
            data = [
                fields["Name"].get().strip(),
                int(fields["Age"].get().strip() or 0),
                fields["Gender"].get().strip(),
                fields["Phone"].get().strip(),
                fields["Address"].get("1.0", tk.END).strip(),
                fields["Diagnosis"].get().strip(),
                datetime.now().strftime("%Y-%m-%d %H:%M"),
            ]
            if not data[0] or data[1] <= 0 or not data[2]:
                messagebox.showwarning("Validation", "Please complete name, age, and gender.")
                return
            self.db.add_patient(tuple(data))
            messagebox.showinfo("Saved", "Patient registered successfully.")
            dialog.destroy()
            self.refresh()

        save_btn = tk.Button(form, text="Save", command=save_patient, bg="#28a745", fg="white")
        save_btn.grid(row=len(labels) * 2, column=0, pady=(14, 0))
