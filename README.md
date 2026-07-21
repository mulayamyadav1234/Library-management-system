# Library Management System (LMS)

This project is a simple Flask-based Library Management System for managing students, books, issued books, and student reports. It uses MySQL as the database and Bootstrap for styling.

## Project Goal

The application helps a library administrator:
- register students
- add and manage books
- issue and return books
- track overdue fines
- generate a student report

## Main Features

- User login and registration
- Student management
- Book management
- Book issuing and returning
- Fine calculation for overdue books
- Student report generation
- Dashboard with summary cards

## Project Structure

- app.py: Main Flask application entry point
- db.py: Database connection setup
- modules/: Contains feature-based Flask blueprints
- templates/: HTML files for the user interface
- static/: Static assets like CSS or images
- testing/: Sample test files

## Files and Modules Explained

### 1. app.py
This is the main entry file of the application.

It:
- creates the Flask app
- sets the secret key for sessions
- registers all blueprints
- defines routes like / and /home
- handles logout

### 2. db.py
This file contains the database connection logic.

It connects the app to the MySQL database using mysql.connector.

Important details:
- host: 127.0.0.1
- user: root
- password: mulayam@123
- database: library_management_system

### 3. modules/auth.py
This module handles authentication.

Features:
- login
- student registration
- password hashing using Werkzeug
- session creation for logged-in users

How it works:
- The login route checks the email and password in the users table.
- If valid, the app stores the email in the session.
- The registration route inserts the student data into the students table and the login credentials into the users table.

### 4. modules/books.py
This module manages books and book circulation.

Features:
- list all books
- add new books
- edit existing books
- delete books
- issue books to students
- return books
- show issued books page
- calculate fines for overdue books

The module uses the issued_books table to track each borrow transaction.

### 5. modules/students.py
This module manages students.

Features:
- list students
- edit student details
- delete students
- generate a student report using the student name

It also ensures that the registration_date column exists in the students table.

### 6. modules/dashboard.py
This module provides the dashboard feature.

The dashboard shows:
- total number of books
- number of issued books
- remaining books
- total number of students
- recent students
- recent books

### 7. modules/report.py
This module creates a separate report page.

It allows the user to enter a student name and view:
- registration date
- issued books
- issue date
- due date
- return date
- overdue fine

### 8. templates/
This folder contains all HTML templates.

Common templates:
- base.html: shared layout and navbar
- home.html: dashboard page
- login.html: login page
- register.html: registration page
- students.html: students page and student report UI
- books.html: book listing page
- book_form.html: add/edit book form
- issue_book.html: issue/return book page
- issued_books.html: list of issued books
- report.html: separate report page

### 9. static/
This folder is for static files like CSS, JS, or images.

### 10. testing/
This folder contains test scripts used during development.

## How the App Works

1. The user opens the app.
2. If not logged in, they are redirected to the login page.
3. After login, they can access the dashboard.
4. From the dashboard, they can manage students and books.
5. When a book is issued, the app records the issue date and due date.
6. On return, the fine is calculated if the book is overdue.
7. The report module shows a student’s record and borrowing history.

## Database Tables

The app depends on these tables:

- users
  - stores login information
- students
  - stores student details and registration date
- books
  - stores book details and quantity
- issued_books
  - stores issue and return data plus fine amount

## Installation Steps

1. Install Python
2. Install Flask and mysql-connector-python
3. Create a MySQL database named library_management_system
4. Create the required tables
5. Run the app using:

```bash
python app.py
```

## Example Dependencies

Install these packages if needed:

```bash
pip install flask mysql-connector-python
```

## Important Notes for Beginners

- Flask routes are functions that handle web requests.
- Blueprints help organize the app into smaller modules.
- Templates are HTML files that use Jinja syntax to display dynamic data.
- Sessions are used to remember whether a user is logged in.
- SQL queries are used to interact with the MySQL database.

## Suggested Learning Order

1. Understand app.py
2. Learn db.py
3. Study auth.py for login/registration
4. Study books.py for library operations
5. Study students.py for student management
6. Study dashboard.py for summary cards
7. Study report.py for reports
8. Understand templates and how they display data

## Summary

This project is a beginner-friendly Flask application that demonstrates:
- web development with Python
- database integration with MySQL
- route handling
- templates
- sessions
- CRUD operations

It is a good project to learn full-stack basics using Flask.
