import sqlite3

conn = sqlite3.connect("data/users.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(users)")
columns = {row[1] for row in cursor.fetchall()}

if "profile_pic" not in columns:
	cursor.execute("ALTER TABLE users ADD COLUMN profile_pic TEXT")

conn.commit()
conn.close()

print("Profile picture column added!")
