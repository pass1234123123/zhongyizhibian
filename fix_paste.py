#!/usr/bin/env python
"""Add submit button to upload paste area."""
import os

path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
with open(path, 'r', encoding='utf-8') as f:
    h = f.read()

# Find pasteArea textarea and add submit button
paste_end = h.find('</textarea>')
if paste_end > 0:
    nearby = h[paste_end:paste_end+300]
    if 'submitPaste' not in nearby:
        btn = '<div style="text-align:center;margin:8px 0"><button class="pay-btn sm" onclick="submitPaste()" style="background:#8B3A3A;color:#fff;padding:8px 24px">📤 提交文字内容</button></div>'
        h = h[:paste_end+12] + btn + h[paste_end+12:]
        print('Submit button added')
    else:
        print('Submit button already present')
else:
    print('Paste area not found')

with open(path, 'w', encoding='utf-8') as f:
    f.write(h)
print('Done')
