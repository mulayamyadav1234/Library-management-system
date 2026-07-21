from flask import Blueprint, render_template, request, redirect, url_for, session
from db import get_db_connection

books_bp = Blueprint('books', __name__)


# Show all books
@books_bp.route('/books')
def book_list():
    if 'email' not in session:
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books ORDER BY book_id DESC")
    books = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('books.html', books=books)


# Add a new book
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
            return render_template('add_book.html', error=f"Failed to add book: {e}")
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('books.book_list'))

    return render_template('add_book.html')


# Edit an existing book
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

        cursor.execute(
            "UPDATE books SET book_name=%s, author=%s, quantity=%s WHERE book_id=%s",
            (book_name, author, quantity, book_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('books.book_list'))

    cursor.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
    book = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('edit_book.html', book=book)


# Delete a book
@books_bp.route('/books/delete/<int:book_id>')
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


# Mark a book as issued (reduce quantity by 1)
@books_bp.route('/books/issue/<int:book_id>')
def issue_book(book_id):
    if 'email' not in session:
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT quantity FROM books WHERE book_id = %s", (book_id,))
    book = cursor.fetchone()

    if book and book['quantity'] > 0:
        cursor.execute("UPDATE books SET quantity = quantity - 1 WHERE book_id = %s", (book_id,))
        conn.commit()

    cursor.close()
    conn.close()
    return redirect(url_for('books.book_list'))


# Mark a book as returned (increase quantity by 1)
@books_bp.route('/books/return/<int:book_id>')
def return_book(book_id):
    if 'email' not in session:
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE books SET quantity = quantity + 1 WHERE book_id = %s", (book_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('books.book_list'))