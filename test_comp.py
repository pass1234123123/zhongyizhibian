#!/usr/bin/env python
"""Comprehensive API test for TCM Platform."""
import requests, json

BASE = 'http://127.0.0.1:5000'
failed = 0

def t(name, func):
    global failed
    try:
        func()
        print(f'  OK   {name}')
    except Exception as e:
        print(f'  FAIL {name}: {e}')
        failed += 1

def check(resp, expected_keys=None, status=200):
    if resp.status_code != status:
        raise Exception(f'Expected {status}, got {resp.status_code}: {resp.text[:200]}')
    data = resp.json()
    if expected_keys:
        for k in expected_keys:
            if k not in data:
                raise Exception(f'Missing key "{k}" in response')
    return data

print('=== API Test Suite ===')

# 1. Categories
def test_categories():
    r = requests.get(f'{BASE}/api/categories')
    data = check(r, status=200)
    assert len(data) == 13, f'Expected 13 categories, got {len(data)}'
    names = [c['name'] for c in data]
    assert '内科' in names
t('GET /api/categories (13 categories)', test_categories)

# 2. Diseases
def test_diseases():
    r = requests.get(f'{BASE}/api/diseases')
    data = check(r, status=200)
    assert len(data) > 10, f'Expected many diseases'
    
    r2 = requests.get(f'{BASE}/api/diseases?category_id=1')
    data2 = check(r2, status=200)
    names = [d['name'] for d in data2]
    assert '胃痛' in names
t('GET /api/diseases (filter by category)', test_diseases)

# 3. Disease Detail
def test_disease_detail():
    r = requests.get(f'{BASE}/api/diseases/101')
    check(r, status=200)
t('GET /api/diseases/101', test_disease_detail)

# 4. Treatments
def test_treatments():
    r = requests.get(f'{BASE}/api/treatments?disease_id=101')
    data = check(r, status=200)
    assert len(data) == 5, f'Expected 5 treatments for 胃痛, got {len(data)}'
    titles = [t['title'] for t in data]
    assert '胃痛温中健脾方' in titles, f'Expected 胃痛温中健脾方, got {titles}'
    assert data[0]['price'] > 0
t('GET /api/treatments?disease_id=101 (5 treatments)', test_treatments)

# 5. Search
def test_search():
    r = requests.get(f'{BASE}/api/treatments?search=胃痛')
    data = check(r, status=200)
    assert len(data) >= 5, f'Expected >=5 results for 胃痛'
t('GET /api/treatments?search=胃痛', test_search)

# 6. Treatment Types
def test_types():
    r = requests.get(f'{BASE}/api/treatments/types')
    data = check(r, status=200)
    assert '针灸' in data
t('GET /api/treatments/types', test_types)

# 7. Register
def test_register():
    # Generate unique phone to avoid conflict
    import random
    phone = f'139{random.randint(10000000, 99999999)}'
    r = requests.post(f'{BASE}/api/auth/register', json={
        'phone': phone, 'password': 'test123', 'username': '测试用户'
    })
    data = check(r, expected_keys=['token', 'user'], status=200)
    global test_token, test_user
    test_token = data['token']
    test_user = data['user']
    assert test_user['role'] == 'user'
    assert test_user['points'] == 0
t('POST /api/auth/register', test_register)

# 8. Login
def test_login():
    r = requests.post(f'{BASE}/api/auth/login', json={
        'phone': test_user['phone'], 'password': 'test123'
    })
    data = check(r, expected_keys=['token', 'user'], status=200)
    assert data['user']['id'] == test_user['id']
t('POST /api/auth/login', test_login)

# 9. Admin Login (built-in)
def test_admin_login():
    r = requests.post(f'{BASE}/api/auth/login', json={
        'phone': '13800000000', 'password': 'admin123'
    })
    data = check(r, expected_keys=['token', 'user'], status=200)
    assert data['user']['role'] == 'admin'
    global admin_token
    admin_token = data['token']
t('POST /api/auth/login (admin)', test_admin_login)

# 10. Auth Me
def test_auth_me():
    r = requests.get(f'{BASE}/api/auth/me', headers={'Authorization': f'Bearer {test_token}'})
    data = check(r, status=200)
    assert data['id'] == test_user['id']
t('GET /api/auth/me', test_auth_me)

# 11. Treatment Detail (as user, not purchased - should show preview only)
def test_treatment_detail():
    r = requests.get(f'{BASE}/api/treatments/10101', headers={'Authorization': f'Bearer {test_token}'})
    data = check(r, expected_keys=['title', 'price', 'preview', 'is_purchased'], status=200)
    assert data['is_purchased'] == False
    assert 'full_content' not in data, 'Non-purchased user should not see full content'
t('GET /api/treatments/10101 (not purchased)', test_treatment_detail)

# 12. Purchase
def test_purchase():
    r = requests.post(f'{BASE}/api/purchase', 
        headers={'Authorization': f'Bearer {test_token}'},
        json={'treatment_id': 10101})
    data = check(r, status=200)
    assert data['treatment_id'] == 10101
t('POST /api/purchase (10101)', test_purchase)

# 13. Treatment Detail AFTER purchase
def test_treatment_detail_purchased():
    r = requests.get(f'{BASE}/api/treatments/10101', headers={'Authorization': f'Bearer {test_token}'})
    data = check(r, status=200)
    assert data['is_purchased'] == True
    assert 'full_content' in data, 'Purchased user should see full content'
    assert '方名' in data['full_content'], 'Full content should be Chinese medicine text'
    assert data['formulas'] is not None
    assert len(data['formulas']) > 0
t('GET /api/treatments/10101 (purchased)', test_treatment_detail_purchased)

# 14. Full Content
def test_full_content():
    r = requests.get(f'{BASE}/api/treatments/10101/full', 
        headers={'Authorization': f'Bearer {test_token}'})
    data = check(r, status=200)
    assert 'full_content' in data
t('GET /api/treatments/10101/full', test_full_content)

# 15. Toggle Favorite
def test_fav_toggle():
    r = requests.post(f'{BASE}/api/favorites/toggle',
        headers={'Authorization': f'Bearer {test_token}'},
        json={'treatment_id': 10101})
    data = check(r, status=200)
    assert data['favorited'] == True
    
    # Toggle back
    r2 = requests.post(f'{BASE}/api/favorites/toggle',
        headers={'Authorization': f'Bearer {test_token}'},
        json={'treatment_id': 10101})
    data2 = check(r2, status=200)
    assert data2['favorited'] == False
t('POST /api/favorites/toggle', test_fav_toggle)

# 16. Get Favorites
def test_get_favs():
    # First favorite something
    requests.post(f'{BASE}/api/favorites/toggle',
        headers={'Authorization': f'Bearer {test_token}'},
        json={'treatment_id': 10102})
    
    r = requests.get(f'{BASE}/api/favorites',
        headers={'Authorization': f'Bearer {test_token}'})
    data = check(r, status=200)
    assert len(data) >= 1
    assert data[0]['treatment_id'] == 10102
t('GET /api/favorites', test_get_favs)

# 17. Submit Feedback
def test_feedback():
    r = requests.post(f'{BASE}/api/feedback',
        headers={'Authorization': f'Bearer {test_token}'},
        json={'treatment_id': 10101, 'rating': 5, 'efficacy': 'effective', 
              'description': '效果非常好，3天症状明显缓解', 'course_days': 7})
    data = check(r, status=200)
    assert 'points_awarded' in data
    assert data['points_awarded'] == 50
t('POST /api/feedback', test_feedback)

# 18. Get Feedback
def test_get_feedback():
    r = requests.get(f'{BASE}/api/feedback/10101')
    data = check(r, status=200)
    assert data['total'] >= 1
    assert data['avg_rating'] >= 4.0
    assert 'effective' in data['efficacy_stats']
    assert len(data['list']) >= 1
    assert data['list'][0]['description'] is not None
t('GET /api/feedback/10101', test_get_feedback)

# 19. Check Points
def test_points():
    r = requests.get(f'{BASE}/api/auth/me', headers={'Authorization': f'Bearer {test_token}'})
    data = check(r, status=200)
    assert data['points'] >= 50, 'Expected >=50 points, got %d' % data['points']
t('GET /api/auth/me (points after feedback)', test_points)

# 20. Upload Content
def test_upload():
    content = '胃痛验方：高良姜15g、香附15g、延胡索12g，水煎服，每日1剂。主治寒凝气滞型胃痛。'
    r = requests.post(f'{BASE}/api/upload',
        headers={'Authorization': f'Bearer {test_token}'},
        json={'content': content})
    data = check(r, status=200)
    assert data['upload_id'] > 0
    assert data['status'] == 'pending'
    global upload_id
    upload_id = data['upload_id']
t('POST /api/upload', test_upload)

# 21. Get Uploads
def test_get_uploads():
    r = requests.get(f'{BASE}/api/uploads',
        headers={'Authorization': f'Bearer {test_token}'})
    data = check(r, status=200)
    assert len(data) >= 1
    upload = next((x for x in data if x['id'] == upload_id), None)
    assert upload is not None
    assert upload['content'].startswith('胃痛验方')
    assert upload['ai_result'] is not None
t('GET /api/uploads', test_get_uploads)

# 22. Admin Pending
def test_admin_pending():
    r = requests.get(f'{BASE}/api/admin/pending?status=pending',
        headers={'Authorization': f'Bearer {admin_token}'})
    data = check(r, status=200)
    assert len(data) >= 1
t('GET /api/admin/pending (admin)', test_admin_pending)

# 23. Admin Approve
def test_admin_approve():
    r = requests.post(f'{BASE}/api/admin/review',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'upload_id': upload_id, 'action': 'approve'})
    data = check(r, status=200)
t('POST /api/admin/review (approve)', test_admin_approve)

# 24. Admin Reject
def test_admin_reject():
    # First upload another one
    r = requests.post(f'{BASE}/api/upload',
        headers={'Authorization': f'Bearer {test_token}'},
        json={'content': '测试用验方：生姜3片、红糖适量，水煎服。'})
    data = check(r, status=200)
    reject_id = data['upload_id']
    
    r2 = requests.post(f'{BASE}/api/admin/review',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'upload_id': reject_id, 'action': 'reject', 'review_note': '内容不完整，请补充更多细节'})
    data2 = check(r2, status=200)
t('POST /api/admin/review (reject)', test_admin_reject)

# 25. Points Log
def test_points_log():
    r = requests.get(f'{BASE}/api/points/log',
        headers={'Authorization': f'Bearer {test_token}'})
    data = check(r, status=200)
    assert len(data) >= 1
    assert data[0]['amount'] == 50
    assert data[0]['source_type'] == 'feedback'
t('GET /api/points/log', test_points_log)

# Print summary
print(f'\n=== Results: {25 - failed}/25 passed, {failed} failed ===')
