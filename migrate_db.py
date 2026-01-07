"""
Migration script to add start_time and end_time columns to the program table.
Run this script once to update your database schema.
"""
from app import app, db
import sqlite3
import os

def migrate_database():
    """Add start_time and end_time columns to program table if they don't exist."""
    with app.app_context():
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        # Handle both relative and absolute paths
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
        else:
            db_path = db_uri.replace('sqlite:///', '')
        
        # Handle instance folder path
        if not os.path.isabs(db_path):
            db_path = os.path.join('instance', db_path)
        
        # Ensure database exists first
        if not os.path.exists(db_path):
            print(f"Database not found at {db_path}. Creating tables...")
            db.create_all()
            print("Database created successfully!")
            return
        
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='program'")
            if not cursor.fetchone():
                print("Program table does not exist. Creating all tables...")
                conn.close()
                db.create_all()
                print("Tables created successfully!")
                return
            
            # Check if columns already exist
            cursor.execute("PRAGMA table_info(program)")
            columns = [row[1] for row in cursor.fetchall()]
            
            # Add start_time column if it doesn't exist
            if 'start_time' not in columns:
                print("Adding start_time column...")
                cursor.execute("ALTER TABLE program ADD COLUMN start_time TIME")
                print("[OK] start_time column added")
            else:
                print("[OK] start_time column already exists")
            
            # Add end_time column if it doesn't exist
            if 'end_time' not in columns:
                print("Adding end_time column...")
                cursor.execute("ALTER TABLE program ADD COLUMN end_time TIME")
                print("[OK] end_time column added")
            else:
                print("[OK] end_time column already exists")
            
            conn.commit()
            print("\n[SUCCESS] Migration completed successfully!")
            
        except Exception as e:
            conn.rollback()
            print(f"[ERROR] Error during migration: {e}")
            raise
        finally:
            conn.close()

if __name__ == '__main__':
    migrate_database()

