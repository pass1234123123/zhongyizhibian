import os
lines = open('templates/index.html','r',encoding='utf-8').readlines()

start = None
for i, l in enumerate(lines):
    if '管理后台' in l and 'menu-arrow' in l:
        start = i - 1
        break

if start is not None:
    del lines[start:start+4]
    
    for i, l in enumerate(lines):
        if 'text-align' in l and 'padding' in l:
            lines.insert(i+1, '      <div style="text-align:center;padding:12px 0 4px">\n')
            lines.insert(i+2, '        <a href="/admin" style="color:#C23B22;font-size:12px">管理员登录 \u2192</a>\n')
            lines.insert(i+3, '      </div>\n')
            break
    
    open('templates/index.html','w',encoding='utf-8').writelines(lines)
    print('Updated index.html')
else:
    print('Admin menu items not found')
