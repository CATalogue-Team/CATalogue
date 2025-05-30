# CATalogue 配置管理规范

## 1. 配置分类

### 敏感配置
- 数据库连接信息
- API密钥
- 加密密钥
- 存储位置: `.env`文件(不提交到版本控制)

### 业务配置
- 分页大小
- 上传限制
- 缓存时间
- 存储位置: `app/constants.py`

### 环境配置
- 运行环境(dev/test/prod)
- 调试模式
- 日志级别
- 存储位置: `app/config.py`

## 2. 环境变量管理

### .env文件示例
```ini
# 数据库配置
DATABASE_URL=postgresql://user:pass@localhost/cats
SECRET_KEY=your-secret-key-here

# 应用配置
ITEMS_PER_PAGE=20
MAX_UPLOAD_SIZE=5242880  # 5MB
```

### 环境变量加载
```python
# app/__init__.py
from dotenv import load_dotenv
load_dotenv()  # 从.env文件加载
```

## 3. 配置访问规范

### 通过配置类访问
```python
# app/core/config.py
class Config:
    @property
    def db_url(self):
        return os.getenv('DATABASE_URL')
```

### 禁止直接访问
```python
# 错误做法
db_url = os.getenv('DATABASE_URL')

# 正确做法
config = Config()
db_url = config.db_url
```

## 4. 安全注意事项

1. 永远不要将`.env`文件提交到版本控制
2. 生产环境使用实际环境变量而非文件
3. 敏感配置必须加密存储
4. 配置变更需同步更新文档
5. 不同环境使用不同配置

## 5. 配置验证

```python
# 添加配置验证
def validate_config():
    required_keys = ['DATABASE_URL', 'SECRET_KEY']
    for key in required_keys:
        if not os.getenv(key):
            raise ValueError(f'缺少必要配置: {key}')
