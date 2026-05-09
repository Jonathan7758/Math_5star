import sqlite3
import os

# Check all table schemas and migrate
db_path = "/opt/math-home-tutor/data.db"
db = sqlite3.connect(db_path)

# Check all table schemas
tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print(f"Tables: {tables}")

# Migrations per table
migrations = {
    "student": [
        ("total_attempts", "INTEGER DEFAULT 0"),
        ("total_correct", "INTEGER DEFAULT 0"),
    ],
    "sprite_state": [
        ("owned_skins", "TEXT DEFAULT '[]'"),
        ("streak_freeze", "INTEGER DEFAULT 0"),
    ],
    "answer_record": [],
    "mastery": [],
    "daily_stats": [],
    "achievement": [],
    "learning_path": [],
    "push_subscription": [],
}

for table, cols in migrations.items():
    if table not in tables:
        print(f"  Table '{table}' not found, skipping")
        continue
    existing = [r[1] for r in db.execute(f"PRAGMA table_info({table})").fetchall()]
    for name, typ in cols:
        if name not in existing:
            try:
                db.execute(f"ALTER TABLE {table} ADD COLUMN {name} {typ}")
                print(f"  + {table}.{name} ({typ})")
            except Exception as e:
                print(f"  ! {table}.{name}: {e}")
        else:
            print(f"  = {table}.{name} exists")

db.commit()

# Verify
print("\nFinal schemas:")
for table in tables:
    cols = [r[1] for r in db.execute(f"PRAGMA table_info({table})").fetchall()]
    print(f"  {table}: {cols}")

db.close()
print("\nMigration complete.")
