#!/usr/bin/env python3
"""Test database connection and fix the issue"""
import os
import sqlite3
from werkzeug.security import generate_password_hash

# Database path with absolute path
base_dir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(base_dir, 'instance', 'nirvana_buddha.db')

print(f"Testing database connection...")
print(f"Database path: {db_path}")
print(f"Database exists: {os.path.exists(db_path)}")

# Try to connect
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print("✓ Database connection successful!")
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"✓ Tables found: {[table[0] for table in tables]}")
    
    # Check if admin user exists
    cursor.execute("SELECT * FROM user WHERE is_admin = 1;")
    admin = cursor.fetchone()
    if admin:
        print(f"✓ Admin user exists: {admin[2]}")  # email is at index 2
    else:
        print("Creating admin user...")
        hashed_password = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO user (name, email, password_hash, is_admin)
            VALUES (?, ?, ?, ?)
        ''', ('Admin', 'admin@nirvanabuddha.com', hashed_password, True))
        conn.commit()
        print("✓ Admin user created!")
    
    conn.close()
    print("SUCCESS: Database test completed successfully!")
    
except Exception as e:
    print(f"ERROR: Database error: {e}")
    print(f"Error type: {type(e).__name__}")