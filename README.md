# 中国象棋AI教练

一个基于FastAPI和OpenAI兼容API的中国象棋对弈网站，AI会在每步棋后提供详细解释，帮助学习象棋策略。

## 功能特性

- 🤖 **AI对弈**: 与AI对弈，实时获取棋步解释
- 📝 **历史记录**: 查看完整的对局记录和AI解说
- ↩️ **悔棋功能**: 支持悔棋，重新思考策略
- 🎨 **精美界面**: 响应式设计，支持移动端
- 🔀 **先手选择**: 可选择执红先行或执黑后行

## 快速开始

### 1. 安装依赖

```bash
# 使用uv安装依赖
uv sync
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，填写你的API配置
# OPENAI_API_KEY=your_api_key_here
# OPENAI_BASE_URL=https://api.openai.com/v1
```

### 3. 启动服务

```bash
# 开发模式
uv run uvicorn backend.main:app --reload --port 8000

# 或使用
uv run python backend/main.py
```

### 4. 访问网站

打开浏览器访问: http://localhost:8000

## 开发指南

### 运行测试

```bash
# 所有测试
uv run pytest

# 单个文件
uv run pytest tests/test_game.py

# 单个函数
uv run pytest tests/test_game.py::test_create_game

# 覆盖率报告
uv run pytest --cov=backend --cov-report=html
```

### 代码质量检查

```bash
# 类型检查
uv run mypy backend/

# 代码检查
uv run ruff check backend/

# 自动修复
uv run ruff check --fix backend/

# 格式化代码
uv run ruff format backend/
```

## 项目结构

```
chinese_chess_coach/
├── backend/                 # 后端代码
│   ├── api/                # API路由
│   ├── game/               # 游戏逻辑
│   ├── ai/                 # AI引擎
│   └── models/             # 数据模型
├── frontend/               # 前端代码
│   ├── index.html
│   └── static/
│       ├── css/
│       └── js/
├── tests/                  # 测试代码
├── AGENTS.md               # 开发指南
└── README.md               # 本文件
```

## 技术栈

- **后端**: Python 3.11+, FastAPI, Uvicorn
- **前端**: 纯HTML/JavaScript + CSS3
- **AI**: OpenAI兼容API
- **测试**: Pytest
- **代码质量**: MyPy, Ruff

## License

MIT
