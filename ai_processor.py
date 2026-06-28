import json, os, traceback

def extract_text_from_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.txt':
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    elif ext == '.docx':
        try:
            from docx import Document
            return chr(10).join([p.text for p in Document(filepath).paragraphs])
        except ImportError:
            return None
    elif ext == '.pdf':
        try:
            import pdfplumber
            with pdfplumber.open(filepath) as pdf:
                return chr(10).join([p.extract_text() or '' for p in pdf.pages])
        except ImportError:
            return None
    return None

def call_deepseek(content, api_key, model='deepseek-chat', api_url=None):
    if not api_key:
        return {'error': 'API key not configured', 'need_config': True}
    try:
        import requests
        headers = {'Authorization': 'Bearer ' + api_key, 'Content-Type': 'application/json'}
        data = {'model': model, 'messages': [
            {'role': 'system', 'content': 'You are a TCM data assistant. Extract treatment details as JSON.'},
            {'role': 'user', 'content': 'Extract treatments from:\n' + content[:3000]}
        ], 'temperature': 0.1}
        r = requests.post(api_url or 'https://api.deepseek.com/v1/chat/completions', headers=headers, json=data, timeout=30)
        r.raise_for_status()
        ai_text = r.json()['choices'][0]['message']['content']
        bt = chr(96)
        cm = bt * 3
        if (cm + 'json') in ai_text:
            ai_text = ai_text.split(cm + 'json')[1].split(cm)[0].strip()
        elif cm in ai_text:
            ai_text = ai_text.split(cm)[1].split(cm)[0].strip()
        return json.loads(ai_text)
    except Exception as e:
        return {'error': str(e)}

def process_and_insert(db, ai_result, user_id):
    results = []
    items = ai_result.get('treatments', [ai_result] if 'title' in ai_result else [])
    for t in items:
        dn = (t.get('disease') or '').strip()
        cn = (t.get('category') or '\xe5\x86\x85\xe7\xa7\x91').strip()
        if not dn: continue
        cat = db.execute('SELECT id FROM disease_categories WHERE name=?', (cn,)).fetchone()
        if not cat:
            db.execute('INSERT INTO disease_categories (name) VALUES (?)', (cn,))
            cat = db.execute('SELECT id FROM disease_categories WHERE name=?', (cn,)).fetchone()
        dis = db.execute('SELECT id FROM diseases WHERE name=?', (dn,)).fetchone()
        if not dis:
            mx = db.execute('SELECT MAX(id) FROM diseases').fetchone()[0] or 0
            nid = max(mx + 1, cat['id'] * 100 + 1)
            db.execute('INSERT INTO diseases (id, category_id, name) VALUES (?,?,?)', (nid, cat['id'], dn))
            did = nid
        else:
            did = dis['id']
        ti = t.get('title', '').strip()
        if not ti: continue
        mx2 = db.execute('SELECT MAX(id) FROM treatments').fetchone()[0] or 0
        tid = mx2 + 1
        db.execute('INSERT INTO treatments (id, disease_id, title, preview, full_content, status, uploader_id) VALUES (?,?,?,?,?, published,?)',
            (tid, did, ti, t.get('preview',''), t.get('full_content',''), user_id))
        for tp in t.get('types', []):
            db.execute('INSERT OR IGNORE INTO treatment_types (name) VALUES (?)', (tp,))
            db.execute('INSERT OR IGNORE INTO treatment_type_relations VALUES (?,?)', (tid, tp))
        for f in t.get('formulas', []):
            db.execute('INSERT INTO treatment_formulas (treatment_id, formula_name, ingredients, usage_text, note) VALUES (?,?,?,?,?)',
                (tid, f.get('formula_name',''), f.get('ingredients',''), f.get('usage_text',''), f.get('note','')))
        for a in t.get('acupoints', []):
            db.execute('INSERT INTO treatment_acupoints (treatment_id, points, method, course) VALUES (?,?,?,?)',
                (tid, a.get('points',''), a.get('method',''), a.get('course','')))
        results.append({'id': tid, 'title': ti})
    db.commit()
    return results
