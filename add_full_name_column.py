import sqlite3, os
p = os.path.abspath('instance/nirvana_buddha.db')
print('DB path:', p)
conn = sqlite3.connect(p)
cur = conn.cursor()
cols = [r[1] for r in cur.execute("PRAGMA table_info(program_registration);")]
print('Before columns:', cols)
if 'full_name' not in cols:
    print('Adding full_name column...')
    cur.execute("ALTER TABLE program_registration ADD COLUMN full_name TEXT;")
    conn.commit()
else:
    print('full_name already exists')
cols2 = [r[1] for r in cur.execute("PRAGMA table_info(program_registration);")]
print('After columns:', cols2)
conn.close()
