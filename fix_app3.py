import py_compile, os

f = open('/home/ubuntu/zhongyizhiban/app.py', 'r', encoding='utf-8')
content_lines = f.read().split('\n')
f.close()

target = [i for i, l in enumerate(content_lines) if 'Init & Run' in l][0]

new_code = [
    '',
    '# --- Admin: AI Settings ---',
    '@app.route("/api/admin/ai/settings", methods=["GET", "POST"])',
    '@admin_required',
    'def admin_ai_settings():',
    '    if request.method == "POST":',
    '        data = get_json_body()',
    '        db = get_db()',
    '        for k in ("api_key", "model", "api_url"):',
    '            v = data.get(k)',
    '            if v is not None:',
    "                db.execute('UPDATE ai_settings SET ' + k + '=? WHERE id=1', (v,))",
    "        v = data.get('auto_approve')",
    '        if v is not None:',
    "            db.execute('UPDATE ai_settings SET auto_approve=? WHERE id=1', (1 if v else 0,))",
    "        db.execute(\"UPDATE ai_settings SET updated_at=datetime('now') WHERE id=1\")",
    '        db.commit()',
    '        db.close()',
    '        return jsonify({"message": "AI\u8bbe\u7f6e\u5df2\u66f4\u65b0"})',
    '    db = get_db()',
    '    s = db.execute("SELECT * FROM ai_settings WHERE id=1").fetchone()',
    '    db.close()',
    '    if not s:',
    '        return jsonify({"api_key": "", "model": "deepseek-chat", "api_url": "https://api.deepseek.com/v1/chat/completions", "auto_approve": 1})',
    '    return jsonify(dict(s))',
]

content_lines = content_lines[:target] + new_code + content_lines[target:]

f = open('/home/ubuntu/zhongyizhiban/app.py', 'w', encoding='utf-8')
f.write('\n'.join(content_lines))
f.close()

py_compile.compile('/home/ubuntu/zhongyizhiban/app.py', doraise=True)
print('OK')
