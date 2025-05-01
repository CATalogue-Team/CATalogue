
# CATalogue - 专业猫咪信息管理系统

## 项目概述
基于Flask的现代化猫咪信息管理平台，采用模块化架构设计，具有以下特点：
- **多用户协作**：支持管理员和普通用户分级权限管理
- **全生命周期管理**：完整的猫咪信息CRUD操作流程
- **企业级安全**：CSRF防护、密码哈希、防SQL注入
- **高性能设计**：响应速度<500ms，支持100+并发

## 系统架构
### 技术规格
| 组件         | 技术选型               | 版本要求   | 关键特性                     |
|--------------|-----------------------|-----------|----------------------------|
| Web框架      | Flask                | 2.0+      | 轻量级、扩展性强             |
| 数据库ORM    | SQLAlchemy           | 2.0+      | 类型安全、连接池管理         |
| 前端框架     | Bootstrap            | 5.x       | 响应式设计、移动端适配       |
| 认证系统     | Flask-Login          | 0.6+      | 会话管理、记住我功能         |
| 表单处理     | WTForms              | 3.0+      | CSRF保护、字段验证           |

### 架构图
```
[客户端] ←HTTP→ [Flask应用层] ←→ [业务逻辑层] ←→ [数据访问层] ←→ [SQLite数据库]
                    ↑                     ↑
                    │                     │
                [认证授权]           [缓存管理]
```

## 核心功能
### 用户管理系统
- **多角色认证**：
  - 管理员：完整系统权限
  - 普通用户：受限操作权限
- **审批流程**：
  - 新用户注册需管理员审核
  - 审批记录可追溯
- **安全机制**：
  - bcrypt密码哈希
  - 会话超时控制
  - 操作日志审计

### 猫咪信息管理
- **信息管理**：
  - 上传猫咪基本信息+多张图片
  - 支持富文本描述
  - 信息版本控制
- **智能搜索**：
  - 关键词高亮
  - 搜索结果缓存
  - 分页加载优化
- **数据分析**：
  - 品种分布统计
  - 领养率分析
  - 数据导出功能

## 快速开始
### 开发环境
```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 初始化数据库
flask db init
flask db migrate -m "initial migration"
flask db upgrade

# 5. 创建管理员
flask create-admin admin@example.com yourpassword

# 6. 启动服务
flask run --debug
```

### 生产部署
```bash
# 使用Gunicorn+反向代理
gunicorn -w 4 --bind 0.0.0.0:8000 "run:app"

# 推荐配置
export FLASK_ENV=production
export SECRET_KEY=$(openssl rand -hex 32)
export DATABASE_URL=postgresql://user:pass@localhost/catalogue
```

## 项目结构
```
.
├── app/                # 应用主模块
│   ├── routes/         # 路由控制器
│   ├── static/         # 静态资源
│   ├── __init__.py     # 应用工厂
│   ├── config.py       # 配置管理
│   └── forms.py        # 表单定义
├── core/               # 核心业务模型
│   └── models.py       # 数据模型
├── extensions/         # 扩展模块
│   └── __init__.py     # 扩展初始化
├── static/             # 全局静态资源
│   ├── css/            # 样式表
│   └── uploads/        # 上传文件(自动压缩)
├── templates/          # 前端模板(Jinja2)
├── instance/           # 实例配置
├── tests/              # 单元测试
├── .env.example        # 环境变量示例
├── requirements.txt    # 依赖清单
└── run.py              # 启动脚本
```

## 扩展阅读
- [API文档](docs/api.md)
- [开发规范](docs/development.md)
- [测试指南](docs/testing.md)
- [部署手册](docs/deployment.md)
