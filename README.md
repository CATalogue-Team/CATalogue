
# CATalogue - 专业猫咪信息管理系统

## 📌 核心价值
为动物救助机构提供高效的猫咪信息管理解决方案，包含：
- 完整的猫咪信息生命周期管理
- 多角色协作工作流
- 数据安全与权限控制
- 响应式管理界面

## 🛠️ 功能特性

### 用户系统
- 多角色认证（管理员/普通用户）
- 注册审批流程
- 密码加密存储（PBKDF2+SHA256）
- 会话管理与活动日志

### 猫咪管理
- 完整档案管理（基本信息+多图上传）
- 领养状态跟踪（待领养/已领养）
- 高级搜索与筛选
- 批量导入/导出

### 后台管理
- 基于角色的访问控制
- 数据审核与版本记录
- 系统监控仪表盘
- 自动化数据备份

## 🚀 快速入门

### 环境准备
```bash
# 克隆仓库
git clone https://github.com/your-repo/CATalogue.git
cd CATalogue

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 安装依赖
```bash
pip install -r requirements.txt
```

## 🗄️ 数据库初始化

### 1. 常规迁移方式 (推荐开发使用)
```bash
# 初始化迁移仓库
flask db init

# 生成迁移脚本
flask db migrate -m "Initial migration"

# 应用迁移
flask db upgrade

# 创建管理员 (CLI命令)
flask create-admin <username> <password>
# 示例:
flask create-admin admin securePassword123!

# 密码要求:
# - 至少8个字符
# - 包含大小写字母和数字
# - 不能与用户名相同
```

### 2. 使用初始化脚本 (首次部署/重置数据)
```bash
# 执行初始化脚本(会创建表、管理员账号和示例数据)
python init_db.py

# 参数说明
# -- 自动创建数据库表
# -- 创建默认管理员(admin/admin123)
# -- 生成5只示例猫咪数据
# -- 每只猫关联3张示例图片
```

### 环境差异
| 场景         | 开发环境                      | 生产环境                     |
|--------------|-----------------------------|----------------------------|
| 推荐方式      | 常规迁移 或 init_db.py       | 仅使用常规迁移               |
| 数据保留      | 可随意重置                   | 必须备份后操作               |
| 适用场景      | 开发测试                     | 正式部署                    |

### 注意事项
1. **init_db.py会清空现有数据**，生产环境慎用
2. 示例图片存储在`static/uploads/`
3. 管理员账号自动创建: admin/admin123
4. 使用前请确保:
```bash
pip install -r requirements.txt
```

### 启动服务
```bash
# 开发模式
flask run --debug

# 生产模式
gunicorn -w 4 --bind 0.0.0.0:8000 "run:app"
```

## ⚙️ 配置指南

### 关键配置项
| 配置项 | 说明 | 示例值 |
|--------|------|--------|
| `DATABASE_URL` | 数据库连接 | `sqlite:///instance/cats.db` |
| `UPLOAD_FOLDER` | 文件上传路径 | `./static/uploads` |
| `MAX_IMAGE_SIZE` | 图片大小限制 | `5242880` (5MB) |

### 生产环境建议
```ini
# .env 文件示例
FLASK_ENV=production
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost/prod_db
```

## 📚 开发者文档

### 项目结构
```
.
├── app/              # 核心模块
│   ├── routes/       # 路由控制器
│   ├── services/     # 业务逻辑
│   ├── models/       # 数据模型
│   └── static/       # 静态资源
├── tests/            # 单元测试
└── docs/            # 项目文档
```

### API速查表
| 端点 | 方法 | 描述 | 权限 |
|------|------|------|------|
| `/cats` | GET | 猫咪列表 | 公开 |
| `/cats` | POST | 创建记录 | 管理员 |
| `/cats/<id>` | PUT | 更新记录 | 所有者 |

## 🤝 参与贡献
1. Fork项目仓库
2. 创建特性分支 (`git checkout -b feature/xxx`)
3. 提交修改 (`git commit -am 'Add some feature'`)
4. 推送分支 (`git push origin feature/xxx`)
5. 新建Pull Request

## 📜 开源协议
MIT License © 2023 CATalogue Team
