# CATalogue 项目 Copilot 指南

## 项目架构
- 前端：SvelteKit + Vite，组件化开发，状态管理用 Svelte Stores。
- 后端：FastAPI (ASGI)，ORM 用 SQLAlchemy，接口遵循 RESTful，文档自动生成（OpenAPI/Swagger）。
- 数据库：PostgreSQL，规范见 `.clinerules/db-rules.md`。
- 规范文档均在 `.clinerules/` 目录，分 tech-specs、dev-rules、ops-rules。

## 关键开发流程
- 前端开发：
  - 入口 `src/routes/`，页面按路由分文件夹。
  - 组件 props/events 明确类型定义（见 `CatProfile.svelte` 示例）。
  - 状态统一用 Svelte Stores，参考 `cat.store.ts`。
  - 路由参数需校验，动态路由见 `[id]/+page.svelte`。
  - 性能优化：代码分割、图片懒加载、API 节流。
- 后端开发：
  - API 入口 `api/main.py`，业务分层（models、schemas、services、routers）。
  - 数据库迁移用 Alembic，配置见 `alembic.ini`。
  - 依赖管理：Python 用 Poetry，前端用 pnpm 或 npm，禁止直接改 `package-lock.json`。
- 测试与 CI/CD：
  - 单元测试覆盖率要求，测试入口 `tests/`。
  - 前端用 Vitest，后端用 pytest。
  - CI/CD 流程见 `.clinerules/ops-rules/deployment-rules.md`，分开发/测试/生产环境，日志级别区分。
  - 生产部署需严格权限管控，支持蓝绿/金丝雀发布。

## 项目约定与模式
- 组件/服务命名统一英文小写，目录结构按功能分层。
- 依赖分生产/开发，按字母序排列，主版本升级需团队评审。
- 重大变更记录到 `CHANGELOG.md`。
- 规范与技术决策均以 `.clinerules/tech-specs/project-discussion.md` 为准。

## 典型文件/目录参考
- `src/routes/cats/+page.svelte`：猫咪列表页面
- `src/routes/cats/[id]/+page.svelte`：猫咪详情页面
- `api/models/cat.py`：猫模型定义
- `api/services/cat_service.py`：猫业务逻辑
- `api/routers/cats.py`：猫相关路由
- `.clinerules/README.md`：规范文档索引

## 其他说明
- 所有规范文档需定期维护，变更需同步团队。
- 详细技术规范请查阅 `.clinerules/` 下各模块文档。

---
如有不清楚或遗漏之处，请反馈以便补充完善。
