import sqlite3

DB_FILE = "hospital.db"
DEFAULT_USERS = [
    ("admin", "admin123", "Administrator"),
    ("doctor", "docpass", "Doctor"),
]
ROOM_TYPES = ["General", "Private", "Deluxe", "ICU"]

class HospitalDB:
    def __init__(self, db_file=DB_FILE):
        self.conn = sqlite3.connect(db_file)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                age INTEGER,
                gender TEXT,
                phone TEXT,
                address TEXT,
                diagnosis TEXT,
                admitted_on TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                doctor TEXT,
                date TEXT,
                time TEXT,
                notes TEXT,
                FOREIGN KEY(patient_id) REFERENCES patients(id)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS billing (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                description TEXT,
                amount REAL,
                paid INTEGER,
                created_on TEXT,
                FOREIGN KEY(patient_id) REFERENCES patients(id)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_number TEXT UNIQUE,
                room_type TEXT,
                status TEXT,
                patient_id INTEGER,
                FOREIGN KEY(patient_id) REFERENCES patients(id)
            )
            """
        )
        self.conn.commit()
        self._seed_users()
        self._seed_rooms()

    def _seed_users(self):
        cursor = self.conn.cursor()
        for username, password, role in DEFAULT_USERS:
            cursor.execute(
                "INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, password, role),
            )
        self.conn.commit()

    def _seed_rooms(self):
        cursor = self.conn.cursor()
        for room_number in range(101, 111):
            cursor.execute(
                "INSERT OR IGNORE INTO rooms (room_number, room_type, status, patient_id) VALUES (?, ?, ?, ?)",
                (str(room_number), ROOM_TYPES[(room_number - 101) % len(ROOM_TYPES)], "Available", None),
            )
        self.conn.commit()

    def authenticate(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        return cursor.fetchone()

    def add_patient(self, patient_data):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO patients (name, age, gender, phone, address, diagnosis, admitted_on) VALUES (?, ?, ?, ?, ?, ?, ?)",
            patient_data,
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_patients(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM patients ORDER BY id DESC")
        return cursor.fetchall()

    def add_appointment(self, appointment_data):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO appointments (patient_id, doctor, date, time, notes) VALUES (?, ?, ?, ?, ?)",
            appointment_data,
        )
        self.conn.commit()

    def get_appointments(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT a.id, p.name AS patient_name, a.doctor, a.date, a.time, a.notes "
            "FROM appointments a JOIN patients p ON a.patient_id = p.id "
            "ORDER BY a.date DESC, a.time DESC"
        )
        return cursor.fetchall()

    def add_bill(self, bill_data):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO billing (patient_id, description, amount, paid, created_on) VALUES (?, ?, ?, ?, ?)",
            bill_data,
        )
        self.conn.commit()

    def get_bills(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT b.id, p.name AS patient_name, b.description, b.amount, b.paid, b.created_on "
            "FROM billing b JOIN patients p ON b.patient_id = p.id "
            "ORDER BY b.created_on DESC"
        )
        return cursor.fetchall()

    def get_unpaid_total(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT SUM(amount) AS total FROM billing WHERE paid = 0")
        return cursor.fetchone()["total"] or 0.0

    def get_rooms(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT r.id, r.room_number, r.room_type, r.status, p.name AS patient_name "
            "FROM rooms r LEFT JOIN patients p ON r.patient_id = p.id "
            "ORDER BY r.room_number"
        )
        return cursor.fetchall()

    def assign_room(self, room_id, patient_id):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE rooms SET status = 'Occupied', patient_id = ? WHERE id = ?", (patient_id, room_id))
        self.conn.commit()

    def release_room(self, room_id):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE rooms SET status = 'Available', patient_id = NULL WHERE id = ?", (room_id,))
        self.conn.commit()
