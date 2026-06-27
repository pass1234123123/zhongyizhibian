#!/usr/bin/env python
"""Regenerate the frontend: clean script tag, inject fresh JS."""
import os, re

base = os.path.dirname(__file__)
html_path = os.path.join(base, 'templates', 'index.html')

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Find the script tag boundaries
script_start = html.find('<script>')
script_end = html.find('</script>', script_start)

if script_start < 0 or script_end < 0:
    print('ERROR: script tags not found')
    exit(1)

# Read the new JS from a fresh file
js_path = os.path.join(base, 'templates', 'app.js')
with open(js_path, 'r', encoding='utf-8') as f:
    new_js = f.read()

# Replace everything between <script> and </script> with clean JS
new_script_content = '''
// 中医智慧平台 - App
var API = '';
var token = localStorage.getItem('token') || '';
var user = JSON.parse(localStorage.getItem('user') || 'null');
var currentTreatmentId = null;
var fbRating = 5;
var fbEfficacy = 'effective';

document.addEventListener('DOMContentLoaded', function() {
    renderProfile();
    loadHome();
});
''' + new_js

html = html[:script_start+8] + new_script_content + html[script_end:]

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'OK - {len(html)} bytes written')

# Verify no duplicate function definitions
import re
funcs = re.findall(r'(?:async\s+)?function\s+(\w+)', html)
from collections import Counter
dupes = [(f,c) for f,c in Counter(funcs).items() if c > 1]
if dupes:
    print(f'WARNING: duplicates found: {dupes[:5]}')
else:
    print('No duplicates - clean!')
print(f'Total functions: {len(set(funcs))}')
