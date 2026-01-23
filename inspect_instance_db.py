import sqlite3, os
p = os.path.abspath('instance/nirvana_buddha.db')
print('DB path:', p)
if not os.path.exists(p):
    print('Instance DB not found')
else:
    conn = sqlite3.connect(p)
    cur = conn.cursor()
    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table';")]
    print('tables:', tables)
    if 'program_registration' in tables:
        cols = [r[1] for r in cur.execute('PRAGMA table_info(program_registration);')]
        print('program_registration cols:', cols)
    conn.close()
