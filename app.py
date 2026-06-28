import os
import json
import hashlib
import uuid
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import jwt

from config import SECRET_KEY, JWT_EXPIRATION_HOURS, UPLOAD_FOLDER
from models import get_db, init_db, seed_data
from ai_processor import extract_text_from_file, call_deepseek, process_and_insert

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app, supports_credentials=True)


# ─── JWT Helpers ───────────────────────────────────────────────
def make_token(user_id, role):
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return jsonify({'error': '未提供认证令牌'}), 401
        try:
            token = auth.split(' ')[1]
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.current_user = data
        except jwt.ExpiredSignatureError:
            return jsonify({'error': '令牌已过期，请重新登录'}), 401
        except:
            return jsonify({'error': '无效的令牌'}), 401
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if request.current_user.get('role') not in ('admin', 'reviewer'):
            return jsonify({'error': '需要管理员权限'}), 403
        return f(*args, **kwargs)
    return decorated


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def get_member_status(user_id):
    db = get_db()
    member = db.execute('''
        SELECT m.*, ms.annual_fee FROM members m
        LEFT JOIN member_settings ms ON ms.id=1
        WHERE m.user_id=? AND m.status="active" AND m.end_date > datetime("now")
    ''', (user_id,)).fetchone()
    approved_count = db.execute(
        'SELECT COUNT(*) as cnt FROM uploads WHERE user_id=? AND status="approved"',
        (user_id,)).fetchone()['cnt']
    today_views = db.execute(
        'SELECT COUNT(*) as cnt FROM view_log WHERE user_id=? AND date(created_at)=date("now")',
        (user_id,)).fetchone()['cnt']
    settings = db.execute('SELECT * FROM member_settings WHERE id=1').fetchone()
    db.close()
    return {
        'is_member': member is not None,
        'member_type': member['type'] if member else None,
        'member_end': member['end_date'] if member else None,
        'member_status': member['status'] if member else None,
        'approved_uploads': approved_count,
        'today_views': today_views,
        'annual_fee': settings['annual_fee'] if settings else 199.0,
        'free_duration_days': settings['free_duration_days'] if settings else 365
    }


def can_view_full(user_id, treatment_id):
    status = get_member_status(user_id)
    if status['is_member']:
        return True, '会员可查看全部内容'
    # Non-member: track views and limit to 1
    db = get_db()
    existing = db.execute('SELECT id FROM view_log WHERE user_id=? AND treatment_id=?', (user_id, treatment_id)).fetchone()
    if not existing:
        db.execute('INSERT INTO view_log (user_id, treatment_id) VALUES (?,?)', (user_id, treatment_id))
        db.commit()
    db.close()
    total = status['today_views']
    if total < 1:
        return True, '今日剩余1次免费查看'
    return False, '非会员每日仅可查看1个方案，开通会员可查看全部'


def get_json_body():
    return request.get_json(silent=True) or {}


def to_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


# ─── Serve Frontend ────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/admin')
def admin_panel():
    return render_template('admin.html')


@app.route('/api/init', methods=['POST'])
def api_init():
    """初始化数据库（只在首次运行有效）"""
    init_db()
    seed_data()
    return jsonify({'message': '数据库初始化完成'})


# ─── Auth ──────────────────────────────────────────────────────
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = get_json_body()
    phone = data.get('phone', '').strip()
    password = data.get('password', '')
    username = data.get('username', '').strip()
    
    if not phone or len(phone) < 8:
        return jsonify({'error': '请输入有效的手机号'}), 400
    if not password or len(password) < 6:
        return jsonify({'error': '密码至少6位'}), 400
    
    db = get_db()
    existing = db.execute('SELECT id FROM users WHERE phone=?', (phone,)).fetchone()
    if existing:
        db.close()
        return jsonify({'error': '该手机号已注册'}), 400
    
    if not username:
        username = '用户' + phone[-4:]
    
    password_hash = hash_password(password)
    db.execute('INSERT INTO users (phone, username, password_hash) VALUES (?,?,?)',
               (phone, username, password_hash))
    db.commit()
    user = db.execute('SELECT * FROM users WHERE phone=?', (phone,)).fetchone()
    token = make_token(user['id'], user['role'])
    db.close()
    
    return jsonify({
        'token': token,
        'user': {'id': user['id'], 'phone': user['phone'], 'username': user['username'],
                 'role': user['role'], 'points': user['points'], 'balance': user['balance']}
    })


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = get_json_body()
    phone = data.get('phone', '').strip()
    password = data.get('password', '')
    
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE phone=?', (phone,)).fetchone()
    db.close()
    
    if not user or user['password_hash'] != hash_password(password):
        return jsonify({'error': '手机号或密码错误'}), 401
    
    token = make_token(user['id'], user['role'])
    return jsonify({
        'token': token,
        'user': {'id': user['id'], 'phone': user['phone'], 'username': user['username'],
                 'role': user['role'], 'points': user['points'], 'balance': user['balance']}
    })


@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_me():
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id=?', (request.current_user['user_id'],)).fetchone()
    db.close()
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    return jsonify({
        'id': user['id'], 'phone': user['phone'], 'username': user['username'],
        'role': user['role'], 'points': user['points'], 'balance': user['balance'],
        'avatar': user['avatar'], 'total_earnings': user['total_earnings']
    })


# ─── Categories & Diseases ─────────────────────────────────────
@app.route('/api/categories', methods=['GET'])
def get_categories():
    db = get_db()
    cats = db.execute('SELECT * FROM disease_categories ORDER BY id').fetchall()
    result = []
    for c in cats:
        count = db.execute('SELECT COUNT(*) as cnt FROM diseases WHERE category_id=?', (c['id'],)).fetchone()['cnt']
        result.append({'id': c['id'], 'name': c['name'], 'icon': c['icon'], 'color': c['color'], 'disease_count': count})
    db.close()
    return jsonify(result)


@app.route('/api/diseases', methods=['GET'])
def get_diseases():
    category_id = request.args.get('category_id', type=int)
    db = get_db()
    if category_id:
        diseases = db.execute('SELECT * FROM diseases WHERE category_id=? ORDER BY id', (category_id,)).fetchall()
    else:
        diseases = db.execute('SELECT * FROM diseases ORDER BY id').fetchall()
    result = []
    for d in diseases:
        count = db.execute('SELECT COUNT(*) as cnt FROM treatments WHERE disease_id=? AND status="published"', (d['id'],)).fetchone()['cnt']
        result.append({'id': d['id'], 'category_id': d['category_id'], 'name': d['name'],
                        'icon': d['icon'], 'treatment_count': count})
    db.close()
    return jsonify(result)


@app.route('/api/diseases/<int:disease_id>', methods=['GET'])
def get_disease_detail(disease_id):
    db = get_db()
    d = db.execute('SELECT * FROM diseases WHERE id=?', (disease_id,)).fetchone()
    if not d:
        db.close()
        return jsonify({'error': '疾病不存在'}), 404
    cat = db.execute('SELECT * FROM disease_categories WHERE id=?', (d['category_id'],)).fetchone()
    db.close()
    return jsonify({
        'id': d['id'], 'name': d['name'], 'icon': d['icon'],
        'category_id': d['category_id'], 'category_name': cat['name'] if cat else ''
    })


# ─── Treatments ────────────────────────────────────────────────
@app.route('/api/treatments', methods=['GET'])
def get_treatments():
    disease_id = request.args.get('disease_id', type=int)
    search = request.args.get('search', '').strip()
    type_filter = request.args.get('type', '').strip()
    sort = request.args.get('sort', 'default')
    
    db = get_db()
    query = 'SELECT DISTINCT t.* FROM treatments t WHERE t.status="published"'
    params = []
    
    if disease_id:
        query += ' AND t.disease_id=?'
        params.append(disease_id)
    
    if search:
        query += ' AND t.title LIKE ?'
        params.append(f'%{search}%')
    
    if type_filter:
        query += ' AND t.id IN (SELECT treatment_id FROM treatment_type_relations WHERE type_name=?)'
        params.append(type_filter)
    
    if sort == 'rating':
        query += ' ORDER BY t.rating DESC'
    elif sort == 'price':
        query += ' ORDER BY t.price ASC'
    elif sort == 'popular':
        query += ' ORDER BY t.feedback_count DESC'
    else:
        query += ' ORDER BY t.id ASC'
    
    treatments = db.execute(query, params).fetchall()
    result = []
    for t in treatments:
        types = [r['type_name'] for r in db.execute('SELECT type_name FROM treatment_type_relations WHERE treatment_id=?', (t['id'],)).fetchall()]
        result.append({
            'id': t['id'], 'title': t['title'], 'price': t['price'],
            'rating': t['rating'], 'feedback_count': t['feedback_count'],
            'effective_rate': t['effective_rate'], 'preview': t['preview'],
            'types': types, 'is_special': bool(t['is_special']),
            'disease_id': t['disease_id']
        })
    db.close()
    return jsonify(result)


@app.route('/api/treatments/<int:treatment_id>', methods=['GET'])
@token_required
def get_treatment_detail(treatment_id):
    db = get_db()
    t = db.execute('SELECT * FROM treatments WHERE id=?', (treatment_id,)).fetchone()
    if not t:
        db.close()
        return jsonify({'error': '治疗方案不存在'}), 404
    
    # Check if user purchased
    user_id = request.current_user['user_id']
    can_view, view_msg = can_view_full(user_id, treatment_id)
    member_status = get_member_status(user_id)
    
    types = [r['type_name'] for r in db.execute('SELECT type_name FROM treatment_type_relations WHERE treatment_id=?', (treatment_id,)).fetchall()]
    formulas = [dict(r) for r in db.execute('SELECT * FROM treatment_formulas WHERE treatment_id=?', (treatment_id,)).fetchall()]
    acupoints = [dict(r) for r in db.execute('SELECT * FROM treatment_acupoints WHERE treatment_id=?', (treatment_id,)).fetchall()]
    
    # Check if favorited
    fav = db.execute('SELECT id FROM favorites WHERE user_id=? AND treatment_id=?', (user_id, treatment_id)).fetchone()
    
    result = {
        'id': t['id'], 'title': t['title'], 'price': t['price'],
        'rating': t['rating'], 'feedback_count': t['feedback_count'],
        'effective_rate': t['effective_rate'], 'preview': t['preview'],
        'types': types, 'is_special': bool(t['is_special']), 'is_favorited': fav is not None,
        'can_view': can_view, 'view_msg': view_msg,
        'is_member': member_status['is_member'],
        'member_type': member_status['member_type'],
        'member_end': member_status['member_end'],
        'approved_uploads': member_status['approved_uploads'],
        'formulas': formulas, 'acupoints': acupoints
    }
    
    if can_view:
        result['full_content'] = t['full_content']
    
    db.close()
    return jsonify(result)


@app.route('/api/treatments/<int:treatment_id>/full', methods=['GET'])
@token_required
def get_treatment_full(treatment_id):
    db = get_db()
    t = db.execute('SELECT * FROM treatments WHERE id=?', (treatment_id,)).fetchone()
    if not t:
        db.close()
        return jsonify({'error': '治疗方案不存在'}), 404
    
    user_id = request.current_user['user_id']
    can_view, view_msg = can_view_full(user_id, treatment_id)
    
    if not can_view:
        db.close()
        return jsonify({'error': view_msg, 'can_view': False}), 403
    
    formulas = [dict(r) for r in db.execute('SELECT * FROM treatment_formulas WHERE treatment_id=?', (treatment_id,)).fetchall()]
    acupoints = [dict(r) for r in db.execute('SELECT * FROM treatment_acupoints WHERE treatment_id=?', (treatment_id,)).fetchall()]
    
    db.close()
    return jsonify({
        'id': t['id'], 'full_content': t['full_content'],
        'formulas': formulas, 'acupoints': acupoints
    })


@app.route('/api/treatments/types', methods=['GET'])
def get_treatment_types():
    db = get_db()
    types = [r['name'] for r in db.execute('SELECT name FROM treatment_types ORDER BY name').fetchall()]
    db.close()
    return jsonify(types)


# ─── Purchase (Simulated) ──────────────────────────────────────
@app.route('/api/purchase', methods=['POST'])
@token_required
def purchase_treatment():
    data = get_json_body()
    treatment_id = to_int(data.get('treatment_id'))
    user_id = request.current_user['user_id']
    
    db = get_db()
    t = db.execute('SELECT * FROM treatments WHERE id=?', (treatment_id,)).fetchone()
    if not t:
        db.close()
        return jsonify({'error': '治疗方案不存在'}), 404
    
    can_view, view_msg = can_view_full(user_id, treatment_id)
    if can_view:
        db.close()
        return jsonify({'message': '已是会员可免费查看', 'already_purchased': True, 'is_member': True})
    
    # Legacy: record purchase for non-members
    db.execute('INSERT INTO purchases (user_id, treatment_id, amount) VALUES (?,?,?)',
               (user_id, treatment_id, t['price']))
    
    # Award points to uploader (split 50%)
    if t['uploader_id'] and t['uploader_id'] != 0 and t['uploader_id'] != user_id:
        amount_share = t['price'] * 0.5
        db.execute('UPDATE users SET balance=balance+?, total_earnings=total_earnings+? WHERE id=?',
                    (amount_share, amount_share, t['uploader_id']))
    
    db.commit()
    db.close()
    return jsonify({'message': '购买成功！', 'treatment_id': treatment_id, 'amount': t['price']})


@app.route('/api/purchases', methods=['GET'])
@token_required
def get_purchases():
    user_id = request.current_user['user_id']
    db = get_db()
    rows = db.execute('''
        SELECT p.*, t.title, t.price, t.rating, t.effective_rate
        FROM purchases p JOIN treatments t ON p.treatment_id=t.id
        WHERE p.user_id=? ORDER BY p.created_at DESC
    ''', (user_id,)).fetchall()
    result = [dict(r) for r in rows]
    db.close()
    return jsonify(result)


# ─── Favorites ─────────────────────────────────────────────────
@app.route('/api/favorites', methods=['GET'])
@token_required
def get_favorites():
    user_id = request.current_user['user_id']
    db = get_db()
    rows = db.execute('''
        SELECT f.*, t.title, t.price, t.rating, t.effective_rate, t.preview
        FROM favorites f JOIN treatments t ON f.treatment_id=t.id
        WHERE f.user_id=? ORDER BY f.created_at DESC
    ''', (user_id,)).fetchall()
    
    result = []
    for r in rows:
        types = [x['type_name'] for x in db.execute('SELECT type_name FROM treatment_type_relations WHERE treatment_id=?', (r['treatment_id'],)).fetchall()]
        result.append({**dict(r), 'types': types})
    
    db.close()
    return jsonify(result)


@app.route('/api/favorites/toggle', methods=['POST'])
@token_required
def toggle_favorite():
    data = get_json_body()
    treatment_id = to_int(data.get('treatment_id'))
    user_id = request.current_user['user_id']

    if not treatment_id:
        return jsonify({'error': '请指定治疗方案'}), 400
    
    db = get_db()
    treatment = db.execute('SELECT id FROM treatments WHERE id=? AND status="published"', (treatment_id,)).fetchone()
    if not treatment:
        db.close()
        return jsonify({'error': '治疗方案不存在'}), 404

    existing = db.execute('SELECT id FROM favorites WHERE user_id=? AND treatment_id=?', (user_id, treatment_id)).fetchone()
    
    if existing:
        db.execute('DELETE FROM favorites WHERE id=?', (existing['id'],))
        db.commit()
        db.close()
        return jsonify({'favorited': False, 'message': '已取消收藏'})
    else:
        db.execute('INSERT INTO favorites (user_id, treatment_id) VALUES (?,?)', (user_id, treatment_id))
        db.commit()
        db.close()
        return jsonify({'favorited': True, 'message': '已收藏'})


# ─── Feedback ──────────────────────────────────────────────────
@app.route('/api/feedback', methods=['POST'])
@token_required
def submit_feedback():
    data = get_json_body()
    treatment_id = to_int(data.get('treatment_id'))
    rating = to_int(data.get('rating'), 5)
    efficacy = data.get('efficacy', '')
    description = data.get('description', '')
    course_days = max(0, to_int(data.get('course_days')))
    user_id = request.current_user['user_id']
    
    if not treatment_id:
        return jsonify({'error': '请指定治疗方案'}), 400
    if rating < 1 or rating > 5:
        return jsonify({'error': '评分范围为1-5'}), 400
    
    db = get_db()
    # Check purchase
    member = db.execute('SELECT id FROM members WHERE user_id=? AND status="active" AND end_date > datetime("now")', (user_id,)).fetchone()
    purchased = db.execute('SELECT id FROM purchases WHERE user_id=? AND treatment_id=?', (user_id, treatment_id)).fetchone()
    viewed = db.execute('SELECT id FROM view_log WHERE user_id=? AND treatment_id=?', (user_id, treatment_id)).fetchone()
    if not purchased and not member and not viewed:
        db.close()
        return jsonify({'error': '请先查看内容后再提交反馈'}), 403
    
    existing_fb = db.execute('SELECT id FROM feedbacks WHERE user_id=? AND treatment_id=?', (user_id, treatment_id)).fetchone()
    if existing_fb:
        db.close()
        return jsonify({'error': '您已提交过反馈'}), 400
    
    db.execute('INSERT INTO feedbacks (user_id, treatment_id, rating, efficacy, description, course_days) VALUES (?,?,?,?,?,?)',
               (user_id, treatment_id, rating, efficacy, description, course_days))
    
    # Update treatment stats
    stats = db.execute('SELECT COUNT(*) as cnt, AVG(rating) as avg FROM feedbacks WHERE treatment_id=?', (treatment_id,)).fetchone()
    eff_count = db.execute('SELECT COUNT(*) as cnt FROM feedbacks WHERE treatment_id=? AND efficacy="effective"', (treatment_id,)).fetchone()['cnt']
    total_fb = stats['cnt']
    eff_rate = int(eff_count / total_fb * 100) if total_fb > 0 else 0
    
    db.execute('UPDATE treatments SET rating=?, feedback_count=?, effective_rate=? WHERE id=?',
               (round(stats['avg'], 1), total_fb, eff_rate, treatment_id))
    
    # Award points
    db.execute('UPDATE users SET points=points+50 WHERE id=?', (user_id,))
    user = db.execute('SELECT points FROM users WHERE id=?', (user_id,)).fetchone()
    db.execute('INSERT INTO points_log (user_id, amount, balance_after, source_type, source_id, note) VALUES (?,50,?,?,?,?)',
               (user_id, user['points'], 'feedback', treatment_id, '提交疗效反馈奖励'))
    
    db.commit()
    db.close()
    return jsonify({'message': '反馈提交成功，获得50积分！', 'points_awarded': 50})


@app.route('/api/feedback/<int:treatment_id>', methods=['GET'])
def get_feedback(treatment_id):
    db = get_db()
    # Aggregate stats
    stats = db.execute('SELECT COUNT(*) as cnt, AVG(rating) as avg FROM feedbacks WHERE treatment_id=?', (treatment_id,)).fetchone()
    efficacy_stats = {}
    for row in db.execute('SELECT efficacy, COUNT(*) as cnt FROM feedbacks WHERE treatment_id=? GROUP BY efficacy', (treatment_id,)).fetchall():
        efficacy_stats[row['efficacy']] = row['cnt']
    
    total = stats['cnt'] or 0
    avg_rating = round(stats['avg'], 1) if stats['avg'] else 0
    
    # Rating distribution
    distribution = {}
    for i in range(1, 6):
        cnt = db.execute('SELECT COUNT(*) as cnt FROM feedbacks WHERE treatment_id=? AND rating=?', (treatment_id, i)).fetchone()['cnt']
        distribution[str(i)] = cnt
    
    # Feedback list
    fb_list = db.execute('''
        SELECT f.*, u.username
        FROM feedbacks f JOIN users u ON f.user_id=u.id
        WHERE f.treatment_id=? ORDER BY f.created_at DESC
        LIMIT 50
    ''', (treatment_id,)).fetchall()
    
    db.close()
    return jsonify({
        'total': total,
        'avg_rating': avg_rating,
        'efficacy_stats': efficacy_stats,
        'distribution': distribution,
        'list': [dict(r) for r in fb_list]
    })


# ─── Upload ────────────────────────────────────────────────────
@app.route('/api/upload', methods=['POST'])
@token_required
def upload_content():
    user_id = request.current_user['user_id']
    data = get_json_body()
    content = (data.get('content') if request.is_json else request.form.get('content', '')) or ''
    content = content.strip()
    files = request.files
    
    file_names = []
    saved_files = []
    for _, f in files.items(multi=True):
        if f.filename:
            ext = os.path.splitext(f.filename)[1].lower()
            saved_name = f'{uuid.uuid4().hex}{ext}'
            f.save(os.path.join(UPLOAD_FOLDER, saved_name))
            file_names.append(f.filename)
            saved_files.append(saved_name)

    if not content and not file_names:
        return jsonify({'error': '请粘贴内容或上传文件'}), 400
    
    db = get_db()
    db.execute('INSERT INTO uploads (user_id, content, file_names, ai_result, status) VALUES (?,?,?,?,?)',
               (user_id, content, ','.join(file_names),
                json.dumps({'title': '（AI自动提取中...）', 'disease_ids': [], 'types': []}, ensure_ascii=False),
                'processing'))
    upload_id = db.execute('SELECT last_insert_rowid() as id').fetchone()['id']
    
    # AI processing (use DeepSeek if configured)
    settings = db.execute('SELECT * FROM ai_settings WHERE id=1').fetchone()
    api_key = settings['api_key'] if settings else ''
    if api_key:
        try:
            from ai_processor import call_deepseek
            ai_text_for_result = content[:2000] if content else 'file content'
            ai_dict = call_deepseek(ai_text_for_result, api_key, settings.get('model', 'deepseek-chat'), settings.get('api_url', ''))
            if 'error' not in ai_dict:
                from ai_processor import process_and_insert
                db2 = get_db()
                process_and_insert(db2, ai_dict, user_id)
                db2.close()
                new_status = 'approved' if settings.get('auto_approve', 1) else 'pending'
                db.execute('UPDATE uploads SET ai_result=?, status=? WHERE id=?', (json.dumps(ai_dict, ensure_ascii=False), new_status, upload_id))
                db.commit()
                db.close()
                return jsonify({'message': '上传成功，AI已自动处理并入库！', 'upload_id': upload_id, 'status': new_status, 'auto_approved': bool(settings.get('auto_approve', 1))})
        except Exception as ex:
            pass
    ai_result = json.dumps({
        'title': '上传内容（AI自动提取）',
        'disease_ids': [],
        'types': [],
        'preview': content[:100] if content else '文件内容（AI提取中）',
        'saved_files': saved_files
    }, ensure_ascii=False)
    db.execute('UPDATE uploads SET ai_result=?, status="pending" WHERE id=?', (ai_result, upload_id))
    
    db.commit()
    db.close()
    return jsonify({'message': '上传成功，等待审核', 'upload_id': upload_id, 'status': 'pending'})


@app.route('/api/uploads', methods=['GET'])
@token_required
def get_uploads():
    user_id = request.current_user['user_id']
    role = request.current_user.get('role')
    
    db = get_db()
    if role in ('admin', 'reviewer'):
        rows = db.execute('''
            SELECT u.*, up.username as uploader_name
            FROM uploads u LEFT JOIN users up ON u.user_id=up.id
            ORDER BY u.created_at DESC LIMIT 50
        ''').fetchall()
    else:
        rows = db.execute('''
            SELECT * FROM uploads WHERE user_id=? ORDER BY created_at DESC
        ''', (user_id,)).fetchall()
    
    result = []
    for r in rows:
        d = dict(r)
        try:
            d['ai_result'] = json.loads(d['ai_result']) if d['ai_result'] else {}
        except:
            d['ai_result'] = {}
        result.append(d)
    
    db.close()
    return jsonify(result)


# ─── Admin: Review ─────────────────────────────────────────────
@app.route('/api/admin/pending', methods=['GET'])
@admin_required
def get_pending_uploads():
    status = request.args.get('status', 'pending')
    db = get_db()
    rows = db.execute('''
        SELECT u.*, up.username as uploader_name
        FROM uploads u LEFT JOIN users up ON u.user_id=up.id
        WHERE u.status=? ORDER BY u.created_at ASC LIMIT 50
    ''', (status,)).fetchall()
    result = []
    for r in rows:
        d = dict(r)
        try:
            d['ai_result'] = json.loads(d['ai_result']) if d['ai_result'] else {}
        except:
            d['ai_result'] = {}
        result.append(d)
    db.close()
    return jsonify(result)


@app.route('/api/admin/review', methods=['POST'])
@admin_required
def review_upload():
    data = get_json_body()
    upload_id = to_int(data.get('upload_id'))
    action = data.get('action', '')  # approve or reject
    review_note = data.get('review_note', '')
    reviewer_id = request.current_user['user_id']
    
    db = get_db()
    upload = db.execute('SELECT * FROM uploads WHERE id=?', (upload_id,)).fetchone()
    if not upload:
        db.close()
        return jsonify({'error': '内容不存在'}), 404
    if upload['status'] != 'pending':
        db.close()
        return jsonify({'error': '该内容已审核，不能重复操作'}), 400
    
    if action == 'approve':
        try:
            ai_result = json.loads(upload['ai_result']) if upload['ai_result'] else {}
        except:
            ai_result = {}
        
        # Create a new treatment from uploaded content
        db.execute('UPDATE uploads SET status="approved", reviewer_id=?, reviewed_at=CURRENT_TIMESTAMP WHERE id=?',
                   (reviewer_id, upload_id))
        
        # Award points to uploader
        if upload['user_id']:
            db.execute('UPDATE users SET points=points+100 WHERE id=?', (upload['user_id'],))
            user = db.execute('SELECT points FROM users WHERE id=?', (upload['user_id'],)).fetchone()
            if user:
                db.execute('INSERT INTO points_log (user_id, amount, balance_after, source_type, source_id, note) VALUES (?,100,?,?,?,?)',
                           (upload['user_id'], user['points'], 'upload_approved', upload_id, '内容审核通过奖励'))
        
        db.commit()
        db.close()
        return jsonify({'message': '已审核通过，内容发布成功'})
    
    elif action == 'reject':
        db.execute('UPDATE uploads SET status="rejected", review_note=?, reviewer_id=?, reviewed_at=CURRENT_TIMESTAMP WHERE id=?',
                   (review_note, reviewer_id, upload_id))
        db.commit()
        db.close()
        return jsonify({'message': '已驳回', 'review_note': review_note})
    
    db.close()
    return jsonify({'error': '无效的操作'}), 400


# ─── Points ────────────────────────────────────────────────────
@app.route('/api/points/log', methods=['GET'])
@token_required
def get_points_log():
    user_id = request.current_user['user_id']
    db = get_db()
    logs = db.execute('SELECT * FROM points_log WHERE user_id=? ORDER BY created_at DESC LIMIT 100', (user_id,)).fetchall()
    db.close()
    return jsonify([dict(r) for r in logs])


# ─── Member ────────────────────────────────────────────────────
@app.route('/api/member/status', methods=['GET'])
@token_required
def member_status():
    return jsonify(get_member_status(request.current_user['user_id']))


@app.route('/api/member/apply', methods=['POST'])
@token_required
def member_apply():
    data = get_json_body()
    action = data.get('action')  # 'upgrade' or 'renewal'
    user_id = request.current_user['user_id']
    db = get_db()
    status = get_member_status(user_id)
    
    if action == 'upgrade':
        if status['is_member']:
            db.close()
            return jsonify({'message': '您已经是会员', 'is_member': True})
        settings = db.execute('SELECT * FROM member_settings WHERE id=1').fetchone()
        days = settings['free_duration_days'] if settings else 365
        fee = settings['annual_fee'] if settings else 199.0
        # Simulate payment
        end_date = 'datetime("now", "+{} days")'.format(days)
        db.execute('INSERT OR REPLACE INTO members (user_id, type, status, start_date, end_date) VALUES (?, "regular", "active", datetime("now"), {})'.format(end_date), (user_id,))
        db.commit()
        db.close()
        return jsonify({'message': '会员开通成功！有效期{}天'.format(days), 'days': days, 'fee': fee})
    
    elif action == 'renewal':
        if status['approved_uploads'] < 10:
            db.close()
            return jsonify({'error': '需要至少10个通过审核的上传内容才能申请贡献者会员'}), 400
        existing = db.execute(
            'SELECT id FROM member_applications WHERE user_id=? AND status="pending"',
            (user_id,)).fetchone()
        if existing:
            db.close()
            return jsonify({'message': '已提交过申请，等待审核'})
        db.execute(
            'INSERT INTO member_applications (user_id, type, status) VALUES (?, "contributor_renewal", "pending")',
            (user_id,))
        db.commit()
        db.close()
        return jsonify({'message': '申请已提交，等待管理员审核'})
    
    db.close()
    return jsonify({'error': '无效操作'}), 400


# ─── Admin: Member ─────────────────────────────────────────────
@app.route('/api/admin/member/settings', methods=['GET', 'POST'])
@admin_required
def admin_member_settings():
    if request.method == 'POST':
        data = get_json_body()
        fee = data.get('annual_fee')
        days = data.get('free_duration_days')
        db = get_db()
        if fee is not None:
            db.execute('UPDATE member_settings SET annual_fee=?, updated_at=datetime("now") WHERE id=1', (float(fee),))
        if days is not None:
            db.execute('UPDATE member_settings SET free_duration_days=?, updated_at=datetime("now") WHERE id=1', (int(days),))
        db.commit()
        db.close()
        return jsonify({'message': '会员设置已更新'})
    db = get_db()
    settings = db.execute('SELECT * FROM member_settings WHERE id=1').fetchone()
    db.close()
    return jsonify(dict(settings) if settings else {'annual_fee': 199.0, 'free_duration_days': 365})


@app.route('/api/admin/member/list', methods=['GET'])
@admin_required
def admin_member_list():
    db = get_db()
    members = db.execute('''
        SELECT m.*, u.username, u.phone
        FROM members m JOIN users u ON m.user_id=u.id
        ORDER BY m.created_at DESC LIMIT 100
    ''').fetchall()
    db.close()
    return jsonify([dict(r) for r in members])


@app.route('/api/admin/member/add', methods=['POST'])
@admin_required
def admin_member_add():
    data = get_json_body()
    user_id = to_int(data.get('user_id'))
    mem_type = data.get('type', 'regular')
    days = to_int(data.get('days', 365))
    db = get_db()
    user = db.execute('SELECT id FROM users WHERE id=?', (user_id,)).fetchone()
    if not user:
        db.close()
        return jsonify({'error': '用户不存在'}), 404
    db.execute(
        'INSERT OR REPLACE INTO members (user_id, type, status, start_date, end_date) VALUES (?, ?, "active", datetime("now"), datetime("now", "+{} days"))'.format(days),
        (user_id, mem_type))
    db.commit()
    db.close()
    return jsonify({'message': '已添加会员', 'user_id': user_id, 'type': mem_type, 'days': days})


@app.route('/api/admin/member/applications', methods=['GET', 'POST'])
@admin_required
def admin_member_applications():
    if request.method == 'POST':
        data = get_json_body()
        app_id = to_int(data.get('application_id'))
        action = data.get('action')
        note = data.get('review_note', '')
        reviewer_id = request.current_user['user_id']
        db = get_db()
        app = db.execute('SELECT * FROM member_applications WHERE id=?', (app_id,)).fetchone()
        if not app:
            db.close()
            return jsonify({'error': '申请不存在'}), 404
        if app['status'] != 'pending':
            db.close()
            return jsonify({'error': '该申请已处理'}), 400
        if action == 'approve':
            settings = db.execute('SELECT * FROM member_settings WHERE id=1').fetchone()
            days = settings['free_duration_days'] if settings else 365
            db.execute(
                'INSERT OR REPLACE INTO members (user_id, type, status, start_date, end_date) VALUES (?, "contributor", "active", datetime("now"), datetime("now", "+{} days"))'.format(days),
                (app['user_id'],))
            db.execute('UPDATE member_applications SET status="approved", review_note=?, reviewer_id=?, reviewed_at=datetime("now") WHERE id=?',
                       (note, reviewer_id, app_id))
            db.commit()
            db.close()
            return jsonify({'message': '申请通过，贡献者会员已开通', 'days': days})
        elif action == 'reject':
            db.execute('UPDATE member_applications SET status="rejected", review_note=?, reviewer_id=?, reviewed_at=datetime("now") WHERE id=?',
                       (note, reviewer_id, app_id))
            db.commit()
            db.close()
            return jsonify({'message': '申请已驳回', 'review_note': note})
        db.close()
        return jsonify({'error': '无效操作'}), 400
    db = get_db()
    apps = db.execute('''
        SELECT a.*, u.username, u.phone
        FROM member_applications a JOIN users u ON a.user_id=u.id
        ORDER BY a.created_at DESC LIMIT 50
    ''').fetchall()
    db.close()
    return jsonify([dict(r) for r in apps])



# --- Admin: AI Settings ---
@app.route("/api/admin/ai/settings", methods=["GET", "POST"])
@admin_required
def admin_ai_settings():
    if request.method == "POST":
        data = get_json_body()
        db = get_db()
        for k in ("api_key", "model", "api_url"):
            v = data.get(k)
            if v is not None:
                db.execute('UPDATE ai_settings SET ' + k + '=? WHERE id=1', (v,))
        v = data.get('auto_approve')
        if v is not None:
            db.execute('UPDATE ai_settings SET auto_approve=? WHERE id=1', (1 if v else 0,))
        db.execute("UPDATE ai_settings SET updated_at=datetime('now') WHERE id=1")
        db.commit()
        db.close()
        return jsonify({"message": "AI设置已更新"})
    db = get_db()
    s = db.execute("SELECT * FROM ai_settings WHERE id=1").fetchone()
    db.close()
    if not s:
        return jsonify({"api_key": "", "model": "deepseek-chat", "api_url": "https://api.deepseek.com/v1/chat/completions", "auto_approve": 1})
    return jsonify(dict(s))
# ─── Init & Run ────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    seed_data()
    print('=' * 50)
    print('  中医智慧平台 v2.0')
    print('  启动地址: http://127.0.0.1:5000')
    print('  管理员: 13800000000 / admin123')
    print('=' * 50)
    app.run(host='127.0.0.1', port=5000, debug=False)
