from flask import Flask, render_template, request, redirect, url_for, session, Response
from app.ocr import read_plate
from app.fine_logic import check_if_fine
from app.db import get_db_connection, validate_user
from app.sms import send_sms
from werkzeug.security import check_password_hash
import os
import cv2
from functools import wraps

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'supersecret')

# 🎥 Camera setup
camera = cv2.VideoCapture(0)

# 👮 Require login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

# 🏠 Home - upload
@app.route('/')
@login_required
def index():
    return render_template('index.html')

# 🔑 Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = validate_user(username)

        if user and check_password_hash(user['password'], password):
            session['username'] = username
            return redirect('/')
        else:
            return render_template('login.html', error="Invalid credentials.")
    return render_template('login.html')

# 🚪 Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

# 📷 Live camera feed
def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_feed')
@login_required
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/live')
@login_required
def live():
    return render_template('live.html')

# 📸 Capture + OCR + Fine logic
@app.route('/capture', methods=['POST'])
@login_required
def capture():
    ret, frame = camera.read()
    if not ret:
        return "Failed to capture frame", 500

    img_path = os.path.join('static', 'uploads', 'capture.jpg')
    cv2.imwrite(img_path, frame)

    plate_text = read_plate(frame)
    result = ""

    if plate_text:
        conn = get_db_connection()
        result = check_if_fine(plate_text, conn)
        conn.close()

        if "Fine Issued" in result:
            send_sms(plate_text)
    else:
        result = "❌ No valid plate detected."

    return render_template("capture.html", plate_text=plate_text, result=result)

# 📊 Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()

    # All fine records
    cursor.execute("SELECT * FROM fines ORDER BY timestamp DESC")
    fines = cursor.fetchall()

    # For chart: convert Row objects to normal dicts
    cursor.execute("""
        SELECT DATE(timestamp) as day, COUNT(*) as total 
        FROM fines 
        GROUP BY day 
        ORDER BY day DESC
    """)
    rows = cursor.fetchall()
    chart_data = [{"day": row["day"], "total": row["total"]} for row in rows]

    conn.close()
    return render_template("dashboard.html", fines=fines, chart_data=chart_data)


