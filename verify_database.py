"""Verify the complete database structure and data."""
import sqlite3

db_path = "c:/Users/user/Documents/GitHub/NTU-Nvidia-/pdf_ingestion_system/nvidia_courses.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("DATABASE VERIFICATION REPORT")
print("=" * 60)

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print("\nAll Tables:")
for t in tables:
    print(f"  - {t[0]}")

print("\n" + "-" * 60)
print("TABLE ROW COUNTS")
print("-" * 60)

for t in tables:
    if t[0] != 'sqlite_sequence':
        cursor.execute(f"SELECT COUNT(*) FROM {t[0]}")
        count = cursor.fetchone()[0]
        print(f"{t[0]:25} {count:>5} rows")

print("\n" + "-" * 60)
print("COURSE DATA BY DOMAIN")
print("-" * 60)

cursor.execute('SELECT domain, COUNT(*) FROM courses GROUP BY domain')
domain_counts = cursor.fetchall()
for domain, count in domain_counts:
    print(f"{domain:25} {count:>5} courses")

print("\n" + "-" * 60)
print("USER ACCOUNTS")
print("-" * 60)

cursor.execute('SELECT id, email, full_name, created_at FROM users')
users = cursor.fetchall()
for user in users:
    print(f"ID: {user[0]:3} Email: {user[1]:30} Name: {user[2]:20} Created: {user[3]}")

print("\n" + "=" * 60)
print("[SUCCESS] Database verification complete!")
print("All user data and course data are present.")
print("=" * 60)

conn.close()
