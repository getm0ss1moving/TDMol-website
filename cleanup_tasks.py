import os
import sqlite3
from datetime import datetime, timedelta

# --- Configuration ---
# The path to your SQLite database file. It MUST match the one in app.py
# This constructs the path relative to the script's location.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'tasks.db')
# How many days of records to keep.
DAYS_TO_KEEP = 2

def cleanup_old_tasks():
    """Connects to the database and deletes records older than DAYS_TO_KEEP."""
    
    if not os.path.exists(DB_PATH):
        print(f"Database file not found at {DB_PATH}. Nothing to do.")
        return

    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Calculate the cutoff date
        # Records created *before* this date will be deleted.
        cutoff_date = datetime.utcnow() - timedelta(days=DAYS_TO_KEEP)
        
        # Format for SQLite (YYYY-MM-DD HH:MM:SS)
        cutoff_str = cutoff_date.strftime('%Y-%m-%d %H:%M:%S')

        print(f"[{datetime.utcnow().isoformat()}] Starting cleanup process.")
        print(f"Database: {DB_PATH}")
        print(f"Deleting records older than {cutoff_str} (UTC)...")

        # Find how many records will be deleted (for logging purposes)
        cursor.execute("SELECT COUNT(*) FROM task WHERE created_at < ?", (cutoff_str,))
        count = cursor.fetchone()[0]

        if count > 0:
            # Execute the DELETE statement
            cursor.execute("DELETE FROM task WHERE created_at < ?", (cutoff_str,))
            
            # Commit the changes to the database
            conn.commit()
            print(f"Successfully deleted {count} old task record(s).")
        else:
            print("No old records found to delete.")

    except sqlite3.Error as e:
        print(f"Database error during cleanup: {e}")
    finally:
        # Always close the connection
        if conn:
            conn.close()
            print("Cleanup finished and database connection closed.")

if __name__ == '__main__':
    cleanup_old_tasks()