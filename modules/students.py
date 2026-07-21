from datetime import date

from flask import Blueprint, render_template, request, redirect, url_for, session
from db import get_db_connection

students_bp = Blueprint('students', __name__)


def _normalize_student_row(row):
    if not row:
        return None
    return {key.lower(): value for key, value in row.items()}


def _ensure_student_registration_date_column():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SHOW COLUMNS FROM students LIKE 'registration_date'")
    if cursor.fetchone() is None:
        cursor.execute("ALTER TABLE students ADD COLUMN registration_date DATE DEFAULT NULL")
        conn.commit()
    cursor.close()
    conn.close()


@students_bp.route('/students')
def student_list():
    if 'email' not in session:
        return redirect(url_for('auth.login'))

    _ensure_student_registration_date_column()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students ORDER BY Student_Name ASC")
    students = [_normalize_student_row(row) for row in cursor.fetchall()]
    cursor.close()
    conn.close()

    return render_template('students.html', students=students)


@students_bp.route('/students/report', methods=['GET', 'POST'])
def student_report():
    if 'email' not in session:
        return redirect(url_for('auth.login'))

    _ensure_student_registration_date_column()

    student_name = (request.form.get('student_name') or request.args.get('student_name') or '').strip()
    report_student = None
    report_records = []

    if student_name:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT Student_ID, Student_Name, Email, Phone, Department, registration_date FROM students WHERE LOWER(Student_Name) LIKE LOWER(%s) ORDER BY Student_Name ASC",
            (f'%{student_name}%',)
        )
        student_rows = cursor.fetchall()

        if student_rows:
            row = student_rows[0]
            report_student = _normalize_student_row(row)

            cursor.execute(
                """
                SELECT ib.issue_id, ib.book_id, ib.student_email, ib.issue_date, ib.due_date, ib.return_date, ib.fine_amount,
                       b.book_name
                FROM issued_books ib
                LEFT JOIN books b ON b.book_id = ib.book_id
                WHERE ib.student_email = %s
                ORDER BY ib.issue_id DESC
                """,
                (report_student.get('email'),)
            )
            issue_rows = cursor.fetchall()

            today = date.today()
            for issue in issue_rows:
                fine_amount = float(issue.get('fine_amount') or 0.00)
                due_date = issue.get('due_date')
                return_date = issue.get('return_date')

                if due_date and return_date is None and today > due_date:
                    overdue_days = (today - due_date).days
                    fine_amount = overdue_days * 5
                elif due_date and return_date and return_date > due_date:
                    overdue_days = (return_date - due_date).days
                    fine_amount = overdue_days * 5

                report_records.append({
                    'book_name': issue.get('book_name') or 'Unknown Book',
                    'issue_date': issue.get('issue_date'),
                    'due_date': due_date,
                    'return_date': return_date,
                    'fine_amount': fine_amount,
                    'overdue': bool(due_date and ((return_date and return_date > due_date) or (return_date is None and today > due_date)))
                })

        cursor.close()
        conn.close()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students ORDER BY Student_Name ASC")
    students = [_normalize_student_row(row) for row in cursor.fetchall()]
    cursor.close()
    conn.close()

    return render_template('students.html', students=students, report_student=report_student, report_records=report_records, report_query=student_name)


@students_bp.route('/students/edit/<email>', methods=['GET', 'POST'])
def edit_student(email):
    if 'email' not in session:
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        name = request.form['name']
        new_email = request.form['email']
        phone = request.form['phone']
        department = request.form['department']

        try:
            cursor.execute(
                "UPDATE students SET Student_Name=%s, Email=%s, Phone=%s, Department=%s WHERE Email=%s",
                (name, new_email, phone, department, email)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            cursor.execute("SELECT * FROM students WHERE Email = %s", (email,))
            student_row = cursor.fetchone()
            student = _normalize_student_row(student_row)
            cursor.close()
            conn.close()
            return render_template('students.html', student=student, error=f"Update failed: {e}")

        cursor.close()
        conn.close()
        return redirect(url_for('students.student_list'))

    cursor.execute("SELECT * FROM students WHERE Email = %s", (email,))
    student_row = cursor.fetchone()
    student = _normalize_student_row(student_row)
    cursor.close()
    conn.close()

    if not student:
        return redirect(url_for('students.student_list'))

    return render_template('students.html', student=student)


@students_bp.route('/students/delete/<email>', methods=['GET', 'POST'])
def delete_student(email):
    if 'email' not in session:
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT email FROM students WHERE email = %s", (email,))
        student = cursor.fetchone()

        if student:
            student_email = student[0]
            cursor.execute("DELETE FROM users WHERE email = %s", (student_email,))
            cursor.execute("DELETE FROM students WHERE email = %s", (student_email,))
            conn.commit()

    except Exception as e:
        conn.rollback()

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('students.student_list'))