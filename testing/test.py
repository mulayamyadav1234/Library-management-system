from db import get_db_connection

try:
    conn = get_db_connection()
    print("✅ Connected successfully!")
    conn.close()
except Exception as e:
    print("❌ Connection failed:", e)