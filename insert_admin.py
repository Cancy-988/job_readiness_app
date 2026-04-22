import sqlite3

conn = sqlite3.connect("data/users.db")
cursor = conn.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS admin_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        is_super_admin INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1
    )
    """
)

cursor.execute("""
INSERT OR IGNORE INTO admin_users
(name, email, password, is_super_admin, is_active)
VALUES (?, ?, ?, ?, ?)
""", (
    "Permanent Admin",
    "admin@gmail.com",
    "admin123",
    1,
    1
))

conn.commit()
conn.close()

print("✅ Permanent admin inserted / already exists")
