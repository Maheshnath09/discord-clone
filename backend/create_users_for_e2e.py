from app.core.security import get_password_hash
import sqlite3

conn = sqlite3.connect('chat_app.db')
c = conn.cursor()
users = [
    ('ci_user_a','ci_user_a@localtest.me'),
    ('ci_user_b','ci_user_b@localtest.me')
]
for username,email in users:
    pw = get_password_hash('password123')
    try:
        c.execute("INSERT INTO users (username,email,password_hash,display_name,is_verified,is_active) VALUES (?,?,?,?,1,1)", (username,email, pw, username))
        print('inserted', username)
    except Exception as e:
        print('error inserting', username, e)
conn.commit()
conn.close()
