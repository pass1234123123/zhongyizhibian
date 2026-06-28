import hashlib, sqlite3, sys

h = hashlib.sha256(b'admin123').hexdigest()
print('Computed hash:', h)

db = sqlite3.connect('/home/ubuntu/zhongyizhiban/zhongyi.db')
rows = db.execute('SELECT id, phone, password_hash, role FROM users').fetchall()
for r in rows:
    print(f'User: id={r[0]}, phone={r[1]}, role={r[3]}')
    print(f'  DB hash:    {r[2]}')
    print(f'  Computed:   {h}')
    print(f'  Match:      {r[2] == h}')

# Test with the actual app
sys.path.insert(0, '/home/ubuntu/zhongyizhiban')
from app import hash_password
print()
print('Using app.hash_password:', hash_password('admin123'))
test_h = hash_password('admin123')
print(f'Match via hash_password: {rows[0][2] == test_h if rows else "N/A"}')

db.close()
