import sqlite3

db = sqlite3.connect('/opt/math-home-tutor/data.db')
cols = [r[1] for r in db.execute('PRAGMA table_info(student)').fetchall()]
print(f"Current columns: {cols}")

migrations = [
    ("total_attempts", "INTEGER DEFAULT 0"),
    ("total_correct", "INTEGER DEFAULT 0"),
]

for name, typ in migrations:
    if name not in cols:
        db.execute(f"ALTER TABLE student ADD COLUMN {name} {typ}")
        print(f"  Added column: {name}")
    else:
        print(f"  Already exists: {name}")

db.commit()
db.close()
print("Migration done.")
