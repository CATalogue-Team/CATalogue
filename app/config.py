from os import path, environ
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = environ.get('SECRET_KEY') or 'dev-key'
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL') or \
        'sqlite:///' + path.join(path.dirname(__file__), 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = path.join(path.dirname(__file__), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    FLASK_ENV = environ.get('FLASK_ENV') or 'development'
    SERVER_NAME = environ.get('SERVER_NAME')
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    WTF_CSRF_ENABLED = False
    JWT_SECRET_KEY = 'test-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = False

class ProductionConfig(Config):
    ENV = 'production'
    DEBUG = False
    TESTING = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 3600
    }
    TEMPLATES_AUTO_RELOAD = False
    PROPAGATE_EXCEPTIONS = True

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
