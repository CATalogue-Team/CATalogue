
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(basedir), 'instance/cats.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 300,
        'pool_pre_ping': True
    }
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300
    TEMPLATES_AUTO_RELOAD = False
    SEND_FILE_MAX_AGE_DEFAULT = 31536000
    COMPRESS_ALGORITHM = 'gzip'
    COMPRESS_LEVEL = 6
    COMPRESS_MIN_SIZE = 500
    MAX_IMAGE_SIZE = 1024 * 1024 * 5  # 5MB
    ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'png', 'jpeg', 'gif']
    UPLOAD_FOLDER = os.path.join(os.path.dirname(basedir), 'static/uploads')
