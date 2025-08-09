# 项目配置说明 (pyproject.toml)

## 1. 项目基本信息
```toml
[project]
name = "catalogue"  # 项目名称
version = "0.1.0"   # 项目版本
requires-python = ">=3.9,<4.0"  # Python版本要求
```

## 2. 主要依赖说明

### 核心依赖
- `fastapi`: Web框架
- `uvicorn`: ASGI服务器
- `sqlalchemy`: ORM工具
- `psycopg2-binary`: PostgreSQL驱动
- `motor`: MongoDB异步驱动
- `redis`: Redis客户端

### 安全相关
- `bcrypt`: 密码哈希
- `cryptography`: 加密库
- `pyjwt`: JWT实现

## 3. 脚本入口
```toml
[project.scripts]
start = "scripts.start:main"  # 启动应用
initdb = "scripts.initdb:main"  # 初始化数据库
```

## 4. 开发依赖
- `pytest`: 测试框架
- `pytest-asyncio`: 异步测试支持
- `mypy`: 静态类型检查
- `black`: 代码格式化

## 5. 构建配置
```toml
[build-system]
requires = ["poetry-core>=2.0.0"]  # 构建工具要求
build-backend = "poetry.core.masonry.api"
```

## 6. 版本管理策略
- 主版本: 手动升级
- 次版本: 半自动升级
- 补丁版本: 自动升级
