from flask import Blueprint, render_template, session, redirect, url_for
from db import get_db_connection

dashboard_bp = Blueprint('dashboard', __name__, template_folder='../templates')


def _normalize_row(row):
    if not row:
        return None
    return {key.lower(): value for key, value in row.items()}


def get_dashboard_context():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total_books FROM books")
    total_books = cursor.fetchone()['total_books']

    try:
        cursor.execute("SELECT COUNT(*) AS issued_books FROM issued_books WHERE return_date IS NULL")
        issued_books = cursor.fetchone()['issued_books']
    except Exception:
        issued_books = 0

    remaining_books = total_books - issued_books

    cursor.execute("SELECT COUNT(*) AS total_students FROM students")
    total_students = cursor.fetchone()['total_students']

    cursor.execute("SELECT Student_Name AS student_name, Email AS email, Department AS department FROM students ORDER BY Student_ID DESC LIMIT 5")
    recent_students = [_normalize_row(row) for row in cursor.fetchall()]

    try:
        cursor.execute("SELECT Book_Name AS book_name, Author AS author FROM books ORDER BY Book_ID DESC LIMIT 5")
        recent_books = [_normalize_row(row) for row in cursor.fetchall()]
    except Exception:
        cursor.execute("SELECT * FROM books ORDER BY Book_ID DESC LIMIT 5")
        recent_books = [_normalize_row(row) for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return {
        'total_books': total_books,
        'issued_books': issued_books,
        'remaining_books': remaining_books,
        'total_students': total_students,
        'recent_students': recent_students,
        'recent_books': recent_books,
    }


@dashboard_bp.route('/dashboard')
def dashboard_home():
    if 'email' not in session:
        return redirect(url_for('auth.login'))

    context = get_dashboard_context()
    context['email'] = session['email']
    return render_template('home.html', **context)
