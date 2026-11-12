from flask import Flask, request, jsonify, session, render_template, send_from_directory
from flask_cors import CORS
import mysql.connector
from functools import wraps
import contextlib
import random
import datetime
from decimal import Decimal

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "campusride_secure_session_key"

# Enable CORS (with support for session cookies)
CORS(app, supports_credentials=True)

# -----------------------------
# JSON Serialization Helper
# -----------------------------
def make_json_serializable(data):
    if isinstance(data, list):
        return [make_json_serializable(x) for x in data]
    elif isinstance(data, dict):
        return {k: make_json_serializable(v) for k, v in data.items()}
    elif isinstance(data, Decimal):
        return float(data)
    elif isinstance(data, datetime.timedelta):
        total_seconds = int(data.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02d}:{minutes:02d}"
    elif isinstance(data, datetime.time):
        return data.strftime("%H:%M")
    elif isinstance(data, datetime.date):
        return data.isoformat()
    elif isinstance(data, datetime.datetime):
        return data.isoformat()
    return data

# -----------------------------
# Database Connection Context
# -----------------------------
@contextlib.contextmanager
def db_cursor():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="busmg"
    )
    cursor = conn.cursor(dictionary=True)
    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

# -----------------------------
# Database Setup & Migrations
# -----------------------------
def init_db():
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="root")
        cursor = conn.cursor()
        
        # Create database if not exists
        cursor.execute("CREATE DATABASE IF NOT EXISTS busmg")
        cursor.execute("USE busmg")
        
        # 1. Create admins table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            admin_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
        ''')

        # Create login_logs table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS login_logs (
            log_id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(100) NOT NULL,
            role VARCHAR(50) NOT NULL,
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(50) DEFAULT 'Success',
            ip_address VARCHAR(45)
        )
        ''')

        # Create schedules table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedules (
            schedule_id INT AUTO_INCREMENT PRIMARY KEY,
            bus_id INT,
            route_id INT,
            arrival_time_1st_shift TIME,
            arrival_time_2nd_shift TIME,
            FOREIGN KEY (bus_id) REFERENCES buses(bus_id),
            FOREIGN KEY (route_id) REFERENCES routes(route_id)
        )
        ''')
        
        # 2. Check and alter students table for password
        cursor.execute("DESCRIBE students")
        student_cols = [x[0] for x in cursor.fetchall()]
        if 'password' not in student_cols:
            cursor.execute("ALTER TABLE students ADD COLUMN password VARCHAR(255) DEFAULT 'password'")
            
        # 3. Check and alter drivers table for email & password
        cursor.execute("DESCRIBE drivers")
        driver_cols = [x[0] for x in cursor.fetchall()]
        if 'email' not in driver_cols:
            cursor.execute("ALTER TABLE drivers ADD COLUMN email VARCHAR(100) UNIQUE")
        if 'password' not in driver_cols:
            cursor.execute("ALTER TABLE drivers ADD COLUMN password VARCHAR(255) DEFAULT 'password'")
            
        # 4. Check and alter buses table for latitude & longitude
        cursor.execute("DESCRIBE buses")
        bus_cols = [x[0] for x in cursor.fetchall()]
        if 'latitude' not in bus_cols:
            cursor.execute("ALTER TABLE buses ADD COLUMN latitude DECIMAL(10, 8) DEFAULT 22.7196")
        if 'longitude' not in bus_cols:
            cursor.execute("ALTER TABLE buses ADD COLUMN longitude DECIMAL(10, 8) DEFAULT 75.8577")
            
        # 5. Seed default admin account
        cursor.execute("SELECT * FROM admins WHERE username=%s", ('admin@campusride.edu',))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO admins (username, password) VALUES (%s, %s)", ('admin@campusride.edu', 'admin123'))
            
        # 6. Seed default student account
        cursor.execute("SELECT * FROM students WHERE email=%s", ('student@campusride.edu',))
        student = cursor.fetchone()
        if not student:
            cursor.execute("INSERT INTO students (name, email, password) VALUES (%s, %s, %s)", ('Krishna Patel', 'student@campusride.edu', 'password'))
            student_id = cursor.lastrowid
        else:
            cursor.execute("SELECT student_id FROM students WHERE email=%s", ('student@campusride.edu',))
            student_id = cursor.fetchone()[0]
            
        # 7. Seed student route mapping
        cursor.execute("SELECT * FROM student_routes WHERE student_id=%s", (student_id,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO student_routes (student_id, route_id) VALUES (%s, 1)", (student_id,))
            
        # 8. Update driver 1 (Shri Santosh Choudhary) with login credentials
        cursor.execute("UPDATE drivers SET email=%s, password=%s WHERE driver_id=1", ('driver@campusride.edu', 'password'))

        # 9. Seed schedules mapping (for default bus and routes)
        cursor.execute("SELECT * FROM schedules LIMIT 1")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO schedules (bus_id, route_id, arrival_time_1st_shift, arrival_time_2nd_shift) VALUES (1, 1, '08:10:00', '10:15:00')")
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialized and migrated successfully.")
    except Exception as e:
        print("Database migration failed on startup:", e)

# Run migrations
init_db()

# -----------------------------
# Authentication Guard Decorator
# -----------------------------
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                return jsonify({"error": "Unauthorized. Please log in."}), 401
            if role and session['user']['role'] != role:
                return jsonify({"error": "Forbidden. Insufficient permissions."}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# -----------------------------
# Frontend Routes
# -----------------------------
@app.route('/')
def home():
    return render_template('index011.html')

# Explicit fallbacks for serving JS/CSS from the static directory directly
@app.route('/stlye011.css')
def serve_css():
    return send_from_directory('static', 'stlye011.css')

@app.route('/script011.js')
def serve_js():
    return send_from_directory('static', 'script011.js')

# -----------------------------
# Authentication API
# -----------------------------
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Missing email or password"}), 400
    
    email = data['email'].strip().lower()
    password = data['password']
    role = data.get('role')
    ip_addr = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    try:
        with db_cursor() as cursor:
            # 1. Admin login
            if not role or role == 'admin':
                cursor.execute("SELECT * FROM admins WHERE username=%s AND password=%s", (email, password))
                admin = cursor.fetchone()
                if admin:
                    session['user'] = {
                        'id': admin['admin_id'],
                        'email': admin['username'],
                        'name': 'System Administrator',
                        'role': 'admin'
                    }
                    cursor.execute("INSERT INTO login_logs (email, role, status, ip_address) VALUES (%s, %s, %s, %s)",
                                   (email, 'admin', 'Success', ip_addr))
                    return jsonify({"success": True, "message": "Admin login successful", "user": session['user']})
            
            # 2. Student login
            if not role or role == 'student':
                cursor.execute("SELECT * FROM students WHERE email=%s AND password=%s", (email, password))
                student = cursor.fetchone()
                if student:
                    session['user'] = {
                        'id': student['student_id'],
                        'email': student['email'],
                        'name': student['name'],
                        'role': 'student'
                    }
                    cursor.execute("INSERT INTO login_logs (email, role, status, ip_address) VALUES (%s, %s, %s, %s)",
                                   (email, 'student', 'Success', ip_addr))
                    return jsonify({"success": True, "message": "Student login successful", "user": session['user']})
            
            # 3. Driver login
            if not role or role == 'driver':
                cursor.execute("SELECT * FROM drivers WHERE email=%s AND password=%s", (email, password))
                driver = cursor.fetchone()
                if driver:
                    session['user'] = {
                        'id': driver['driver_id'],
                        'email': driver['email'],
                        'name': driver['name'],
                        'role': 'driver'
                    }
                    cursor.execute("INSERT INTO login_logs (email, role, status, ip_address) VALUES (%s, %s, %s, %s)",
                                   (email, 'driver', 'Success', ip_addr))
                    return jsonify({"success": True, "message": "Driver login successful", "user": session['user']})
                
            # Log failure
            cursor.execute("INSERT INTO login_logs (email, role, status, ip_address) VALUES (%s, %s, %s, %s)",
                           (email, 'unknown', 'Failed - Invalid Credentials', ip_addr))
                
        return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        try:
            with db_cursor() as cursor:
                cursor.execute("INSERT INTO login_logs (email, role, status, ip_address) VALUES (%s, %s, %s, %s)",
                               (email, 'unknown', f'Failed - DB Error: {str(e)[:40]}', ip_addr))
        except:
            pass
        return jsonify({"error": f"Database error during login: {str(e)}"}), 500

# -----------------------------
# Student Registration API
# -----------------------------
@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.json
    role = data.get('role', 'student')
    
    if not data or 'name' not in data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Missing required fields"}), 400
        
    if role == 'student' and 'route_id' not in data:
        return jsonify({"error": "Missing route_id for student"}), 400
    
    name = data['name'].strip()
    email = data['email'].strip().lower()
    password = data['password']
    
    if not name or not email or not password:
        return jsonify({"error": "All fields are required"}), 400
        
    try:
        with db_cursor() as cursor:
            # Check if email is already registered anywhere
            cursor.execute("SELECT email FROM students WHERE email = %s", (email,))
            if cursor.fetchone():
                return jsonify({"error": "Email already registered"}), 400
                
            cursor.execute("SELECT username FROM admins WHERE username = %s", (email,))
            if cursor.fetchone():
                return jsonify({"error": "Email registered as administrator"}), 400
                
            cursor.execute("SELECT email FROM drivers WHERE email = %s", (email,))
            if cursor.fetchone():
                return jsonify({"error": "Email registered as driver"}), 400
                
            ip_addr = request.headers.get('X-Forwarded-For', request.remote_addr)

            if role == 'admin':
                # Insert admin
                cursor.execute("INSERT INTO admins (username, password) VALUES (%s, %s)", (email, password))
                admin_id = cursor.lastrowid
                
                # Log registration
                cursor.execute("INSERT INTO login_logs (email, role, status, ip_address) VALUES (%s, %s, %s, %s)",
                               (email, 'admin', 'Registered New Admin Account', ip_addr))
                
                # Auto-login
                session['user'] = {
                    'id': admin_id,
                    'email': email,
                    'name': name,
                    'role': 'admin'
                }
                
                return jsonify({"success": True, "message": "Admin registration successful!", "user": session['user']})
            
            else:
                # Insert student
                route_id = data['route_id']
                cursor.execute("INSERT INTO students (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
                student_id = cursor.lastrowid
                
                # Map student to route
                cursor.execute("INSERT INTO student_routes (student_id, route_id) VALUES (%s, %s)", (student_id, route_id))
                
                # Log registration
                cursor.execute("INSERT INTO login_logs (email, role, status, ip_address) VALUES (%s, %s, %s, %s)",
                               (email, 'student', 'Registered New Account', ip_addr))
                
                # Auto-login
                session['user'] = {
                    'id': student_id,
                    'email': email,
                    'name': name,
                    'role': 'student'
                }
                
                return jsonify({"success": True, "message": "Registration successful!", "user": session['user']})

    except Exception as e:
        return jsonify({"error": f"Database error during registration: {str(e)}"}), 500

# -----------------------------
# Search API (Routes, Buses, Stops)
# -----------------------------
@app.route('/api/search', methods=['GET'])
@login_required()
def search_transit():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])
        
    try:
        with db_cursor() as cursor:
            # Find routes matching directly, or matching containing stops, or matching active buses
            cursor.execute("""
                SELECT DISTINCT r.route_id, r.route_name, r.start_point, r.end_point 
                FROM routes r
                LEFT JOIN route_stops rs ON r.route_id = rs.route_id
                LEFT JOIN stops s ON rs.stop_id = s.stop_id
                LEFT JOIN schedules sch ON r.route_id = sch.route_id
                LEFT JOIN buses b ON sch.bus_id = b.bus_id
                WHERE r.route_name LIKE %s 
                   OR r.start_point LIKE %s 
                   OR r.end_point LIKE %s
                   OR s.stop_name LIKE %s
                   OR b.bus_number LIKE %s
            """, (f"%{q}%", f"%{q}%", f"%{q}%", f"%{q}%", f"%{q}%"))
            routes = cursor.fetchall()
            
            results = []
            for r in routes:
                route_id = r['route_id']
                
                # Fetch buses on this route
                cursor.execute("""
                    SELECT b.bus_id, b.bus_number, b.capacity, b.latitude, b.longitude, 
                           d.name AS driver, d.phone_number AS driver_phone,
                           s.arrival_time_1st_shift AS departure, s.arrival_time_2nd_shift AS arrival 
                    FROM schedules s 
                    JOIN buses b ON s.bus_id = b.bus_id 
                    LEFT JOIN drivers d ON b.driver_id = d.driver_id 
                    WHERE s.route_id = %s
                """, (route_id,))
                buses = cursor.fetchall()
                
                # Fetch stops for this route
                cursor.execute("""
                    SELECT s.stop_name 
                    FROM route_stops rs 
                    JOIN stops s ON rs.stop_id = s.stop_id 
                    WHERE rs.route_id = %s 
                    ORDER BY rs.stop_order ASC
                """, (route_id,))
                stops = [x['stop_name'] for x in cursor.fetchall()]
                
                results.append({
                    "route": r,
                    "buses": buses,
                    "stops": stops
                })
                
            return jsonify(make_json_serializable(results))
    except Exception as e:
        return jsonify({"error": f"Search query failed: {str(e)}"}), 500

# -----------------------------
# Admin Audit Logs API
# -----------------------------
@app.route('/api/admin/logs', methods=['GET'])
@login_required(role='admin')
def get_admin_logs():
    try:
        with db_cursor() as cursor:
            cursor.execute("SELECT * FROM login_logs ORDER BY login_time DESC LIMIT 100")
            logs = cursor.fetchall()
            return jsonify(make_json_serializable(logs))
    except Exception as e:
        return jsonify({"error": f"Failed to fetch audit logs: {str(e)}"}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({"success": True, "message": "Logged out successfully"})

@app.route('/api/session', methods=['GET'])
def get_session():
    if 'user' in session:
        return jsonify({"logged_in": True, "user": session['user']})
    return jsonify({"logged_in": False})

# -----------------------------
# Admin CRUD: Notices
# -----------------------------
@app.route('/api/notices', methods=['GET'])
def get_notices():
    try:
        with db_cursor() as cursor:
            cursor.execute("SELECT * FROM notices ORDER BY created_at DESC")
            result = cursor.fetchall()
            return jsonify(make_json_serializable(result))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/notices', methods=['POST'])
@login_required(role='admin')
def add_notice():
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "Message content is required"}), 400
    
    title = data.get('title', 'General Alert')
    message = data['message']
    expiry_date = data.get('expiry_date')
    target_route_id = data.get('target_route_id')
    
    try:
        with db_cursor() as cursor:
            cursor.execute(
                "INSERT INTO notices (title, message, expiry_date, target_route_id) VALUES (%s, %s, %s, %s)",
                (title, message, expiry_date, target_route_id)
            )
            return jsonify({"success": True, "message": "Notice published successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/notices/<int:notice_id>', methods=['PUT'])
@login_required(role='admin')
def update_notice(notice_id):
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "Message content is required"}), 400
    
    title = data.get('title', 'General Alert')
    message = data['message']
    expiry_date = data.get('expiry_date')
    target_route_id = data.get('target_route_id')
    
    try:
        with db_cursor() as cursor:
            cursor.execute(
                "UPDATE notices SET title=%s, message=%s, expiry_date=%s, target_route_id=%s WHERE notice_id=%s",
                (title, message, expiry_date, target_route_id, notice_id)
            )
            return jsonify({"success": True, "message": "Notice updated successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/notices/<int:notice_id>', methods=['DELETE'])
@login_required(role='admin')
def delete_notice(notice_id):
    try:
        with db_cursor() as cursor:
            cursor.execute("DELETE FROM notices WHERE notice_id=%s", (notice_id,))
            return jsonify({"success": True, "message": "Notice deleted successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------
# Admin CRUD: Drivers
# -----------------------------
@app.route('/api/drivers', methods=['GET'])
@login_required(role='admin')
def get_drivers():
    try:
        with db_cursor() as cursor:
            cursor.execute("SELECT * FROM drivers")
            result = cursor.fetchall()
            return jsonify(make_json_serializable(result))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/drivers', methods=['POST'])
@login_required(role='admin')
def add_driver():
    data = request.json
    if not data or 'name' not in data or 'phone_number' not in data:
        return jsonify({"error": "Name and phone number are required"}), 400
    
    name = data['name']
    phone_number = data['phone_number']
    experience_years = data.get('experience_years')
    email = data.get('email')
    password = data.get('password', 'password')
    
    try:
        with db_cursor() as cursor:
            cursor.execute(
                "INSERT INTO drivers (name, phone_number, experience_years, email, password) VALUES (%s, %s, %s, %s, %s)",
                (name, phone_number, experience_years, email, password)
            )
            return jsonify({"success": True, "message": "Driver added successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/drivers/<int:driver_id>', methods=['PUT'])
@login_required(role='admin')
def update_driver(driver_id):
    data = request.json
    if not data or 'name' not in data or 'phone_number' not in data:
        return jsonify({"error": "Name and phone number are required"}), 400
    
    name = data['name']
    phone_number = data['phone_number']
    experience_years = data.get('experience_years')
    email = data.get('email')
    password = data.get('password')
    
    try:
        with db_cursor() as cursor:
            if password:
                cursor.execute(
                    "UPDATE drivers SET name=%s, phone_number=%s, experience_years=%s, email=%s, password=%s WHERE driver_id=%s",
                    (name, phone_number, experience_years, email, password, driver_id)
                )
            else:
                cursor.execute(
                    "UPDATE drivers SET name=%s, phone_number=%s, experience_years=%s, email=%s WHERE driver_id=%s",
                    (name, phone_number, experience_years, email, driver_id)
                )
            return jsonify({"success": True, "message": "Driver updated successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/drivers/<int:driver_id>', methods=['DELETE'])
@login_required(role='admin')
def delete_driver(driver_id):
    try:
        with db_cursor() as cursor:
            cursor.execute("DELETE FROM drivers WHERE driver_id=%s", (driver_id,))
            return jsonify({"success": True, "message": "Driver deleted successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------
# Admin CRUD: Buses
# -----------------------------
@app.route('/api/buses', methods=['GET'])
def get_buses():
    try:
        with db_cursor() as cursor:
            # Join with Drivers to provide driver names in response
            cursor.execute("""
                SELECT b.*, d.name AS driver_name, d.phone_number AS driver_phone
                FROM buses b 
                LEFT JOIN drivers d ON b.driver_id = d.driver_id
            """)
            result = cursor.fetchall()
            return jsonify(make_json_serializable(result))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/buses', methods=['POST'])
@login_required(role='admin')
def add_bus():
    data = request.json
    if not data or 'bus_number' not in data:
        return jsonify({"error": "Bus number is required"}), 400
    
    bus_number = data['bus_number']
    capacity = data.get('capacity', 52)
    driver_id = data.get('driver_id')
    latitude = data.get('latitude', 22.7196)
    longitude = data.get('longitude', 75.8577)
    
    try:
        with db_cursor() as cursor:
            # If driver_name was provided, find driver_id
            driver_name = data.get('driver_name')
            if driver_name and not driver_id:
                cursor.execute("SELECT driver_id FROM drivers WHERE name=%s", (driver_name,))
                dr = cursor.fetchone()
                if dr:
                    driver_id = dr['driver_id']
                else:
                    # Create new driver dynamically if needed or fail
                    cursor.execute("INSERT INTO drivers (name, phone_number) VALUES (%s, %s)", 
                                   (driver_name, str(random.randint(1000000000, 9999999999))))
                    driver_id = cursor.lastrowid
            
            cursor.execute(
                "INSERT INTO buses (bus_number, capacity, driver_id, latitude, longitude) VALUES (%s, %s, %s, %s, %s)",
                (bus_number, capacity, driver_id, latitude, longitude)
            )
            bus_id = cursor.lastrowid
            
            # Map default schedule to Route 1 so it appears for students
            cursor.execute("INSERT INTO schedules (bus_id, route_id, arrival_time_1st_shift, arrival_time_2nd_shift) VALUES (%s, 1, '08:10:00', '10:15:00')", (bus_id,))
            
            return jsonify({"success": True, "message": "Bus registered and dispatched!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/buses/<int:bus_id>', methods=['PUT'])
@login_required(role='admin')
def update_bus(bus_id):
    data = request.json
    if not data or 'bus_number' not in data:
        return jsonify({"error": "Bus number is required"}), 400
    
    bus_number = data['bus_number']
    capacity = data.get('capacity')
    driver_id = data.get('driver_id')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    try:
        with db_cursor() as cursor:
            cursor.execute(
                "UPDATE buses SET bus_number=%s, capacity=%s, driver_id=%s, latitude=%s, longitude=%s WHERE bus_id=%s",
                (bus_number, capacity, driver_id, latitude, longitude, bus_id)
            )
            return jsonify({"success": True, "message": "Bus updated successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/buses/<int:bus_id>', methods=['DELETE'])
@login_required(role='admin')
def delete_bus(bus_id):
    try:
        with db_cursor() as cursor:
            # Delete schedules mapping
            cursor.execute("DELETE FROM schedules WHERE bus_id=%s", (bus_id,))
            cursor.execute("DELETE FROM buses WHERE bus_id=%s", (bus_id,))
            return jsonify({"success": True, "message": "Bus deregistered successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------
# Admin CRUD: Routes
# -----------------------------
@app.route('/api/routes', methods=['GET'])
def get_routes():
    try:
        with db_cursor() as cursor:
            cursor.execute("""
                SELECT r.*, COUNT(rs.stop_id) AS stop_count
                FROM routes r
                LEFT JOIN route_stops rs ON r.route_id = rs.route_id
                GROUP BY r.route_id
                ORDER BY r.route_id
            """)
            result = cursor.fetchall()
            return jsonify(make_json_serializable(result))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/routes', methods=['POST'])
@login_required(role='admin')
def add_route():
    data = request.json
    if not data or 'route_name' not in data:
        return jsonify({"error": "Route name is required"}), 400
    
    route_name = data['route_name']
    start_point = data.get('start_point')
    end_point = data.get('end_point')
    
    try:
        with db_cursor() as cursor:
            cursor.execute(
                "INSERT INTO routes (route_name, start_point, end_point) VALUES (%s, %s, %s)",
                (route_name, start_point, end_point)
            )
            return jsonify({"success": True, "message": "Route added successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/routes/<int:route_id>', methods=['PUT'])
@login_required(role='admin')
def update_route(route_id):
    data = request.json
    if not data or 'route_name' not in data:
        return jsonify({"error": "Route name is required"}), 400
    
    route_name = data['route_name']
    start_point = data.get('start_point')
    end_point = data.get('end_point')
    
    try:
        with db_cursor() as cursor:
            cursor.execute(
                "UPDATE routes SET route_name=%s, start_point=%s, end_point=%s WHERE route_id=%s",
                (route_name, start_point, end_point, route_id)
            )
            return jsonify({"success": True, "message": "Route updated successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/routes/<int:route_id>', methods=['DELETE'])
@login_required(role='admin')
def delete_route(route_id):
    try:
        with db_cursor() as cursor:
            cursor.execute("DELETE FROM route_stops WHERE route_id=%s", (route_id,))
            cursor.execute("DELETE FROM student_routes WHERE route_id=%s", (route_id,))
            cursor.execute("DELETE FROM schedules WHERE route_id=%s", (route_id,))
            cursor.execute("DELETE FROM routes WHERE route_id=%s", (route_id,))
            return jsonify({"success": True, "message": "Route deleted successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------
# Admin CRUD: Students
# -----------------------------
@app.route('/api/students', methods=['GET'])
@login_required(role='admin')
def get_students():
    try:
        with db_cursor() as cursor:
            cursor.execute("SELECT * FROM students")
            result = cursor.fetchall()
            return jsonify(make_json_serializable(result))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/students', methods=['POST'])
@login_required(role='admin')
def add_student():
    data = request.json
    if not data or 'name' not in data or 'email' not in data:
        return jsonify({"error": "Name and email are required"}), 400
    
    name = data['name']
    email = data['email']
    password = data.get('password', 'password')
    route_id = data.get('route_id')
    
    try:
        with db_cursor() as cursor:
            cursor.execute(
                "INSERT INTO students (name, email, password) VALUES (%s, %s, %s)",
                (name, email, password)
            )
            student_id = cursor.lastrowid
            if route_id:
                cursor.execute(
                    "INSERT INTO student_routes (student_id, route_id) VALUES (%s, %s)",
                    (student_id, route_id)
                )
            return jsonify({"success": True, "message": "Student registered successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/students/<int:student_id>', methods=['PUT'])
@login_required(role='admin')
def update_student(student_id):
    data = request.json
    if not data or 'name' not in data or 'email' not in data:
        return jsonify({"error": "Name and email are required"}), 400
    
    name = data['name']
    email = data['email']
    password = data.get('password')
    route_id = data.get('route_id')
    
    try:
        with db_cursor() as cursor:
            if password:
                cursor.execute(
                    "UPDATE students SET name=%s, email=%s, password=%s WHERE student_id=%s",
                    (name, email, password, student_id)
                )
            else:
                cursor.execute(
                    "UPDATE students SET name=%s, email=%s WHERE student_id=%s",
                    (name, email, student_id)
                )
            
            if route_id:
                # Update route mapping
                cursor.execute("DELETE FROM student_routes WHERE student_id=%s", (student_id,))
                cursor.execute("INSERT INTO student_routes (student_id, route_id) VALUES (%s, %s)", (student_id, route_id))
                
            return jsonify({"success": True, "message": "Student updated successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/students/<int:student_id>', methods=['DELETE'])
@login_required(role='admin')
def delete_student(student_id):
    try:
        with db_cursor() as cursor:
            cursor.execute("DELETE FROM student_routes WHERE student_id=%s", (student_id,))
            cursor.execute("DELETE FROM students WHERE student_id=%s", (student_id,))
            return jsonify({"success": True, "message": "Student deleted successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------
# Student Dashboard API
# -----------------------------
@app.route('/api/student/dashboard', methods=['GET'])
@login_required(role='student')
def get_student_dashboard():
    student_id = session['user']['id']
    try:
        with db_cursor() as cursor:
            # 1. Fetch assigned route details
            cursor.execute("""
                SELECT r.route_id, r.route_name, r.start_point, r.end_point 
                FROM student_routes sr 
                JOIN routes r ON sr.route_id = r.route_id 
                WHERE sr.student_id = %s
            """, (student_id,))
            route = cursor.fetchone()
            
            # Default to first route if none assigned
            if not route:
                cursor.execute("SELECT * FROM routes LIMIT 1")
                route = cursor.fetchone()
            
            if not route:
                return jsonify(make_json_serializable({
                    "student": session['user'],
                    "route": {"route_name": "No assigned route", "start_point": "N/A", "end_point": "N/A"},
                    "buses": [],
                    "stops": [],
                    "notices": []
                }))
            
            route_id = route['route_id']
            
            # 2. Fetch buses on the assigned route
            cursor.execute("""
                SELECT b.bus_id, b.bus_number, b.capacity, b.latitude, b.longitude, 
                       d.name AS driver, d.phone_number AS driver_phone,
                       s.arrival_time_1st_shift AS departure, s.arrival_time_2nd_shift AS arrival 
                FROM schedules s 
                JOIN buses b ON s.bus_id = b.bus_id 
                LEFT JOIN drivers d ON b.driver_id = d.driver_id 
                WHERE s.route_id = %s
            """, (route_id,))
            buses = cursor.fetchall()
            
            # 3. Fetch stops on the route
            cursor.execute("""
                SELECT s.stop_name 
                FROM route_stops rs 
                JOIN stops s ON rs.stop_id = s.stop_id 
                WHERE rs.route_id = %s 
                ORDER BY rs.stop_order ASC
            """, (route_id,))
            stops = [x['stop_name'] for x in cursor.fetchall()]
            
            # 4. Fetch bulletins/notices for this route
            cursor.execute("""
                SELECT notice_id AS id, message AS text, target_route_id 
                FROM notices 
                WHERE target_route_id IS NULL OR target_route_id = %s 
                ORDER BY created_at DESC
            """, (route_id,))
            notices = cursor.fetchall()
            
            return jsonify(make_json_serializable({
                "student": session['user'],
                "route": route,
                "buses": buses,
                "stops": stops,
                "notices": notices
            }))
    except Exception as e:
        return jsonify({"error": f"Failed to load student dashboard: {str(e)}"}), 500

# -----------------------------
# Driver Dashboard API
# -----------------------------
@app.route('/api/driver/dashboard', methods=['GET'])
@login_required(role='driver')
def get_driver_dashboard():
    driver_id = session['user']['id']
    try:
        with db_cursor() as cursor:
            # 1. Fetch assigned bus
            cursor.execute("SELECT * FROM buses WHERE driver_id = %s LIMIT 1", (driver_id,))
            bus = cursor.fetchone()
            
            if not bus:
                return jsonify(make_json_serializable({
                    "driver": session['user'],
                    "bus": None,
                    "route": {"route_name": "No assigned corridor", "start_point": "N/A", "end_point": "N/A"},
                    "notices": []
                }))
            
            # 2. Fetch assigned route from schedule
            cursor.execute("""
                SELECT r.route_id, r.route_name, r.start_point, r.end_point, 
                       s.arrival_time_1st_shift, s.arrival_time_2nd_shift 
                FROM schedules s 
                JOIN routes r ON s.route_id = r.route_id 
                WHERE s.bus_id = %s 
                LIMIT 1
            """, (bus['bus_id'],))
            route = cursor.fetchone()
            
            if not route:
                route = {"route_name": "No active schedule corridor", "start_point": "N/A", "end_point": "N/A"}
                route_id = None
            else:
                route_id = route['route_id']
                
            # 3. Fetch Notices
            if route_id:
                cursor.execute("""
                    SELECT notice_id AS id, message AS text, target_route_id 
                    FROM notices 
                    WHERE target_route_id IS NULL OR target_route_id = %s 
                    ORDER BY created_at DESC
                """, (route_id,))
            else:
                cursor.execute("SELECT notice_id AS id, message AS text, target_route_id FROM notices WHERE target_route_id IS NULL ORDER BY created_at DESC")
            notices = cursor.fetchall()
            
            return jsonify(make_json_serializable({
                "driver": session['user'],
                "bus": bus,
                "route": route,
                "notices": notices
            }))
    except Exception as e:
        return jsonify({"error": f"Failed to load driver dashboard: {str(e)}"}), 500

# -----------------------------
# GPS Tracking & Simulation
# -----------------------------
@app.route('/api/track/<int:bus_id>', methods=['GET'])
def get_bus_location(bus_id):
    try:
        with db_cursor() as cursor:
            cursor.execute("SELECT bus_id, bus_number, latitude, longitude FROM buses WHERE bus_id = %s", (bus_id,))
            bus = cursor.fetchone()
            if not bus:
                return jsonify({"error": "Bus not found"}), 404
            
            return jsonify(make_json_serializable({
                "bus_id": bus['bus_id'],
                "bus_number": bus['bus_number'],
                "latitude": bus['latitude'],
                "longitude": bus['longitude']
            }))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/track/<int:bus_id>', methods=['POST'])
@login_required()  # Any logged-in user (like driver or admin) can send location updates
def update_bus_location(bus_id):
    data = request.json
    if not data or 'latitude' not in data or 'longitude' not in data:
        return jsonify({"error": "Latitude and longitude are required"}), 400
    
    try:
        with db_cursor() as cursor:
            cursor.execute(
                "UPDATE buses SET latitude=%s, longitude=%s WHERE bus_id=%s",
                (data['latitude'], data['longitude'], bus_id)
            )
            return jsonify({"success": True, "message": "Location updated successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------
# Run the Application Server
# -----------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
