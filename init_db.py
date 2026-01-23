#!/usr/bin/env python3
"""
Database initialization script for Render deployment
Run this script to create all database tables and default admin user
"""

from app import create_tables, create_admin_user

if __name__ == '__main__':
    print("Initializing database...")
    create_tables()
    create_admin_user()
    print("Database initialization complete!")