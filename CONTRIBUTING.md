# CATalogue 项目贡献指南

感谢您有兴趣为CATalogue项目做贡献！以下是参与贡献的指南。

## 🚀 开始之前

1. 确保您已阅读[README](README_zh.md)了解项目
2. 检查[问题追踪系统](https://github.com/your-repo/CATalogue/issues)中是否有相关讨论

## 🛠️ 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/your-repo/CATalogue.git
cd CATalogue

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## 🔍 代码风格

- Python代码遵循[PEP 8](https://peps.python.org/pep-0008/)规范
- 使用类型注解(Type Hints)
- 文档字符串遵循Google风格
- 前端代码遵循Standard JS规范

## 📝 提交规范

提交信息遵循[Conventional Commits](https://www.conventionalcommits.org/)规范：

```
<类型>[可选的作用域]: <描述>

[可选的正文]

[可选的脚注]
```

示例：
```
feat(api): 添加猫咪搜索API

新增GET /cats/search端点，支持按品种和年龄筛选

Closes #123
```

## 🧪 测试要求

- 新功能必须包含单元测试
- 修改现有代码需确保测试通过
- 运行测试：
  ```bash
  pytest tests/
  ```

## 🔄 工作流程

1. Fork主仓库
2. 创建特性分支 (`git checkout -b feat/your-feature`)
3. 提交更改 (`git commit -am 'feat: add some feature'`)
4. 推送到分支 (`git push origin feat/your-feature`)
5. 创建Pull Request

## 💬 沟通渠道

- GitHub Issues: 功能请求和问题报告
- Discussions: 设计讨论和问题咨询
- Slack: 实时交流(需邀请)

## 🙏 行为准则

请遵守我们的[行为准则](CODE_OF_CONDUCT.md)
