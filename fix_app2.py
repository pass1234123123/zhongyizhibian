import py_compile

with open('/home/ubuntu/zhongyizhiban/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the Init & Run line
target = None
for i, line in enumerate(lines):
    if 'Init & Run' in line:
        target = i
        break

if target is None:
    print('ERROR: Init & Run not found')
    exit(1)

# AI settings endpoint lines to insert
ai_lines = [
    '\n',
    '# --- Admin: AI Settings ---\n',
    "@app.route('/api/admin/ai/settings', methods=['GET', 'POST'])\n",
    '@admin_required\n',
    'def admin_ai_settings():\n',
    "    if request.method == 'POST':\n",
    '        data = get_json_body()\n',
    '        db = get_db()\n',
    "        for k in ('api_key', 'model', 'api_url'):\n",
    '            v = data.get(k)\n',
    '            if v is not None:\n',
    "                db.execute('UPDATE ai_settings SET ' + k + '=? WHERE id=1', (v,))\n",
    "        v = data.get('auto_approve')\n",
    '        if v is not None:\n",
    "            db.execute('UPDATE ai_settings SET auto_approve=? WHERE id=1', (1 if v else 0,))\n",
    "        db.execute(\"UPDATE ai_settings SET updated_at=datetime('now') WHERE id=1\")\n",
    '        db.commit()\n',
    '        db.close()\n',
    "        return jsonify({'message': 'AI\\u8bbe\\u7f6e\\u5df2\\u66f4\\u65b0'})\n",
    '    db = get_db()\n',
    "    s = db.execute('SELECT * FROM ai_settings WHERE id=1').fetchone()\n",
    '    db.close()\n",
    '    if not s:\n",
    "        return jsonify({'api_key': '', 'model': 'deepseek-chat', 'api_url': 'https://api.deepseek.com/v1/chat/completions', 'auto_approve': 1})\n",
    '    return jsonify(dict(s))\n",
]

# Insert before the Init & Run line
lines = lines[:target] + ai_lines + lines[target:]

with open('/home/ubuntu/zhongyizhiban/app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

try:
    py_compile.compile('/home/ubuntu/zhongyizhiban/app.py', doraise=True)
    print('Syntax OK')
except py_compile.PyCompileError as e:
    print(f'Syntax error: {e}')

print('Done')
