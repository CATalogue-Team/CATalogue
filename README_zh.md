
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
- 系统监控仪表盘 (Prometheus指标端点`/metrics`)
- 请求日志与性能监控
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
# 基本初始化(使用默认管理员账号)
python init_db.py

# 自定义管理员账号
python init_db.py --username myadmin --password MySecurePass123

# 跳过示例数据初始化
python init_db.py --skip-samples

# 参数说明:
# --username: 管理员用户名(默认:admin)
# --password: 管理员密码(默认:admin123)
# --skip-samples: 跳过示例数据初始化
```

## 📜 日志管理

### 查看日志
```bash
# 查看日志文件列表
curl -H "Authorization: Bearer <token>" http://localhost:5000/admin/logs

# 查看具体日志文件内容
curl -H "Authorization: Bearer <token>" http://localhost:5000/admin/logs/app.log
```

### 动态调整日志级别
```bash
# 设置日志级别(DEBUG/INFO/WARNING/ERROR/CRITICAL)
curl -X PUT -H "Content-Type: application/json" \
     -H "Authorization: Bearer <token>" \
     -d '{"level":"DEBUG"}' \
     http://localhost:5000/admin/logs/level
```

### 日志配置
```ini
# .env 日志相关配置
LOG_LEVEL=INFO  # 日志级别
LOG_FILE=logs/app.log  # 日志文件路径
LOG_FORMAT='%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # 日志格式
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

## 🖼️ 界面截图

![首页](static/screenshots/home.png)
![猫咪详情](static/screenshots/cat_detail.png)
![管理后台](static/screenshots/admin.png)

##  开发者文档

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

### API详细说明

#### 猫咪管理接口

**1. 获取猫咪列表**
```
GET /cats
```
参数：
- `page` - 页码(默认1)
- `per_page` - 每页数量(默认10)
- `breed` - 按品种筛选
- `is_adopted` - 按领养状态筛选(true/false)

示例请求：
```bash
curl "http://localhost:5000/cats?page=2&breed=波斯猫"
```

响应示例：
```json
{
  "items": [
    {
      "id": 1,
      "name": "小白",
      "breed": "波斯猫",
      "age": 2,
      "is_adopted": false
    }
  ],
  "total": 15,
  "page": 2,
  "per_page": 10
}
```

**2. 创建猫咪记录**
```
POST /cats
```
请求头：
- `Content-Type: application/json`
- `Authorization: Bearer <token>`

请求体：
```json
{
  "name": "新猫咪",
  "breed": "英短",
  "age": 1,
  "description": "活泼可爱"
}
```

**3. 更新猫咪信息**
```
PUT /cats/<id>
```
参数：
- `id` - 猫咪ID(路径参数)

请求体：
```json
{
  "age": 2,
  "is_adopted": true
}
```

#### 系统监控接口

**获取监控指标**
```
GET /metrics
```
响应格式：
```
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="cats",status="200"} 42
```

#### 通用响应状态码
| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 参数错误 |
| 401 | 未授权 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |

### 测试指南
```bash
# 运行单元测试
pytest tests/

# 生成测试覆盖率报告
pytest --cov=app tests/

# 测试监控端点
curl http://localhost:5000/metrics
```

## ❓ 常见问题

### Q: 如何重置管理员密码？
```bash
flask reset-password <username> <new_password>
```

### Q: 上传图片失败怎么办？
1. 检查`static/uploads`目录权限
2. 确认图片大小不超过配置的`MAX_IMAGE_SIZE`
3. 检查文件扩展名是否允许(jpg/png/gif)

### Q: 如何备份数据库？
```bash
# SQLite
cp instance/cats.db instance/backup_$(date +%Y%m%d).db

# PostgreSQL
pg_dump -U username -d dbname > backup_$(date +%Y%m%d).sql
```

## 🤝 参与贡献
1. Fork项目仓库
2. 创建特性分支 (`git checkout -b feature/xxx`)
3. 提交修改 (`git commit -am 'Add some feature'`)
4. 推送分支 (`git push origin feature/xxx`)
5. 新建Pull Request

## 📜 开源协议
MIT License © 2023 CATalogue Team
