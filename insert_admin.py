import sqlite3

conn = sqlite3.connect("data/users.db")
cursor = conn.cursor()

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
