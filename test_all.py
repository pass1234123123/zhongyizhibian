import urllib.request, json, sqlite3, hashlib, sys

print('=== 1. Login API ===')
try:
    d = json.dumps({'phone': '13800000000', 'password': 'admin123'}).encode()
    r = urllib.request.Request('http://localhost:5000/api/auth/login', data=d, headers={'Content-Type': 'application/json'})
    resp = urllib.request.urlopen(r, timeout=5)
    j = json.loads(resp.read())
    if 'token' in j:
        print('LOGIN OK - token: ' + j['token'][:20] + '...')
    else:
        print('LOGIN FAILED:', j)
except Exception as e:
    print('LOGIN ERROR:', e)

print()
print('=== 2. Admin page ===')
try:
    resp = urllib.request.urlopen('http://localhost:5000/admin', timeout=5)
    html = resp.read().decode('utf-8')
    print('HTTP', resp.status, '- HTML size:', len(html))
    for c in ['async function adminLogin', 'function api', 'function t(', 'login-btn']:
        print('Has', repr(c), ':', c in html)
    # Count adminLogin
    print('adminLogin count:', html.count('adminLogin'))
except Exception as e:
    print('ADMIN ERROR:', e)

print()
print('=== 3. Database ===')
try:
    db = sqlite3.connect('/home/ubuntu/zhongyizhiban/zhongyi.db')
    u = db.execute('SELECT id, phone, password_hash, role FROM users WHERE phone=?', ('13800000000',)).fetchone()
    if u:
        h = hashlib.sha256(b'admin123').hexdigest()
        print('User: id=%d, phone=%s, role=%s, hash_match=%s' % (u[0], u[1], u[3], str(u[2] == h)))
    else:
        print('Admin user NOT FOUND')
    db.close()
except Exception as e:
    print('DB ERROR:', e)

print()
print('=== Done ===')
