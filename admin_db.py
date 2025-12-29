import sqlite3

conn = sqlite3.connect("data/users.db")
cursor = conn.cursor()

# Admin users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS admin_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT,
    is_super_admin INTEGER DEFAULT 1,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS admin_login_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address TEXT
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS admin_actions (
    action_id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER,
    action TEXT,
    action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")


print("✅ Admin database structure created successfully")


conn.commit()
conn.close()

print(" Admin table created")