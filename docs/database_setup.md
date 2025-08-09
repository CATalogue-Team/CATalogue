# 数据库配置与管理指南

## 1. 数据库初始化

### 自动初始化 (推荐)
```bash
# 使用项目提供的初始化脚本
poetry run initdb
```

### 手动初始化
```bash
# 初始化PostgreSQL数据目录
initdb -D pgdata --locale=C --encoding=UTF8

# 创建catalogue数据库
createdb -h localhost -p 5432 catalogue

# 应用数据库迁移
alembic upgrade head
```

## 2. 数据库服务管理

### 启动服务
```bash

# 仅启动PostgreSQL服务
pg_ctl -D pgdata -l postgres.log start
```

### 停止服务
```bash
pg_ctl -D pgdata stop
```

## 3. 数据库维护

### 备份数据库
```bash
pg_dump -h localhost -p 5432 -U postgres -F c -b -v -f catalogue.backup catalogue
```

### 恢复数据库
```bash
pg_restore -h localhost -p 5432 -U postgres -d catalogue -v catalogue.backup
```

## 4. 常见问题

### 连接问题
- 确保PostgreSQL服务已启动
- 检查端口5432是否被占用
- 验证pg_hba.conf配置

### 性能优化
- 调整shared_buffers和work_mem参数
- 定期执行VACUUM ANALYZE
- 为常用查询创建索引
