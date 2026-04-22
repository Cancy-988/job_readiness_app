import sqlite3

connection = sqlite3.connect("data/users.db")
cursor = connection.cursor()


cursor.execute(
	"""
	CREATE TABLE IF NOT EXISTS users (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		name TEXT NOT NULL,
		email TEXT UNIQUE NOT NULL,
		password TEXT NOT NULL
	)
	"""
)


cursor.execute("PRAGMA table_info(users)")
columns = {row[1] for row in cursor.fetchall()}

if "role" not in columns:
	cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'student'")

if "profile_pic" not in columns:
	cursor.execute("ALTER TABLE users ADD COLUMN profile_pic TEXT")


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


connection.commit()
connection.close()

print("Database and users table created successfully!")
