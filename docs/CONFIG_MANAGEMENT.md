# 配置管理指南

## 1. 环境变量配置
```bash
# 开发环境
FLASK_ENV=development
APP_PORT=5000
DATABASE_URL=sqlite:///dev.db

# 生产环境
FLASK_ENV=production
APP_PORT=80
DATABASE_URL=postgresql://user:pass@localhost/prod
```

## 2. 多环境配置
```python
# config.py
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    UPLOAD_FOLDER = 'uploads'
    
class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
```

## 3. 敏感信息管理
- 使用.env文件存储敏感信息
- 添加到.gitignore
- 通过python-dotenv加载

## 4. 配置验证
```python
# 启动时验证必要配置
required_keys = ['SECRET_KEY', 'DATABASE_URL']
missing = [k for k in required_keys if not app.config.get(k)]
if missing:
    raise RuntimeError(f"缺少必要配置: {missing}")
