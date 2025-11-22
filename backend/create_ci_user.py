from app.core.security import get_password_hash
import sqlite3

pw = get_password_hash('password123')
conn = sqlite3.connect('chat_app.db')
c = conn.cursor()
try:
    c.execute("INSERT INTO users (username,email,password_hash,display_name,is_verified,is_active) VALUES (?,?,?,?,1,1)", ('ci_user','ci_user@localtest.me', pw, 'CI User'))
    conn.commit()
    print('inserted')
except Exception as e:
    print('error', e)
finally:
    conn.close()
