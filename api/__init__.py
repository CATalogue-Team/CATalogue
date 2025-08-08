import os
import sys
from .base import Base
from .models.cat import DBCat
from .models.user_model import DBUser

# 将项目根目录添加到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 确保所有模型都被加载
__all__ = ['Base', 'DBCat', 'DBUser']
