from flask import Flask, request, jsonify, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for sessions

# -----------------------------
# Database Connection
# -----------------------------
db = mysql.connector.connect(
    host="localhost",          # or 127.0.0.1 if MySQL runs locally
    user="root",               # replace with your MySQL username
    password="root",     # replace with your MySQL password
    database="busmg"           # <-- your database name
)
cursor = db.cursor(dictionary=True)

# -----------------------------
# Admin Login System
# -----------------------------
@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    cursor.execute("SELECT * FROM Admins WHERE username=%s AND password=%s",
                   (data['username'], data['password']))
    admin = cursor.fetchone()
    if admin:
        session['admin_logged_in'] = True
        return jsonify({"message": "Login successful"})
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@app.route('/admin/logout', methods=['POST'])
def admin_logout():
    session.pop('admin_logged_in', None)
    return jsonify({"message": "Logged out successfully"})

# -----------------------------
# Notices (CRUD, restricted to admin)
# -----------------------------
@app.route('/notices', methods=['GET'])
def get_notices():
    cursor.execute("SELECT * FROM Notices")
    result = cursor.fetchall()
    return jsonify(result)

@app.route('/notices', methods=['POST'])
def add_notice():
    if not session.get('admin_logged_in'):
        return jsonify({"message": "Unauthorized"}), 403

    data = request.json
    cursor.execute(
        "INSERT INTO Notices (title, message, expiry_date, target_route_id) VALUES (%s, %s, %s, %s)",
        (data['title'], data['message'], data.get('expiry_date'), data.get('target_route_id'))
    )
    db.commit()
    return jsonify({"message": "Notice added successfully!"})

@app.route('/notices/<int:notice_id>', methods=['PUT'])
def update_notice(notice_id):
    if not session.get('admin_logged_in'):
        return jsonify({"message": "Unauthorized"}), 403

    data = request.json
    cursor.execute(
        "UPDATE Notices SET title=%s, message=%s, expiry_date=%s, target_route_id=%s WHERE notice_id=%s",
        (data['title'], data['message'], data.get('expiry_date'), data.get('target_route_id'), notice_id)
    )
    db.commit()
    return jsonify({"message": "Notice updated successfully!"})

@app.route('/notices/<int:notice_id>', methods=['DELETE'])
def delete_notice(notice_id):
    if not session.get('admin_logged_in'):
        return jsonify({"message": "Unauthorized"}), 403

    cursor.execute("DELETE FROM Notices WHERE notice_id=%s", (notice_id,))
    db.commit()
    return jsonify({"message": "Notice deleted successfully!"})

# -----------------------------
# Example Routes for Drivers, Buses, Routes
# -----------------------------
@app.route('/drivers', methods=['GET'])
def get_drivers():
    cursor.execute("SELECT * FROM Drivers")
    result = cursor.fetchall()
    return jsonify(result)

@app.route('/buses', methods=['GET'])
def get_buses():
    cursor.execute("SELECT * FROM Buses")
    result = cursor.fetchall()
    return jsonify(result)

@app.route('/routes', methods=['GET'])
def get_routes():
    cursor.execute("SELECT * FROM Routes")
    result = cursor.fetchall()
    return jsonify(result)

# -----------------------------
# Run the Server
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)
