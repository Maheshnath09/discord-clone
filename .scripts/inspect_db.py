import sqlite3, json, os
db_path = os.path.join('backend', 'chat_app.db')
if not os.path.exists(db_path):
    print(f"DB not found at {db_path}")
    raise SystemExit(1)
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("SELECT id, username, email, password_hash FROM users")
rows = c.fetchall()
print(json.dumps(rows, indent=2))
