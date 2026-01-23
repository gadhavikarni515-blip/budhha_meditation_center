import sqlite3, os
p = os.path.abspath('instance/nirvana_buddha.db')
conn = sqlite3.connect(p)
cur = conn.cursor()
for row in cur.execute("SELECT id, program_name, full_name, email, phone, created_at FROM program_registration ORDER BY created_at DESC LIMIT 5;"):
    print(row)
conn.close()
