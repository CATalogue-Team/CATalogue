from flask_sqlalchemy import SQLAlchemy
from .base import Base

# 创建独立的数据库实例
db = SQLAlchemy(model_class=Base)
