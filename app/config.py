
import os
from dotenv import load_dotenv
from pathlib import Path
from .constants import CatConstants, AppConstants

class Config:
    def __init__(self):
        self._load_env()
        
    def _load_env(self):
        """加载环境变量"""
        env_path = Path(__file__).parent.parent / '.env'
        load_dotenv(env_path)
        
    @property
    def APP_PORT(self):
        """应用端口配置"""
        return int(os.getenv('APP_PORT', '5000'))
        
    @property
    def SECRET_KEY(self):
        return os.getenv('SECRET_KEY', 'dev-key')
        
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return os.getenv('DATABASE_URL', f'sqlite:///{Path(__file__).parent.parent}/app.db')
        
    @property
    def UPLOAD_FOLDER(self):
        return os.getenv('UPLOAD_FOLDER', str(Path(__file__).parent.parent / 'static/uploads'))
        
    @property 
    def ITEMS_PER_PAGE(self):
        return int(os.getenv('ITEMS_PER_PAGE', str(CatConstants.DEFAULT_ITEMS_PER_PAGE)))
        
    @property
    def FLASK_ENV(self):
        return os.getenv('FLASK_ENV', 'development')
        
    @property
    def FLASK_DEBUG(self):
        return os.getenv('FLASK_DEBUG', '1') == '1'
        
    @property
    def CACHE_TYPE(self):
        return os.getenv('CACHE_TYPE', 'SimpleCache')
        
    @property
    def RATELIMIT_STORAGE_URL(self):
        return os.getenv('RATELIMIT_STORAGE_URL', 'memory://')


class TestingConfig(Config):
    @property
    def TESTING(self):
        return True
        
    @property
    def APP_PORT(self):
        """测试环境端口"""
        return 5001
        
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return 'sqlite:///:memory:'
        
    @property
    def SQLALCHEMY_TRACK_MODIFICATIONS(self):
        return False
        
    @property
    def CACHE_TYPE(self):
        return 'NullCache'
