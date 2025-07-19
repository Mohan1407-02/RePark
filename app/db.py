import sqlite3
import os

def get_db_connection():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect("data/vehicles.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_vehicles_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            plate TEXT PRIMARY KEY,
            owner TEXT,
            phone TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_rto_column_if_missing():
    conn = get_db_connection()
    try:
        conn.execute("ALTER TABLE fines ADD COLUMN rto_valid TEXT DEFAULT 'Unknown'")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

def create_fines_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS fines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate TEXT,
            status TEXT,
            sms_sent TEXT DEFAULT 'No',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_sms_column_if_missing():
    conn = get_db_connection()
    try:
        conn.execute("ALTER TABLE fines ADD COLUMN sms_sent TEXT DEFAULT 'No'")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

def init_db():
    create_vehicles_table()
    create_fines_table()
    add_sms_column_if_missing()
    add_rto_column_if_missing()

def seed_data():
    conn = get_db_connection()
    vehicles = [
        ("TN39G5555", "Govt Officer", "+919999999999"),
        ("KL06F5971", "John Doe", "+918888888888"),
        ("AP03XY1234", "Visitor", "+917777777777")
    ]
    conn.executemany("INSERT OR IGNORE INTO vehicles VALUES (?, ?, ?)", vehicles)
    conn.commit()
    conn.close()

def get_phone_by_plate(plate):
    conn = get_db_connection()
    row = conn.execute("SELECT phone FROM vehicles WHERE plate = ?", (plate,)).fetchone()
    conn.close()
    return row["phone"] if row else None
def validate_user(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user
