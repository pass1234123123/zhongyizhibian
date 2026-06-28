import os, tarfile
pkgs = ['flask','flask_cors','werkzeug','jinja2','markupsafe','itsdangerous','click','blinker']
base = 'C:/Users/Administrator/AppData/Local/hermes/hermes-agent/venv/Lib/site-packages'
tar = tarfile.open('packages.tar.gz', 'w:gz')
for pkg in pkgs:
    for item in [pkg, pkg.replace('-','_')]:
        path = os.path.join(base, item)
        if os.path.exists(path):
            tar.add(path, arcname=item)
            print('Added', item)
            break
    for f in os.listdir(base):
        if f.startswith(pkg.replace('-','_')) and f.endswith('.dist-info'):
            tar.add(os.path.join(base, f), arcname=f)
            print('Added', f)
            break
tar.close()
print('Created packages.tar.gz', os.path.getsize('packages.tar.gz'), 'bytes')
