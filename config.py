import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'zhongyi.db')
SECRET_KEY = os.environ.get('JWT_SECRET', 'zhongyi-platform-secret-key-2026')
JWT_EXPIRATION_HOURS = 72
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
