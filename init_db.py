import sqlite3
from werkzeug.security import generate_password_hash

conn   = sqlite3.connect('smartseat.db')
cursor = conn.cursor()

# ── TABLE 1: students ──
cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_no  TEXT NOT NULL UNIQUE,
        name     TEXT NOT NULL,
        branch   TEXT NOT NULL,
        room_no  TEXT DEFAULT '',
        seat_row INTEGER DEFAULT -1,
        seat_col INTEGER DEFAULT -1
    )
''')

# ── TABLE 2: rooms ──
cursor.execute('''
    CREATE TABLE IF NOT EXISTS rooms (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        room_no TEXT NOT NULL UNIQUE,
        rows    INTEGER NOT NULL,
        cols    INTEGER NOT NULL
    )
''')

# ── TABLE 3: users ── (NEW)
# Stores login credentials for students
# roll_no links to the students table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_no      TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL
    )
''')

# ── TABLE 3.5: exams ── (NEW)
# Stores current exam name, subject, date set by admin
cursor.execute('''
    CREATE TABLE IF NOT EXISTS exams (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_name TEXT NOT NULL,
        subject   TEXT DEFAULT '',
        exam_date TEXT NOT NULL
    )
''')

# ── TABLE 4: admins ── (NEW)
# Separate table for admin accounts
# Passwords are hashed — never stored as plain text
cursor.execute('''
    CREATE TABLE IF NOT EXISTS admins (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        username      TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL
    )
''')

# ── CREATE DEFAULT ADMIN ACCOUNT ──
# Username: admin  |  Password: admin123
# Change this password before deploying!
try:
    hashed = generate_password_hash('admin123')
    cursor.execute(
        "INSERT INTO admins (username, password_hash) VALUES (?, ?)",
        ('admin', hashed)
    )
    print("Default admin created — username: admin, password: admin123")
    print("IMPORTANT: Change this password before deploying!")
except sqlite3.IntegrityError:
    print("Admin already exists, skipping.")

# ── DUMMY STUDENT DATA ──
try:
    cursor.execute("INSERT INTO students (roll_no, name, branch) VALUES ('101', 'Akshat Aswal',   'CSE')")
    cursor.execute("INSERT INTO students (roll_no, name, branch) VALUES ('102', 'Yasharth Dhanai','CSE')")
    cursor.execute("INSERT INTO students (roll_no, name, branch) VALUES ('103', 'Mohit Mamgain',  'CSE')")
    print("Dummy students added.")
except sqlite3.IntegrityError:
    print("Students already exist, skipping.")

# ── DUMMY ROOMS ──
try:
    cursor.execute("INSERT INTO rooms (room_no, rows, cols) VALUES ('301', 5, 6)")
    cursor.execute("INSERT INTO rooms (room_no, rows, cols) VALUES ('302', 4, 8)")
    print("Dummy rooms added.")
except sqlite3.IntegrityError:
    print("Rooms already exist, skipping.")

conn.commit()
conn.close()
print("Database ready!")