from flask import Blueprint, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash
from db import get_db_connection

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        department = request.form['department']
        password = request.form['password']

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO students (Student_name, email, phone, department) VALUES (%s, %s, %s, %s)",
                (name, email, phone, department)
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

        return redirect(url_for('auth.login'))

    return render_template('register.html')