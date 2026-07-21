from datetime import date, timedelta

from flask import Blueprint, render_template, request, redirect, url_for, session
from db import get_db_connection

books_bp = Blueprint('books', __name__, template_folder='../templates')


def _normalize_book_row(row):
    if not row:
        return None
    return {key.lower(): value for key, value in row.items()}


def _ensure_issued_books_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS issued_books (
            issue_id INT AUTO_INCREMENT PRIMARY KEY,
            book_id INT NOT NULL,
            student_email VARCHAR(100) NOT NULL,
            issue_date DATE NOT NULL,
            due_date DATE NOT NULL,
            return_date DATE NULL,
            fine_amount DECIMAL(10,2) DEFAULT 0.00
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()


@books_bp.route('/books')
def book_list():
    if 'email' not in session:
        return redirect(url_for('auth.login'))

    search_query = request.args.get('q', '').strip()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if search_query:
        cursor.execute(
            "SELECT * FROM books WHERE LOWER(book_name) LIKE LOWER(%s) ORDER BY book_id DESC",
            (f'%{search_query}%',)
        )
    else:
        cursor.execute("SELECT * FROM books ORDER BY book_id DESC")

    books = [_normalize_book_row(row) for row in cursor.fetchall()]
    cursor.close()
    conn.close()

    return render_template('books.html', books=books, search_query=search_query)


@books_bp.route('/issued-books')
def issued_books_page():
    if 'email' not in session:
        return redirect(url_for('auth.login'))

    _ensure_issued_books_table()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT ib.issue_id, ib.book_id, ib.student_email, ib.issue_date, ib.due_date, ib.return_date, ib.fine_amount,
               b.book_name, b.author
        FROM issued_books ib
        LEFT JOIN books b ON b.book_id = ib.book_id
        ORDER BY ib.issue_id DESC
    """)
    records = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('issued_books.html', records=records)


@books_bp.route('/books/add', methods=['GET', 'POST'])
def add_book():
    if 'email' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        book_name = request.form['book_name']
        author = request.form['author']
        quantity = request.form['quantity']

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO books (book_name, author, quantity) VALUES (%s, %s, %s)",
                (book_name, author, quantity)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            return render_template('book_form.html', error=f"Failed to add book: {e}")
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('books.book_list'))

    return render_template('book_form.html')


@books_bp.route('/books/edit/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    if 'email' not in session:
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        book_name = request.form['book_name']
        author = request.form['author']
        quantity = request.form['quantity']

        try:
            cursor.execute(
                "UPDATE books SET book_name=%s, author=%s, quantity=%s WHERE book_id=%s",
                (book_name, author, quantity, book_id)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            cursor.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
            book = _normalize_book_row(cursor.fetchone())
            cursor.close()
            conn.close()
            return render_template('book_form.html', book=book, error=f"Update failed: {e}")

        cursor.close()
        conn.close()
        return redirect(url_for('books.book_list'))

    cursor.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
    book = _normalize_book_row(cursor.fetchone())
    cursor.close()
    conn.close()

    if not book:
        return redirect(url_for('books.book_list'))

    return render_template('book_form.html', book=book)


@books_bp.route('/books/delete/<int:book_id>', methods=['GET', 'POST'])
def delete_book(book_id):
    if 'email' not in session:
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('books.book_list'))


@books_bp.route('/books/issue/<int:book_id>', methods=['GET', 'POST'])
def issue_book(book_id):
    if 'email' not in session:
        return redirect(url_for('auth.login'))

    _ensure_issued_books_table()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
    book = _normalize_book_row(cursor.fetchone())

    if not book:
        cursor.close()
        conn.close()
        return redirect(url_for('books.book_list'))

    if request.method == 'POST':
        student_email = request.form.get('student_email', '').strip()
        if not student_email:
            cursor.execute("SELECT Email AS email FROM students ORDER BY Student_ID DESC")
            students = [row.get('email') for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            return render_template('issue_book.html', book=book, students=students, error='Please select a student.')

        cursor.execute("SELECT * FROM students WHERE Email = %s", (student_email,))
        student = cursor.fetchone()
        if not student:
            cursor.execute("SELECT Email AS email FROM students ORDER BY Student_ID DESC")
            students = [row.get('email') for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            return render_template('issue_book.html', book=book, students=students, error='Student not found.')

        cursor.execute("SELECT * FROM issued_books WHERE book_id = %s AND return_date IS NULL", (book_id,))
        active_issue = cursor.fetchone()
        if active_issue:
            cursor.close()
            conn.close()
            return redirect(url_for('books.book_list'))

        if int(book.get('quantity', 0)) <= 0:
            cursor.close()
            conn.close()
            return redirect(url_for('books.book_list'))

        issue_date = date.today()
        due_date = issue_date + timedelta(days=7)
        cursor.execute(
            "INSERT INTO issued_books (book_id, student_email, issue_date, due_date, fine_amount) VALUES (%s, %s, %s, %s, %s)",
            (book_id, student_email, issue_date, due_date, 0.00)
        )
        cursor.execute("UPDATE books SET quantity = quantity - 1 WHERE book_id = %s", (book_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('books.book_list'))

    cursor.execute("SELECT Email AS email FROM students ORDER BY Student_ID DESC")
    students = [row.get('email') for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return render_template('issue_book.html', book=book, students=students)


@books_bp.route('/books/return/<int:book_id>', methods=['GET', 'POST'])
def return_book(book_id):
    if 'email' not in session:
        return redirect(url_for('auth.login'))

    _ensure_issued_books_table()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
    book = _normalize_book_row(cursor.fetchone())

    if not book:
        cursor.close()
        conn.close()
        return redirect(url_for('books.book_list'))

    cursor.execute("SELECT * FROM issued_books WHERE book_id = %s AND return_date IS NULL ORDER BY issue_id DESC LIMIT 1", (book_id,))
    issue = cursor.fetchone()

    if not issue:
        cursor.close()
        conn.close()
        return redirect(url_for('books.book_list'))

    if request.method == 'POST':
        return_date = date.today()
        due_date = issue.get('due_date')
        fine_amount = 0.00
        if due_date and return_date > due_date:
            overdue_days = (return_date - due_date).days
            fine_amount = overdue_days * 5

        cursor.execute(
            "UPDATE issued_books SET return_date = %s, fine_amount = %s WHERE issue_id = %s",
            (return_date, fine_amount, issue['issue_id'])
        )
        cursor.execute("UPDATE books SET quantity = quantity + 1 WHERE book_id = %s", (book_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('books.book_list'))

    due_date = issue.get('due_date')
    return_date = date.today()
    fine_amount = 0.00
    if due_date and return_date > due_date:
        overdue_days = (return_date - due_date).days
        fine_amount = overdue_days * 5

    cursor.close()
    conn.close()
    return render_template('issue_book.html', book=book, issue=issue, return_mode=True, fine_amount=fine_amount)
