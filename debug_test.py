import urllib.request, json

d = json.dumps({"phone": "13800000000", "password": "admin123"}).encode()
r = urllib.request.Request("http://localhost:5000/api/auth/login", data=d, headers={"Content-Type": "application/json"})
try:
    resp = urllib.request.urlopen(r)
    print('Login OK:', resp.read().decode()[:100])
except urllib.request.HTTPError as e:
    print('Login failed:', e.code, e.read().decode()[:100])
except Exception as e:
    print('Error:', e)

# Also test get_json_body directly
import sys
sys.path.insert(0, '/home/ubuntu/zhongyizhiban')
from flask import Flask
from app import app as flask_app
with flask_app.test_request_context('/test', method='POST', data=json.dumps({"test": "value"}), content_type='application/json'):
    body = json.loads(flask_app.request.get_json(silent=True) or "{}")
    print('Test context:', body)
