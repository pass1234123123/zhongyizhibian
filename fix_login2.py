import sys
fp = r'F:\AI\codex\zhongyizhiban\templates\admin.html'
with open(fp, 'r', encoding='utf-8-sig') as f:
    c = f.read()

# Replace just the catch block
old_catch = "}catch(e){err.textContent=e.message;err.style.display=" + chr(39) + "block" + chr(39) + ";}"
new_catch = "}catch(e){err.textContent=e.message;err.style.display=" + chr(39) + "block" + chr(39) + ";t(" + chr(39) + "\u767b\u5f55\u5931\u8d25: " + chr(39) + "+e.message);console.error(e);}"
if old_catch in c:
    c = c.replace(old_catch, new_catch)
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(c)
    print('Catch block fixed. Show toast on login error.')
else:
    print('Pattern not found')
    # Show the actual catch block
    idx = c.find('catch(e)')
    if idx >= 0:
        print(f'Found at {idx}: {c[idx:idx+100]}')
    idx2 = c.find('adminLogin')
    if idx2 >= 0:
        end = c.find(chr(10)+chr(10), idx2)
        if end < 0: end = idx2 + 800
        print(f'adminLogin found at {idx2}:')
        print(c[idx2:end])
