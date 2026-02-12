#!/usr/bin/env python3
"""Simple Flask app to test contacts functionality"""
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'test-secret-key'

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'nirvana_buddha.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    # Test if we can query the database
    try:
        conn = get_db_connection()
        contacts = conn.execute('SELECT * FROM contact ORDER BY created_at DESC LIMIT 5').fetchall()
        conn.close()
        return f'''
        <h1>Nirvan Buddha - Contacts Test</h1>
        <p>Database connection: SUCCESS</p>
        <p>Contacts found: {len(contacts)}</p>
        <p><a href="/admin/contacts">Go to Admin Contacts Page</a></p>
        '''
    except Exception as e:
        return f'<h1>Error</h1><p>{e}</p>'

@app.route('/admin/contacts')
def admin_contacts():
    try:
        conn = get_db_connection()
        contacts = conn.execute('SELECT * FROM contact ORDER BY created_at DESC').fetchall()
        conn.close()
        
        html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Admin Contacts</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #4CAF50; color: white; }
                .empty { text-align: center; padding: 40px; color: #666; }
            </style>
        </head>
        <body>
            <h1>Contact Messages - Admin Panel</h1>
            <p><a href="/">Back to Home</a></p>
            <table>
                <tr>
                    <th>Date</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Phone</th>
                    <th>Message</th>
                </tr>
        '''
        
        if contacts:
            for contact in contacts:
                html += f'''
                <tr>
                    <td>{contact['created_at']}</td>
                    <td>{contact['name']}</td>
                    <td>{contact['email']}</td>
                    <td>{contact['phone'] or '-'}</td>
                    <td>{contact['message'][:100]}...</td>
                </tr>
                '''
        else:
            html += '<tr><td colspan="5" class="empty">No contact messages found</td></tr>'
        
        html += '''
            </table>
        </body>
        </html>
        '''
        
        return html
        
    except Exception as e:
        return f'<h1>Error</h1><p>{e}</p>'

if __name__ == '__main__':
    print("Starting simple test server...")
    print(f"Database path: {DB_PATH}")
    print(f"Database exists: {os.path.exists(DB_PATH)}")
    app.run(debug=True, port=5001)