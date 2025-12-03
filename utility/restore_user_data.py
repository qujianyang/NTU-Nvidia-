"""
Restore user authentication and progress data from backup database
while keeping the new merged course data.
"""
import sqlite3
from pathlib import Path


def restore_user_tables(backup_db_path, new_db_path):
    """Copy user-related tables from backup to new database."""

    print("=" * 60)
    print("User Data Restoration")
    print("=" * 60)

    # Connect to both databases
    print(f"\nConnecting to backup database: {backup_db_path}")
    backup_conn = sqlite3.connect(backup_db_path)
    backup_cursor = backup_conn.cursor()

    print(f"Connecting to new database: {new_db_path}")
    new_conn = sqlite3.connect(new_db_path)
    new_cursor = new_conn.cursor()

    # User tables to copy
    user_tables = ['users', 'user_progress', 'user_sessions', 'user_chat_history']

    print("\n" + "-" * 60)
    print("Copying user-related tables...")
    print("-" * 60)

    for table_name in user_tables:
        print(f"\n[{table_name}]")

        # Check if table exists in backup
        backup_cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        if not backup_cursor.fetchone():
            print(f"  [SKIP] Table '{table_name}' not found in backup")
            continue

        # Get table schema from backup
        backup_cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        create_statement = backup_cursor.fetchone()[0]

        # Create table in new database
        print(f"  [SCHEMA] Creating table structure...")
        new_cursor.execute(create_statement)

        # Get all data from backup
        backup_cursor.execute(f"SELECT * FROM {table_name}")
        rows = backup_cursor.fetchall()

        if rows:
            # Get column count
            backup_cursor.execute(f"PRAGMA table_info({table_name})")
            columns = backup_cursor.fetchall()
            column_count = len(columns)

            # Insert data into new database
            placeholders = ','.join(['?'] * column_count)
            print(f"  [DATA] Copying {len(rows)} rows...")
            new_cursor.executemany(
                f"INSERT INTO {table_name} VALUES ({placeholders})",
                rows
            )
            print(f"  [OK] Successfully copied {len(rows)} rows")
        else:
            print(f"  [EMPTY] Table has no data to copy")

    # Commit changes
    print("\n" + "-" * 60)
    print("Committing changes...")
    new_conn.commit()

    # Get statistics
    print("\n" + "=" * 60)
    print("RESTORATION COMPLETE!")
    print("=" * 60)

    for table_name in user_tables:
        try:
            new_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = new_cursor.fetchone()[0]
            print(f"{table_name}: {count} rows")
        except:
            print(f"{table_name}: Not restored (didn't exist in backup)")

    # Close connections
    backup_conn.close()
    new_conn.close()

    print("\n[SUCCESS] User data has been successfully restored!")
    print("=" * 60)


if __name__ == "__main__":
    base_dir = Path(__file__).parent / "pdf_ingestion_system"
    backup_db = base_dir / "nvidia_courses_OLD_BACKUP.db"
    new_db = base_dir / "nvidia_courses.db"

    if not backup_db.exists():
        print(f"[ERROR] Backup database not found: {backup_db}")
        exit(1)

    if not new_db.exists():
        print(f"[ERROR] New database not found: {new_db}")
        exit(1)

    restore_user_tables(str(backup_db), str(new_db))
