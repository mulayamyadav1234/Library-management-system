from db import get_db_connection
from werkzeug.security import generate_password_hash

conn = get_db_connection()
cursor = conn.cursor()

try:
    # Insert a test student
    cursor.execute(
        "INSERT INTO students (Student_name, email, phone, department) VALUES (%s, %s, %s, %s)",
        ("Test Student", "teststudent@example.com", "9876543210", "Computer Science")
    )

    # Insert matching login credentials
    hashed_password = generate_password_hash("test123")
    cursor.execute(
        "INSERT INTO users (email, password_hash) VALUES (%s, %s)",
        ("teststudent@example.com", hashed_password)
    )

    conn.commit()
    print("✅ Test data inserted successfully!")

except Exception as e:
    conn.rollback()
    print("❌ Insert failed:", e)

finally:
    cursor.close()
    conn.close()