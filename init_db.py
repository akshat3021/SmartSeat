import sqlite3
from werkzeug.security import generate_password_hash

conn   = sqlite3.connect('smartseat.db')
cursor = conn.cursor()

# ── TABLE 1: students (UPDATED WITH ALL GEHU FIELDS) ──
cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_no       TEXT NOT NULL UNIQUE,
        name          TEXT NOT NULL,
        father_name   TEXT DEFAULT 'N/A',
        enrollment_no TEXT DEFAULT 'N/A',
        program       TEXT DEFAULT 'BACHELOR OF TECHNOLOGY',
        semester      INTEGER DEFAULT 4,
        branch        TEXT NOT NULL,
        section       TEXT DEFAULT 'A',
        room_no       TEXT DEFAULT '',
        seat_row      INTEGER DEFAULT -1,
        seat_col      INTEGER DEFAULT -1
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

# ── TABLE 3: users ──
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_no       TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL
    )
''')

# ── TABLE 3.5: exams ──
cursor.execute('''
    CREATE TABLE IF NOT EXISTS exams (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_name TEXT NOT NULL,
        subject   TEXT DEFAULT '',
        exam_date TEXT NOT NULL
    )
''')

# ── TABLE 4: admins ──
cursor.execute('''
    CREATE TABLE IF NOT EXISTS admins (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        username      TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL
    )
''')

# ── CREATE DEFAULT ADMIN ACCOUNT ──
try:
    hashed = generate_password_hash('admin123')
    cursor.execute(
        "INSERT INTO admins (username, password_hash) VALUES (?, ?)",
        ('admin', hashed)
    )
except sqlite3.IntegrityError:
    pass

# ── DUMMY STUDENT DATA (Updated format) ──
try:
    cursor.execute("INSERT INTO students (roll_no, name, father_name, enrollment_no, program, semester, branch, section) VALUES ('101', 'Akshat Aswal', 'Mr. Aswal', 'GE202401', 'BACHELOR OF TECHNOLOGY', 4, 'CSE', 'A2')")
    cursor.execute("INSERT INTO students (roll_no, name, father_name, enrollment_no, program, semester, branch, section) VALUES ('102', 'Yasharth Dhanai', 'Mr. Dhanai', 'GE202402', 'BACHELOR OF TECHNOLOGY', 4, 'CSE', 'A2')")
    cursor.execute("INSERT INTO students (roll_no, name, father_name, enrollment_no, program, semester, branch, section) VALUES ('103', 'Mohit Mamgain', 'Mr. Mamgain', 'GE202403', 'BACHELOR OF TECHNOLOGY', 4, 'CSE', 'A2')")
    print("Dummy students added.")
except sqlite3.IntegrityError:
    pass

# ── DUMMY ROOMS ──
try:
    cursor.execute("INSERT INTO rooms (room_no, rows, cols) VALUES ('301', 5, 6)")
    cursor.execute("INSERT INTO rooms (room_no, rows, cols) VALUES ('302', 4, 8)")
    print("Dummy rooms added.")
except sqlite3.IntegrityError:
    pass

conn.commit()
conn.close()
print("Database ready! All GEHU fields added.")