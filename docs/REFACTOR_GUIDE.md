# CATalogue 重构指南

## 1. 配置管理重构
- 所有配置项迁移到环境变量
- 通过Config类统一管理
- 默认值在代码中定义

## 2. 多语言支持实现
- 使用Flask-Babel扩展
- 翻译文件存放于translations目录
- 模板中使用`_()`标记翻译文本

## 3. 架构优化
- 明确分层结构：路由层->服务层->数据访问层
- 服务层继承BaseService
- 路由层使用BaseCRUD

## 4. 代码迁移步骤
1. 提取硬编码配置到Config类
2. 标记所有需要翻译的文本
3. 重构服务层实现
4. 更新测试用例

## 5. 验证方法
- 运行测试套件：`pytest tests/`
- 检查翻译覆盖率：`pybabel extract -F babel.cfg -o messages.pot .`
- 验证配置加载
