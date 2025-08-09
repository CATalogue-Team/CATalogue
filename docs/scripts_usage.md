# 脚本使用指南

## 1. initdb.py

### 功能
- 初始化PostgreSQL数据目录
- 创建catalogue数据库
- 执行数据库迁移
- 创建超级管理员

### 使用方法
```bash
poetry run initdb
```

### 参数
无参数，自动检测并执行必要操作

## 2. 脚本依赖
- 需要安装PostgreSQL并配置PATH
- 需要Python 3.9+环境
- 需要项目依赖已安装(poetry install)

## 3. 日志文件
- postgres.log: PostgreSQL服务日志
- uvicorn.log: FastAPI应用日志(需额外配置)

## 4. 环境变量
- DATABASE_URL: 数据库连接字符串
- APP_ENV: 应用环境(development/production)
