import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

class BillingFrame(tk.Frame):
    def __init__(self, parent, db, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.db = db
        self.tree = None
        self._build()

    def _build(self):
        frame = tk.Frame(self, padx=18, pady=18, bg="white")
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Billing", font=("Segoe UI", 16, "bold"), bg="white").pack(anchor="w")
        tk.Button(frame, text="Create Bill", command=self._open_new_bill, bg="#4a90e2", fg="white").pack(anchor="w", pady=10)

        columns = ("id", "patient_name", "description", "amount", "paid", "created_on")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=130, anchor="center")
        self.tree.column("description", width=200)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for bill in self.db.get_bills():
            self.tree.insert(
                "",
                tk.END,
                values=(
                    bill["id"],
                    bill["patient_name"],
                    bill["description"],
                    f"${bill['amount']:.2f}",
                    "Yes" if bill["paid"] else "No",
                    bill["created_on"],
                ),
            )

    def _open_new_bill(self):
        dialog = tk.Toplevel(self)
        dialog.title("Create Billing Entry")
        dialog.geometry("420x360")
        dialog.resizable(False, False)

        form = tk.Frame(dialog, padx=16, pady=16)
        form.pack(fill=tk.BOTH, expand=True)

        patients = self.db.get_patients()
        patient_names = [f"{row['id']} - {row['name']}" for row in patients]

        tk.Label(form, text="Patient", anchor="w").grid(row=0, column=0, sticky="w", pady=(0, 4))
        patient_combo = ttk.Combobox(form, values=patient_names, state="readonly", width=36)
        patient_combo.grid(row=1, column=0, pady=(0, 10))

        tk.Label(form, text="Description", anchor="w").grid(row=2, column=0, sticky="w", pady=(0, 4))
        description_entry = tk.Entry(form, width=38)
        description_entry.grid(row=3, column=0, pady=(0, 10))

        tk.Label(form, text="Amount", anchor="w").grid(row=4, column=0, sticky="w", pady=(0, 4))
        amount_entry = tk.Entry(form, width=38)
        amount_entry.grid(row=5, column=0, pady=(0, 10))

        paid_var = tk.IntVar(value=0)
        tk.Checkbutton(form, text="Paid", variable=paid_var, bg="white").grid(row=6, column=0, pady=(0, 10), sticky="w")

        def save_bill():
            patient = patient_combo.get()
            if not patient:
                messagebox.showwarning("Validation", "Select a patient first.")
                return
            try:
                amount = float(amount_entry.get().strip())
            except ValueError:
                messagebox.showwarning("Validation", "Enter a valid amount.")
                return
            patient_id = int(patient.split(" - ")[0])
            self.db.add_bill(
                (
                    patient_id,
                    description_entry.get().strip(),
                    amount,
                    paid_var.get(),
                    datetime.now().strftime("%Y-%m-%d %H:%M"),
                )
            )
            messagebox.showinfo("Saved", "Billing record created.")
            dialog.destroy()
            self.refresh()

        tk.Button(form, text="Save Bill", command=save_bill, bg="#28a745", fg="white").grid(row=7, column=0, pady=(8, 0))
