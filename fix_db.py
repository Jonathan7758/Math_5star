import paramiko

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("101.96.217.150", username="root", password="1Qxcjyb!@", timeout=15)

# Check active DB schema
stdin, stdout, stderr = c.exec_command(
    "/opt/math-home-tutor/venv/bin/python3 -c \"import sqlite3; db=sqlite3.connect('/opt/math-home-tutor/data.db'); "
    "tables=[r[0] for r in db.execute('SELECT name FROM sqlite_master WHERE type=\\'table\\'').fetchall()]; print('Tables:', tables); "
    "cols=[r[1] for r in db.execute('PRAGMA table_info(student)').fetchall()]; print('Student cols:', cols); "
    "count=db.execute('SELECT COUNT(*) FROM student').fetchone()[0]; print('Students:', count); db.close()\""
)
print(stdout.read().decode())
print(stderr.read().decode())

# Migrate: add missing columns
stdin, stdout, stderr = c.exec_command(
    "/opt/math-home-tutor/venv/bin/python3 -c \"import sqlite3; db=sqlite3.connect('/opt/math-home-tutor/data.db'); "
    "cols=[r[1] for r in db.execute('PRAGMA table_info(student)').fetchall()]; "
    "print('Current:', cols); "
    "for name,typ in [('total_attempts','INTEGER DEFAULT 0'),('total_correct','INTEGER DEFAULT 0')]: "
    "  if name not in cols: db.execute(f'ALTER TABLE student ADD COLUMN {name} {typ}'); print(f'Added {name}'); "
    "  else: print(f'{name} exists'); "
    "db.commit(); db.close(); print('Done')\""
)
print(stdout.read().decode())
print(stderr.read().decode())

# Restart backend
stdin, stdout, stderr = c.exec_command("systemctl restart math-tutor")
print("Restarted math-tutor")
c.close()
