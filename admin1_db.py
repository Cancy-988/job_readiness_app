import sqlite3

conn = sqlite3.connect("data/users.db")
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE admin_users ADD COLUMN is_super_admin INTEGER DEFAULT 1")
    print("✅ is_super_admin column added")
except:
    print("ℹ️ is_super_admin already exists")

try:
    cursor.execute("ALTER TABLE admin_users ADD COLUMN is_active INTEGER DEFAULT 1")
    print("✅ is_active column added")
except:
    print("ℹ️ is_active already exists")

conn.commit()
conn.close()

print("✅ Done fixing admin table")
