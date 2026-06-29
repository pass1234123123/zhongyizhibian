import sqlite3, hashlib
db = sqlite3.connect('/home/ubuntu/zhongyizhiban/zhongyi.db')
users = db.execute('SELECT id, phone, password_hash, role FROM users').fetchall()
for u in users:
    print(f'User: id={u[0]}, phone={u[1]}, hash={u[2]}, role={u[3]}')
h = hashlib.sha256(b'admin123').hexdigest()
print(f'Expected hash: {h}')
if users and users[0][2] == h:
    print('Hashes MATCH')
else:
    print('Hashes DO NOT MATCH')
db.close()
