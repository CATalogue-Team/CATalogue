
# CATalogue - 猫咪信息管理系统

## 项目概述
一个基于Flask的猫咪信息管理系统，支持猫咪信息的上传、编辑、搜索和展示。

## 功能特性
### 用户认证系统
- 角色区分：管理员/普通用户
- 权限控制：管理员拥有完整CRUD权限
- 安全机制：CSRF保护所有表单

### 猫咪信息管理
- 信息上传：名称(必填)、描述、图片
- 信息维护：编辑、删除(需二次确认)
- 数据展示：按时间倒序排列
- 图片处理：自动压缩优化(限制5MB)

### 智能搜索系统
- 模糊匹配：名称/描述关键词
- 智能处理：大小写不敏感、空搜索处理
- 默认展示：最新3条记录
- 响应速度：<500ms

## 技术规格
### 核心架构
- Web框架：Flask
- 前端框架：Bootstrap 5
- 数据库：SQLite + SQLAlchemy ORM
- 认证系统：Flask-Login

### 安全规范
- 防注入：参数化查询
- 上传限制：仅允许jpg/png/gif
- 数据保护：自动初始化表结构

### 扩展性设计
- 分类系统：预留字段
- 状态管理：待领养/已领养
- API设计：RESTful接口
- 多图支持：数据库结构预留

## 安装指南
1. 克隆仓库：
```bash
git clone <仓库地址>
cd CATalogue
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 初始化数据库：
```bash
flask db init
flask db migrate -m "initial migration"
flask db upgrade
```

## 运行说明
```bash
python run.py
```
访问 http://localhost:5000

## 项目结构
```
.
├── app/               # 应用核心代码
│   ├── __init__.py    # 应用工厂
│   ├── config.py      # 配置
│   ├── models.py      # 数据模型
│   ├── routes/        # 路由蓝图
│   └── ...
├── static/            # 静态文件
├── templates/         # 模板文件
├── instance/          # 实例文件夹
├── run.py             # 启动脚本
└── requirements.txt   # 依赖列表
```

## 配置说明
复制`.env.example`创建`.env`文件并配置：
```ini
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///cats.db
```

## 开发指南
1. 开发模式：
```bash
export FLASK_ENV=development
python run.py
```

2. 运行测试：
```bash
pytest
```

3. 代码规范检查：
```bash
flake8
```
