import os
from dotenv import load_dotenv
from pathlib import Path

class Config:
    def __init__(self):
        self.load_env()
        
    def load_env(self):
        env_path = Path(__file__).parent.parent / '.env'
        load_dotenv(env_path)
        
    @property
    def items_per_page(self):
        return int(os.getenv('ITEMS_PER_PAGE', '10'))
        
    @property 
    def upload_folder(self):
        return os.getenv('UPLOAD_FOLDER', 'static/uploads')

    @property
    def database_uri(self):
        return os.getenv('DATABASE_URI', 'sqlite:///instance/catalogue.db')

    @property
    def secret_key(self):
        return os.getenv('SECRET_KEY', 'dev-secret-key')

    @property
    def debug(self):
        return os.getenv('DEBUG', 'False').lower() == 'true'

    @property
    def testing(self):
        return os.getenv('TESTING', 'False').lower() == 'true'
