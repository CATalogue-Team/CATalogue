# CATalogue API 文档 (v1)

## 快速开始
```bash
# 启动开发服务器
flask run

# 测试API端点
curl http://localhost:5000/api/v1/cats
```

## 端点列表

### 猫咪管理
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/v1/cats` | 获取猫咪列表 |
| POST | `/api/v1/cats` | 创建新猫咪 |
| GET | `/api/v1/cats/:id` | 获取猫咪详情 |
| PUT | `/api/v1/cats/:id` | 更新猫咪信息 |
| DELETE | `/api/v1/cats/:id` | 删除猫咪 |

## 请求/响应示例

### 创建猫咪 (POST)
```http
POST /api/v1/cats
Content-Type: application/json
Authorization: Bearer {token}

{
  "user_id": 1,
  "name": "Whiskers",
  "age": 2,
  "breed": "Tabby"
}
```

### 响应
```json
{
  "data": {
    "id": 123,
    "name": "Whiskers",
    "age": 2,
    "breed": "Tabby"
  },
  "meta": {
    "version": "v1"
  }
}
```

## 错误代码
- 400: 请求参数错误
- 401: 未授权
- 403: 禁止访问
- 404: 资源不存在
- 500: 服务器错误
