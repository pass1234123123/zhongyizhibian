import sys, os
sys.path.insert(0, os.path.expanduser('~/.local/lib/python3.12/site-packages'))
from app import app, init_db, seed_data
init_db()
seed_data()
app.run(host='0.0.0.0', port=5000, debug=False)
