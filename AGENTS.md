# 开发指南索引

详细的开发文档已拆分到以下文件：

- **[DEVELOPMENT.md](docs/DEVELOPMENT.md)** - 开发命令参考
  - 依赖管理
  - 运行服务
  - 测试命令
  - 代码质量检查

- **[CODE_STYLE.md](docs/CODE_STYLE.md)** - 代码风格指南
  - Python代码规范
  - 前端代码规范
  - 命名规范
  - 最佳实践

- **[AI_GUIDELINES.md](docs/AI_GUIDELINES.md)** - AI设计原则
  - 系统提示词模板
  - 输出验证
  - 常见问题处理

- **[STRUCTURE.md](docs/STRUCTURE.md)** - 项目结构
  - 目录树
  - 模块职责
  - Git忽略规则

## 快速参考

### 开发流程
1. 新增功能前先写测试
2. 运行 `uv run mypy backend/` 确保类型正确
3. 运行 `uv run ruff check --fix backend/ && uv run ruff format backend/`
4. 运行 `uv run pytest` 确保测试通过
5. 提交前确保覆盖率不低于80%

### 技术栈
- **语言**: Python 3.11+
- **包管理器**: `uv`
- **后端框架**: FastAPI
- **前端**: 纯HTML/JS + CSS
- **AI**: OpenAI兼容API
