# CATalogue - 猫咪信息管理系统

## 功能特性

### 用户认证
- `/login` - 用户登录
- `/logout` - 用户登出
- `/register` - 新用户注册

### 猫咪管理
- `/` - 首页
- `/search` - 搜索猫咪
- `/cat/<id>` - 查看猫咪详情
- `/cat/upload` - 上传新猫咪 (管理员)
- `/cat/edit/<id>` - 编辑猫咪信息 (管理员)
- `/cat/delete/<id>` - 删除猫咪 (管理员)

### 后台管理
- `/admin/cats` - 管理猫咪 (管理员)
- `/admin/edit_cat/<id>` - 编辑猫咪 (管理员)
- `/admin/delete_cat/<id>` - 删除猫咪 (管理员)
- `/admin/approvals` - 审批新用户 (管理员)
- `/admin/users` - 用户管理 (管理员)

## 开发指南

### 环境配置
```bash
pip install -r requirements.txt
flask db init
flask db migrate
flask db upgrade
```

### 启动开发服务器
```bash
flask run
```

### 创建管理员账号
```bash
flask create-admin <username> <password>
```

## API端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | / | 首页 |
| GET | /search | 搜索猫咪 |
| GET | /cat/<id> | 猫咪详情 |
| GET/POST | /cat/upload | 上传猫咪 |
| GET/POST | /cat/edit/<id> | 编辑猫咪 |
| POST | /cat/delete/<id> | 删除猫咪 |
| GET | /admin/cats | 猫咪管理 |
| GET/POST | /admin/edit_cat/<id> | 编辑猫咪(后台) |
| POST | /admin/delete_cat/<id> | 删除猫咪(后台) |
| GET/POST | /admin/approvals | 用户审批 |
| GET/POST | /admin/users | 用户管理 |

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
### Favicon配置
1. 将favicon.ico文件放置在`static/`目录下
2. 确保base.html模板中包含以下代码：
```html
<link rel="icon" href="{{ url_for('static', filename='favicon.ico') }}" type="image/x-icon">
```

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
│   ├── __init__.py     # 核心模块初始化
│   └── models.py       # 数据模型定义
├── extensions/         # 扩展模块
│   └── __init__.py     # 扩展初始化
├── static/             # 全局静态资源
│   ├── css/            # 样式表
│   └── uploads/        # 上传文件(自动压缩)
├── templates/          # 前端模板(Jinja2)
├── instance/           # 实例配置
├── tests/              # 单元测试(新创建)
├── .env.example        # 环境变量示例
├── requirements.txt    # 依赖清单
└── run.py              # 启动脚本
```

## API端点参考与使用示例

### 用户认证
```http
POST /login
Content-Type: application/x-www-form-urlencoded

username=testuser&password=123456
```
响应示例：
```json
{
  "redirect": "/",
  "status": "success"
}
```

### 猫咪管理
```http
POST /cat/upload
Content-Type: multipart/form-data

name=Fluffy&description=Cute+cat&image=@cat.jpg
```
响应示例：
```json
{
  "id": 42,
  "name": "Fluffy",
  "image_url": "/static/uploads/cat.jpg"
}
```

### 完整端点列表
| 端点                | 方法 | 描述                  | 权限要求   |
|---------------------|------|-----------------------|-----------|
| /login             | POST | 用户登录              | 无        |
| /logout            | GET  | 用户登出              | 认证用户  |
| /register          | POST | 新用户注册            | 无        |

### 管理员功能
| 端点                | 方法 | 描述                  | 权限要求   |
|---------------------|------|-----------------------|-----------|
| /admin/approvals   | GET  | 待审批用户列表        | 管理员    |
| /admin/users       | GET  | 用户管理界面          | 管理员    |
| /admin/cats        | GET  | 猫咪管理列表          | 管理员    |

### 猫咪信息
| 端点                | 方法 | 描述                  | 权限要求   |
|---------------------|------|-----------------------|-----------|
| /cat/<id>          | GET  | 猫咪详情              | 认证用户  |
| /cat/upload        | POST | 上传猫咪信息          | 管理员    |
| /cat/edit/<id>     | POST | 编辑猫咪信息          | 管理员    |
| /cat/delete/<id>   | POST | 删除猫咪信息          | 管理员    |

## 架构设计与分层说明

### 系统架构图
```mermaid
graph TD
    A[客户端] --> B[路由层]
    B --> C[服务层]
    C --> D[数据访问层]
    D --> E[(数据库)]
    C --> F[模板渲染]
    B --> G[认证中间件]
    G -->|验证| H[用户服务]
```

### 分层职责
1. **路由层** (`app/routes`)
   - 处理HTTP请求/响应
   - 参数验证与转换
   - 调用服务层方法

2. **服务层** (`app/services`)
   - 封装核心业务逻辑
   - 事务管理
   - 异常处理
   - 调用数据访问层

3. **数据访问层** (`app/models`)
   - 数据库模型定义
   - 基础CRUD操作
   - 关系映射

4. **公共组件**
   - 认证中间件
   - 日志系统
   - 配置管理

## 扩展阅读
- [API文档](docs/api.md)
- [开发规范](docs/development.md)
- [测试指南](docs/testing.md)
- [部署手册](docs/deployment.md)
