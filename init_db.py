import sqlite3

# 1. CONNECT (This creates the file 'smartseat.db' if it doesn't exist)
conn = sqlite3.connect('smartseat.db')
cursor = conn.cursor()

# 2. CREATE TABLE (The Structure)
# We need columns for: Roll No, Name, Branch, and their Seat Location
cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_no TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        branch TEXT NOT NULL,
        seat_row INTEGER DEFAULT -1,
        seat_col INTEGER DEFAULT -1
    )
''')

# 3. ADD SOME DUMMY DATA (Optional - just to test)
# Let's add the 3 students we used for the C++ test
try:
    cursor.execute("INSERT INTO students (roll_no, name, branch) VALUES ('101', 'Amit', 'CSE')")
    cursor.execute("INSERT INTO students (roll_no, name, branch) VALUES ('102', 'Rahul', 'ECE')")
    cursor.execute("INSERT INTO students (roll_no, name, branch) VALUES ('103', 'Priya', 'CSE')")
    print("Dummy data added successfully.")
except sqlite3.IntegrityError:
    print("Data already exists. Skipping insertion.")

# 4. SAVE AND CLOSE
conn.commit()
conn.close()

print("Database 'smartseat.db' created successfully!")