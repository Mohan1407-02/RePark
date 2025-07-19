from app.db import init_db, seed_data
import sqlite3

if __name__ == "__main__":
    print("🛠 Initializing RePark database...")
    init_db()
    seed_data()
    print("✅ Database initialized and test data seeded.")


conn = sqlite3.connect("data/vehicles.db")
cursor = conn.cursor()

# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    plate TEXT,
    status TEXT,
    sms_sent TEXT,
    rto_result TEXT,
    timestamp TEXT
)
""")

# Optional: Insert an admin user with hashed password
cursor.execute("""
INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)
""", ("Mohan", "scrypt:32768:8:1$kirT6yktkAa1Gx6f$7817ecc6fff3d34268e82c6a0b7d931648d744315afcaa560311bd5696af5f8322f17e38be2a92390f8a017300ae5a5f543ea52d8e46f099b9acb7f09e6aa385"))

conn.commit()
conn.close()

print("✅ DB initialized.")
