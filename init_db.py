import os
import sqlite3

try:
    import psycopg2
except ImportError:
    psycopg2 = None

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def get_connection():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        if psycopg2 is None:
            raise RuntimeError("psycopg2-binary is required when DATABASE_URL is set.")
        return psycopg2.connect(database_url), True

    conn = sqlite3.connect("data/users.db")
    return conn, False


def run_query(cursor, is_postgres, query, params=()):
    if is_postgres:
        query = query.replace("?", "%s")
    cursor.execute(query, params)


def column_exists(cursor, is_postgres, table_name, column_name):
    if is_postgres:
        run_query(
            cursor,
            is_postgres,
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = ?
              AND column_name = ?
            """,
            (table_name, column_name),
        )
        return cursor.fetchone() is not None

    run_query(cursor, is_postgres, f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    return any(col[1] == column_name for col in columns)


def main():
    conn, is_postgres = get_connection()
    cursor = conn.cursor()

    id_type = "SERIAL PRIMARY KEY" if is_postgres else "INTEGER PRIMARY KEY AUTOINCREMENT"

    run_query(
        cursor,
        is_postgres,
        f"""
        CREATE TABLE IF NOT EXISTS users (
            id {id_type},
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'student',
            profile_pic TEXT
        )
        """,
    )

    run_query(
        cursor,
        is_postgres,
        f"""
        CREATE TABLE IF NOT EXISTS student_details (
            id {id_type},
            user_email TEXT,
            branch TEXT,
            projects INTEGER,
            internships INTEGER,
            skills TEXT,
            confidence INTEGER
        )
        """,
    )

    run_query(
        cursor,
        is_postgres,
        f"""
        CREATE TABLE IF NOT EXISTS quiz_results (
            id {id_type},
            user_email TEXT NOT NULL,
            category TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            taken_on TEXT NOT NULL
        )
        """,
    )

    run_query(
        cursor,
        is_postgres,
        f"""
        CREATE TABLE IF NOT EXISTS admin_users (
            id {id_type},
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_super_admin INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1
        )
        """,
    )

    if not column_exists(cursor, is_postgres, "users", "role"):
        run_query(cursor, is_postgres, "ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'student'")

    if not column_exists(cursor, is_postgres, "users", "profile_pic"):
        run_query(cursor, is_postgres, "ALTER TABLE users ADD COLUMN profile_pic TEXT")

    run_query(
        cursor,
        is_postgres,
        """
        INSERT INTO admin_users (name, email, password, is_super_admin, is_active)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT (email) DO NOTHING
        """,
        ("Permanent Admin", "admin@gmail.com", "admin123", 1, 1),
    )

    conn.commit()
    conn.close()
    print("Database initialization completed successfully.")


if __name__ == "__main__":
    main()
