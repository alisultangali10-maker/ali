import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-kazakhstan-key-2026'

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'news_kz.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        'app',
        'static',
        'images',
        'uploads'
    )

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024