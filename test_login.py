import urllib.request, json
try:
    data = json.dumps({"phone": "13800000000", "password": "admin123"}).encode()
    req = urllib.request.Request("http://localhost:5000/api/auth/login", data=data, headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req, timeout=5)
    result = json.loads(resp.read())
    print(f'Login OK: token={result.get("token","")[:20]}... role={result.get("user",{}).get("role","?")}')
except urllib.request.HTTPError as e:
    print(f'Login FAILED: HTTP {e.code}, body={e.read().decode()[:100]}')
except Exception as e:
    print(f'Login ERROR: {e}')
