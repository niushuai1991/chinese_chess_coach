# 项目结构

## 目录树

```
chinese_chess_coach/
├── backend/
│   ├── main.py              # FastAPI应用入口
│   ├── api/                 # API路由
│   │   ├── __init__.py
│   │   ├── game.py          # 游戏接口
│   │   └── ai.py            # AI接口
│   ├── game/                # 游戏逻辑
│   │   ├── __init__.py
│   │   ├── chess.py         # 象棋规则引擎
│   │   └── state.py         # 游戏状态管理
│   ├── ai/                  # AI模块
│   │   ├── __init__.py
│   │   ├── engine.py        # AI引擎
│   │   └── prompts.py       # 系统提示词
│   └── models/              # 数据模型
│       ├── __init__.py
│       └── schemas.py       # Pydantic模型
├── frontend/
│   ├── index.html           # 主页面
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css    # 样式
│   │   └── js/
│   │       ├── game.js      # 游戏逻辑
│   │       ├── board.js     # 棋盘渲染
│   │       └── ai.js        # AI交互
│   └── assets/              # 棋子图片等
├── tests/
│   ├── test_game.py         # 游戏逻辑测试
│   ├── test_ai.py           # AI模块测试
│   └── test_api.py          # API测试
├── docs/                    # 文档
│   ├── DEVELOPMENT.md       # 开发命令
│   ├── CODE_STYLE.md        # 代码风格
│   ├── AI_GUIDELINES.md     # AI设计原则
│   └── STRUCTURE.md         # 本文件
├── .env                     # 环境变量（gitignore）
├── .env.example             # 环境变量模板
├── pyproject.toml           # uv项目配置
├── README.md                # 项目说明
└── AGENTS.md                # AI开发指南
```

## 模块职责

### Backend

#### `main.py`
- FastAPI应用初始化
- 中间件配置
- 路由注册
- CORS设置

#### `api/game.py`
- 创建游戏会话
- 玩家下棋接口
- 悔棋接口
- 历史记录查询

#### `api/ai.py`
- AI下棋接口
- 棋步解释生成
- 局面分析

#### `game/chess.py`
- 棋盘表示
- 棋子移动规则
- 合法性验证
- 胜负判断

#### `game/state.py`
- 游戏状态管理
- 会话存储
- 历史记录
- 悔棋逻辑

#### `ai/engine.py`
- OpenAI API封装
- 棋步生成
- 提示词构建

#### `ai/prompts.py`
- 系统提示词定义
- 用户提示词模板
- 输出验证

#### `models/schemas.py`
- Pydantic模型
- 请求/响应模型
- 数据验证

### Frontend

#### `index.html`
- 主页面结构
- 棋盘布局
- 控制面板

#### `static/js/game.js`
- 游戏流程控制
- API调用
- 状态管理

#### `static/js/board.js`
- 棋盘渲染
- 棋子显示
- 动画效果

#### `static/js/ai.js`
- AI交互
- 解释显示
- 局面分析

### Tests

#### `test_game.py`
- 象棋规则测试
- 棋步验证测试
- 胜负判断测试

#### `test_ai.py`
- AI引擎测试
- 提示词测试
- Mock API测试

#### `test_api.py`
- API端点测试
- 集成测试
- 错误处理测试

## Git忽略规则

```gitignore
# Python
__pycache__/
*.py[cod]
*.so
.Python
.venv/
.uv/
*.egg-info/
dist/

# 工具
.mypy_cache/
.ruff_cache/
.pytest_cache/

# 环境变量
.env
*.db
*.log

# 系统
.DS_Store
```
