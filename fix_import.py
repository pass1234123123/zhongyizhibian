import os
c = open('app.py', 'r', encoding='utf-8').read()
c = c.replace('from models import get_db, init_db, seed_data',
    'from models import get_db, init_db, seed_data\nfrom ai_processor import extract_text_from_file, call_deepseek, process_and_insert')
open('app.py', 'w', encoding='utf-8').write(c)
print('import added')
