import random
from datetime import date, timedelta, datetime
from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection
from modules.students import _ensure_student_registration_date_column
from extensions import mail 
from flask_mail import Message

auth_bp = Blueprint('auth', __name__, template_folder='../templates')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            otp = str(random.randint(1000, 9999))
            session['otp'] = otp
            session['otp_email'] = user['email']
            session['otp_expiry'] = (datetime.now() + timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')

            msg = Message(
                subject='Your L.M.S Login OTP',
                recipients=[user['email']],
                body=f'Your OTP for L.M.S login is: {otp}. It will expire in 5 minutes.'
            )

            mail.send(msg)
            return redirect(url_for('auth.verify_otp'))

        else:
            return render_template('login.html', error="Invalid email or password")

    return render_template('login.html')


@auth_bp.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if  'otp_email' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        entered_otp = request.form['otp']
        otp = session.get('otp')
        otp_email = session.get('otp_email')
        otp_expiry = session.get('otp_expiry')

        if not otp or not otp_email or not otp_expiry:
            return render_template('verify_otp.html', error="OTP session expired. Please login again.")

        if datetime.now() > datetime.strptime(otp_expiry, '%Y-%m-%d %H:%M:%S'):
            session.pop('otp', None)
            session.pop('otp_email', None)
            session.pop('otp_expiry', None)
            return render_template('verify_otp.html', error="OTP has expired. Please login again.")

        if entered_otp == otp:
            session['email'] = otp_email
            session.pop('otp', None)
            session.pop('otp_email', None)
            session.pop('otp_expiry', None)
            return redirect(url_for('home_page'))
        else:
            return render_template('verify_otp.html', error="Invalid OTP. Please try again.")

    return render_template('verify_otp.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        department = request.form['department']
        password = request.form['password']

        hashed_password = generate_password_hash(password)

        _ensure_student_registration_date_column()

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO students (Student_name, email, phone, department, registration_date) VALUES (%s, %s, %s, %s, %s)",
                (name, email, phone, department, date.today())
            )
            cursor.execute(
                "INSERT INTO users (email, password_hash) VALUES (%s, %s)",
                (email, hashed_password)
            )
            conn.commit()

        except Exception as e:
            conn.rollback()
            return render_template('register.html', error=f"Registration failed: {e}")

        finally:
            cursor.close()
            conn.close()

        return render_template('register.html', success='Student registered successfully. You can add another student now.')

    return render_template('register.html')