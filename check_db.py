import os
import sqlite3
p = os.path.abspath('nirvana_buddha.db')
print('DB path:', p)
print('exists:', os.path.exists('nirvana_buddha.db'))
if os.path.exists('nirvana_buddha.db'):
    conn = sqlite3.connect('nirvana_buddha.db')
    cur = conn.cursor()
    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table';")]
    print('tables:', tables)
    if 'program_registration' in tables:
        cols = [r[1] for r in cur.execute("PRAGMA table_info(program_registration);")]
        print('program_registration cols:', cols)
    conn.close()
else:
    print('Database does not exist yet')
