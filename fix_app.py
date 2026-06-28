import re, json

with open('/home/ubuntu/zhongyizhiban/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_ai = '''

@app.route('/api/admin/ai/settings', methods=['GET', 'POST'])
@admin_required
def admin_ai_settings():
    if request.method == 'POST':
        data = get_json_body()
        db = get_db()
        for k in ('api_key', 'model', 'api_url'):
            v = data.get(k)
            if v is not None:
                db.execute('UPDATE ai_settings SET ' + k + '=? WHERE id=1', (v,))
        v = data.get('auto_approve')
        if v is not None:
            db.execute('UPDATE ai_settings SET auto_approve=? WHERE id=1', (1 if v else 0,))
        db.execute("UPDATE ai_settings SET updated_at=datetime('now') WHERE id=1")
        db.commit()
        db.close()
        return jsonify({'message': '\u4eba\u5de5\u667a\u80fd\u8bbe\u7f6e\u5df2\u66f4\u65b0'})
    db = get_db()
    s = db.execute('SELECT * FROM ai_settings WHERE id=1').fetchone()
    db.close()
    if not s:
        return jsonify({'api_key': '', 'model': 'deepseek-chat', 'api_url': 'https://api.deepseek.com/v1/chat/completions', 'auto_approve': 1})
    return jsonify(dict(s))
'''

content = content.replace('# --- Init & Run ---', new_ai + '\n# --- Init & Run ---')

old_sim = '''    # Simulate AI processing
    ai_result = json.dumps({
        'title': '\u4e0a\u4f20\u5185\u5bb9\uff08AI\u81ea\u52a8\u63d0\u53d6\uff09',
        'disease_ids': [],
        'types': [],
        'preview': content[:100] if content else '\u6587\u4ef6\u5185\u5bb9\uff08AI\u63d0\u53d6\u4e2d\uff09',
        'saved_files': saved_files
    }, ensure_ascii=False)
    db.execute('UPDATE uploads SET ai_result=?, status="pending" WHERE id=?', (ai_result, upload_id))'''

new_ai_upload = '''    # AI processing (use DeepSeek if configured)
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
                return jsonify({'message': '\u4e0a\u4f20\u6210\u529f\uff0cAI\u5df2\u81ea\u52a8\u5904\u7406\u5e76\u5165\u5e93\uff01', 'upload_id': upload_id, 'status': new_status, 'auto_approved': bool(settings.get('auto_approve', 1))})
        except Exception as ex:
            pass
    ai_result = json.dumps({
        'title': '\u4e0a\u4f20\u5185\u5bb9\uff08AI\u81ea\u52a8\u63d0\u53d6\uff09',
        'disease_ids': [],
        'types': [],
        'preview': content[:100] if content else '\u6587\u4ef6\u5185\u5bb9\uff08AI\u63d0\u53d6\u4e2d\uff09',
        'saved_files': saved_files
    }, ensure_ascii=False)
    db.execute('UPDATE uploads SET ai_result=?, status="pending" WHERE id=?', (ai_result, upload_id))'''

content = content.replace(old_sim, new_ai_upload)

with open('/home/ubuntu/zhongyizhiban/app.py', 'w', encoding='utf-8') as f:
    f.write(content)

compile(content, 'app.py', 'exec')
print('OK')
