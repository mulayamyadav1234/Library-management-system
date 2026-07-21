from datetime import date

from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection
from modules.students import _ensure_student_registration_date_column

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
            session.permanent = True
            session['email'] = user['email']
            return redirect(url_for('dashboard.dashboard_home'))
        else:
            return render_template('login.html', error="Invalid email or password")

    return render_template('login.html')


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