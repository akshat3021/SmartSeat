# ============================================================
#  SmartSeat — app.py  (With Login & Registration)
# ============================================================

import os
import sqlite3
import subprocess

from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# Secret key is used to encrypt session cookies
# Change this to a random string before deploying!
app.secret_key = "smartseat_super_secret_2024"

DB_PATH     = "smartseat.db"
INPUT_FILE  = "input.txt"
OUTPUT_FILE = "output.txt"
SOLVER_PATH = "solver.exe"

# ============================================================
#  HELPER FUNCTIONS
# ============================================================
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    """Decorator — protects student routes. Redirects to /login if not logged in."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'roll_no' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    """Decorator — protects admin routes. Redirects to /admin_login if not admin."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            return redirect(url_for('admin_login_page'))
        return f(*args, **kwargs)
    return decorated


# ============================================================
#  AUTH ROUTES
# ============================================================

# ── Login page (GET) ──
@app.route("/login")
def login_page():
    # If already logged in, skip login page
    if 'roll_no' in session:
        return redirect(url_for('index'))
    return render_template("login.html")

# ── Register  POST /register ──
# Student enters roll_no + name + password
# We check roll_no exists in students table (admin must have uploaded it first)
# Then save the hashed password in users table
@app.route("/register", methods=["POST"])
def register():
    data     = request.get_json(silent=True) or {}
    roll_no  = data.get("roll_no", "").strip()
    name     = data.get("name", "").strip()
    password = data.get("password", "").strip()

    if not roll_no or not name or not password:
        return jsonify({"error": "All fields are required."}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    conn = get_db_connection()

    # Check roll_no exists in students table
    # Only students uploaded by admin can register
    student = conn.execute(
        "SELECT * FROM students WHERE roll_no = ?", (roll_no,)
    ).fetchone()

    if student is None:
        conn.close()
        return jsonify({
            "error": "Roll number not found. Make sure the admin has uploaded the student list first."
        }), 404

    # Check not already registered
    existing = conn.execute(
        "SELECT * FROM users WHERE roll_no = ?", (roll_no,)
    ).fetchone()

    if existing:
        conn.close()
        return jsonify({"error": "This roll number is already registered. Please login."}), 409

    # Hash password — NEVER store plain text passwords
    # generate_password_hash adds a random salt automatically
    hashed = generate_password_hash(password)

    conn.execute(
        "INSERT INTO users (roll_no, password_hash) VALUES (?, ?)",
        (roll_no, hashed)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Account created successfully! Please login."})


# ── Student Login  POST /login ──
@app.route("/login", methods=["POST"])
def login():
    data     = request.get_json(silent=True) or {}
    roll_no  = data.get("roll_no", "").strip()
    password = data.get("password", "")

    if not roll_no or not password:
        return jsonify({"error": "Please enter roll number and password."}), 400

    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE roll_no = ?", (roll_no,)
    ).fetchone()
    conn.close()

    if user is None:
        return jsonify({"error": "Roll number not registered. Please register first."}), 401

    # check_password_hash compares plaintext against the stored hash safely
    if not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Incorrect password. Please try again."}), 401

    # Save to session — Flask remembers this across requests
    session['roll_no'] = roll_no
    session['role']    = 'student'

    return jsonify({"message": "Login successful!", "redirect": "/"})


# ── Admin Login page (GET) ──
@app.route("/admin_login")
def admin_login_page():
    if session.get('role') == 'admin':
        return redirect(url_for('admin'))
    return render_template("admin_login.html")


# ── Admin Login  POST /admin_login ──
@app.route("/admin_login", methods=["POST"])
def admin_login():
    data     = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Please enter username and password."}), 400

    conn  = get_db_connection()
    admin = conn.execute(
        "SELECT * FROM admins WHERE username = ?", (username,)
    ).fetchone()
    conn.close()

    if admin is None or not check_password_hash(admin["password_hash"], password):
        return jsonify({"error": "Invalid username or password."}), 401

    session['username'] = username
    session['role']     = 'admin'

    return jsonify({"message": "Admin login successful!", "redirect": "/admin"})


# ── Logout  GET /logout ──
@app.route("/logout")
def logout():
    session.clear()     # wipe everything from session
    return redirect(url_for('login_page'))


# ============================================================
#  STUDENT ROUTES  (protected — must be logged in)
# ============================================================

@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/seat/<roll_no>")
@login_required
def get_seat(roll_no):
    # Students can only look up their OWN seat
    if session.get('roll_no') != roll_no:
        return jsonify({"error": "You can only view your own seat."}), 403

    conn    = get_db_connection()
    student = conn.execute(
        "SELECT * FROM students WHERE roll_no = ?", (roll_no,)
    ).fetchone()
    conn.close()

    if student is None:
        return jsonify({"error": f"Roll number '{roll_no}' not found."}), 404

    if student["seat_row"] == -1:
        return jsonify({"error": "Seats not assigned yet. Ask admin to run the solver."}), 400

    return jsonify({
        "roll_no" : student["roll_no"],
        "name"    : student["name"],
        "branch"  : student["branch"],
        "room_no" : student["room_no"],
        "row"     : student["seat_row"],
        "col"     : student["seat_col"],
        "display" : f"Room {student['room_no']} — Row {student['seat_row']+1}, Seat {student['seat_col']+1}"
    })


@app.route("/grid/<room_no>")
@login_required
def get_grid(room_no):
    conn = get_db_connection()
    room = conn.execute("SELECT * FROM rooms WHERE room_no = ?", (room_no,)).fetchone()
    if not room:
        conn.close()
        return jsonify({"error": f"Room {room_no} not found."}), 404

    students = conn.execute(
        "SELECT * FROM students WHERE room_no = ? AND seat_row != -1", (room_no,)
    ).fetchall()
    conn.close()

    seats = [{"roll_no": s["roll_no"], "name": s["name"],
              "branch": s["branch"], "row": s["seat_row"], "col": s["seat_col"]}
             for s in students]

    return jsonify({"room_no": room_no, "rows": room["rows"], "cols": room["cols"], "seats": seats})


# ============================================================
#  ADMIN ROUTES  (protected — must be admin)
# ============================================================

@app.route("/admin")
@admin_required
def admin():
    return render_template("admin.html")


@app.route("/upload_students", methods=["POST"])
@admin_required
def upload_students():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    content  = file.read().decode("utf-8")
    lines    = content.strip().split("\n")
    conn     = get_db_connection()
    cursor   = conn.cursor()
    cursor.execute("DELETE FROM students")
    inserted, errors = 0, []

    for i, line in enumerate(lines):
        line  = line.strip()
        if not line: continue
        parts = [p.strip() for p in line.split(",")]
        
        # We now expect 8 columns in the CSV!
        if len(parts) != 8:
            errors.append(f"Row {i+1} skipped — expected 8 columns: roll_no, name, father_name, enrollment_no, program, semester, branch, section"); continue
        
        roll_no, name, father_name, enrollment_no, program, semester, branch, section = parts
        branch = branch.upper()
        
        try:
            cursor.execute("""
                INSERT INTO students (roll_no, name, father_name, enrollment_no, program, semester, branch, section) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (roll_no, name, father_name, enrollment_no, program, semester, branch, section)
            )
            inserted += 1
        except sqlite3.IntegrityError:
            errors.append(f"Row {i+1}: roll_no '{roll_no}' duplicate, skipped.")

    conn.commit()
    conn.close()
    return jsonify({"message": f"{inserted} students uploaded.", "errors": errors})

# ----------------------------------------------------

@app.route("/admit_card/<roll_no>")
@login_required
def admit_card(roll_no):
    if session.get("roll_no") != roll_no:
        return jsonify({"error": "You can only download your own admit card."}), 403

    conn    = get_db_connection()
    student = conn.execute("SELECT * FROM students WHERE roll_no = ?", (roll_no,)).fetchone()
    exam    = conn.execute("SELECT * FROM exams ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()

    if not student:
        return jsonify({"error": "Student not found."}), 404
    if student["seat_row"] == -1:
        return jsonify({"error": "Seats not assigned yet."}), 400

    # Sending ALL the new data to the frontend PDF generator
    return jsonify({
        "roll_no"      : student["roll_no"],
        "name"         : student["name"],
        "father_name"  : student["father_name"],
        "enrollment_no": student["enrollment_no"],
        "program"      : student["program"],
        "semester"     : student["semester"],
        "branch"       : student["branch"],
        "section"      : student["section"],
        "room_no"      : student["room_no"],
        "row"          : student["seat_row"],
        "col"          : student["seat_col"],
        "seat_display" : f"Row {student['seat_row']+1}, Seat {student['seat_col']+1}",
        "exam_name"    : exam["exam_name"] if exam else "Examination",
        "subject"      : exam["subject"]   if exam else "",
        "exam_date"    : exam["exam_date"] if exam else ""
    })


@app.route("/upload_rooms", methods=["POST"])
@admin_required
def upload_rooms():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    content  = file.read().decode("utf-8")
    lines    = content.strip().split("\n")
    conn     = get_db_connection()
    cursor   = conn.cursor()
    cursor.execute("DELETE FROM rooms")
    inserted, errors = 0, []

    for i, line in enumerate(lines):
        line  = line.strip()
        if not line: continue
        parts = line.split(",")
        if len(parts) != 3:
            errors.append(f"Row {i+1} skipped — expected room_no,rows,cols"); continue
        room_no = parts[0].strip()
        try:
            rows = int(parts[1].strip())
            cols = int(parts[2].strip())
        except ValueError:
            errors.append(f"Row {i+1}: rows/cols must be numbers"); continue
        try:
            cursor.execute("INSERT INTO rooms (room_no, rows, cols) VALUES (?, ?, ?)",
                           (room_no, rows, cols))
            inserted += 1
        except sqlite3.IntegrityError:
            errors.append(f"Row {i+1}: room '{room_no}' duplicate, skipped.")

    conn.commit()
    conn.close()
    return jsonify({"message": f"{inserted} rooms uploaded.", "errors": errors})


@app.route("/run", methods=["POST"])
@admin_required
def run_solver():
    data        = request.get_json(silent=True) or {}
    strict_mode = int(data.get("strict_mode", 0))

    conn     = get_db_connection()
    rooms    = conn.execute("SELECT * FROM rooms ORDER BY room_no").fetchall()
    students = conn.execute("SELECT * FROM students").fetchall()

    if not rooms:
        conn.close()
        return jsonify({"error": "No rooms uploaded. Upload a rooms.csv first."}), 400
    if not students:
        conn.close()
        return jsonify({"error": "No students uploaded. Upload a students.csv first."}), 400

    total_capacity = sum(r["rows"] * r["cols"] for r in rooms)
    if len(students) > total_capacity:
        conn.close()
        return jsonify({"error": f"Too many students ({len(students)}) for total capacity ({total_capacity})."}), 400

    students     = list(students)
    room_list    = list(rooms)
    room_buckets = {r["room_no"]: [] for r in room_list}

    # Fill each room sequentially — move to next room only when current is full
    # OLD round-robin caused IndexError when room_index jumped past list end
    room_index = 0
    for student in students:
        # Advance past any full rooms
        while room_index < len(room_list) and \
              len(room_buckets[room_list[room_index]["room_no"]]) >= \
              room_list[room_index]["rows"] * room_list[room_index]["cols"]:
            room_index += 1

        if room_index >= len(room_list):
            conn.close()
            return jsonify({"error": "Not enough capacity. Upload more rooms."}), 400

        room_buckets[room_list[room_index]["room_no"]].append(student)

    cursor     = conn.cursor()
    rooms_done = 0

    for room in room_list:
        room_no = room["room_no"]
        batch   = room_buckets[room_no]
        if not batch: continue

        with open(INPUT_FILE, "w") as f:
            f.write(f"{room['rows']} {room['cols']} {strict_mode}\n")
            for s in batch:
                f.write(f"{s['id']} {s['branch']}\n")

        try:
            result = subprocess.run([SOLVER_PATH], capture_output=True, text=True, timeout=30)
        except FileNotFoundError:
            conn.close()
            return jsonify({"error": "solver.exe not found."}), 500
        except subprocess.TimeoutExpired:
            conn.close()
            return jsonify({"error": f"Solver timed out on room {room_no}."}), 500

        if "Failure" in result.stdout:
            conn.close()
            return jsonify({"error": f"Room {room_no}: could not arrange students. Try a larger room."}), 400

        if not os.path.exists(OUTPUT_FILE):
            conn.close()
            return jsonify({"error": f"output.txt missing after room {room_no}."}), 500

        updated_count = 0
        with open(OUTPUT_FILE, "r") as f:
            output_lines = f.readlines()

        # DEBUG: print first 3 lines of output.txt to terminal
        print(f"[DEBUG] Room {room_no} output.txt first 3 lines: {output_lines[:3]}")

        for line in output_lines:
            line = line.strip()
            if not line: continue
            parts = line.split()
            if len(parts) != 4: continue
            student_id = int(parts[0])
            seat_row   = int(parts[2])
            seat_col   = int(parts[3])
            cursor.execute(
                "UPDATE students SET room_no=?, seat_row=?, seat_col=? WHERE id=?",
                (room_no, seat_row, seat_col, student_id)
            )
            updated_count += cursor.rowcount   # rowcount = 1 if UPDATE matched, 0 if not

        print(f"[DEBUG] Room {room_no}: {updated_count} rows updated in DB")
        rooms_done += 1

    conn.commit()

    # DEBUG: verify commit actually saved
    verify = conn.execute("SELECT COUNT(*) FROM students WHERE seat_row != -1").fetchone()[0]
    print(f"[DEBUG] After commit: {verify} students have seats assigned")
    conn.close()

    return jsonify({
        "message"    : f"Seats assigned for {len(students)} students across {rooms_done} rooms!",
        "strict_mode": strict_mode,
        "rooms_done" : rooms_done
    })


@app.route("/students")
@admin_required
def get_all_students():
    conn     = get_db_connection()
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()
    return jsonify([dict(s) for s in students])


@app.route("/rooms")
@admin_required
def get_rooms():
    conn  = get_db_connection()
    rooms = conn.execute("SELECT * FROM rooms ORDER BY room_no").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rooms])




# ============================================================
#  ROUTE: Set Exam Info  POST /set_exam  (admin only)
#  Admin sets exam name, subject and date before running solver
# ============================================================
@app.route("/set_exam", methods=["POST"])
@admin_required
def set_exam():
    data    = request.get_json(silent=True) or {}
    name    = data.get("exam_name", "").strip()
    subject = data.get("subject", "").strip()
    date    = data.get("exam_date", "").strip()

    if not name or not date:
        return jsonify({"error": "Exam name and date are required."}), 400

    conn   = get_db_connection()
    cursor = conn.cursor()

    # We only keep one current exam at a time
    cursor.execute("DELETE FROM exams")
    cursor.execute(
        "INSERT INTO exams (exam_name, subject, exam_date) VALUES (?, ?, ?)",
        (name, subject, date)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": f"Exam info saved: {name} on {date}"})


# ── GET current exam info ──
@app.route("/exam_info")
def exam_info():
    conn = get_db_connection()
    exam = conn.execute("SELECT * FROM exams ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    if not exam:
        return jsonify({"exam_name": "", "subject": "", "exam_date": ""})
    return jsonify(dict(exam))


# ============================================================
#  ROUTE: Stats  GET /stats  (admin only)
#  Returns summary stats for the dashboard
# ============================================================
@app.route("/stats")
@admin_required
def get_stats():
    conn = get_db_connection()

    total_students  = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    seated_students = conn.execute("SELECT COUNT(*) FROM students WHERE seat_row != -1").fetchone()[0]
    total_rooms     = conn.execute("SELECT COUNT(*) FROM rooms").fetchone()[0]
    total_capacity  = conn.execute("SELECT SUM(rows * cols) FROM rooms").fetchone()[0] or 0

    # Branch-wise breakdown
    branches = conn.execute(
        "SELECT branch, COUNT(*) as count FROM students GROUP BY branch ORDER BY count DESC"
    ).fetchall()

    # Room-wise occupancy
    rooms = conn.execute(
        """SELECT r.room_no, r.rows, r.cols,
           COUNT(s.id) as occupied
           FROM rooms r
           LEFT JOIN students s ON s.room_no = r.room_no AND s.seat_row != -1
           GROUP BY r.room_no ORDER BY r.room_no"""
    ).fetchall()

    conn.close()

    return jsonify({
        "total_students" : total_students,
        "seated_students": seated_students,
        "pending"        : total_students - seated_students,
        "total_rooms"    : total_rooms,
        "total_capacity" : total_capacity,
        "utilization"    : round((seated_students / total_capacity * 100), 1) if total_capacity else 0,
        "branches"       : [{"branch": b["branch"], "count": b["count"]} for b in branches],
        "rooms"          : [{"room_no": r["room_no"], "rows": r["rows"],
                             "cols": r["cols"], "occupied": r["occupied"],
                             "capacity": r["rows"] * r["cols"]} for r in rooms]
    })

# ============================================================
#  ROUTE: Seating Chart  GET /seating_chart  (admin only)
#  Returns full room-wise arrangement for printing
# ============================================================
@app.route("/seating_chart")
@admin_required
def seating_chart():
    conn  = get_db_connection()
    rooms = conn.execute("SELECT * FROM rooms ORDER BY room_no").fetchall()
    exam  = conn.execute("SELECT * FROM exams ORDER BY id DESC LIMIT 1").fetchone()

    chart = []
    for room in rooms:
        students = conn.execute(
            """SELECT roll_no, name, branch, seat_row, seat_col
               FROM students WHERE room_no = ? AND seat_row != -1
               ORDER BY seat_row, seat_col""",
            (room["room_no"],)
        ).fetchall()

        chart.append({
            "room_no" : room["room_no"],
            "rows"    : room["rows"],
            "cols"    : room["cols"],
            "students": [dict(s) for s in students]
        })

    conn.close()
    return jsonify({
        "exam_name": exam["exam_name"] if exam else "Examination",
        "subject"  : exam["subject"]   if exam else "",
        "exam_date": exam["exam_date"] if exam else "",
        "rooms"    : chart
    })

if __name__ == "__main__":
    app.run(debug=True)