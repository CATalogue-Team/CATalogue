# CATalogue API 文档

## 1. 认证API

### 登录
`POST /api/auth/login`

请求体:
```json
{
  "username": "string",
  "password": "string",
  "remember": "boolean"
}
```

响应:
- 200: 登录成功
- 401: 无效凭证
- 403: 账号未审核

### 注册
`POST /api/auth/register`

请求体:
```json
{
  "username": "string",
  "password": "string",
  "is_admin": "boolean"
}
```

响应:
- 201: 注册成功
- 400: 无效请求
- 500: 注册失败

## 2. 猫咪管理API

### 获取猫咪列表
`GET /api/cats/`

响应:
```json
[{
  "id": "number",
  "name": "string",
  "breed": "string",
  "age": "number",
  "description": "string",
  "is_adopted": "boolean",
  "created_at": "datetime"
}]
```

### 搜索猫咪
`GET /api/cats/search`

查询参数:
- q: 搜索关键词
- breed: 品种筛选
- min_age: 最小年龄
- max_age: 最大年龄
- is_adopted: 是否被领养

## 3. 文档标准
- 使用Swagger UI自动生成
- 访问路径: `/api/docs`
- 包含请求/响应示例
- 包含错误码说明

## 4. 响应格式规范
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {},
  "timestamp": "ISO8601"
}
```

## 5. 错误码
| 状态码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |
