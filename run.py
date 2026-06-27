import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, init_db, seed_data

if __name__ == '__main__':
    init_db()
    seed_data()
    print('=' * 50)
    print('  中医智慧平台 v2.0')
    print('  启动地址: http://127.0.0.1:5000')
    print('  管理员: 13800000000 / admin123')
    print('=' * 50)
    app.run(host='127.0.0.1', port=5000, debug=False)
