# 开发命令参考

## 依赖管理

```bash
uv sync                           # 安装所有依赖
uv add fastapi uvicorn           # 添加新依赖
uv remove package_name           # 移除依赖
```

## 运行服务

```bash
uv run uvicorn backend.main:app --reload --port 8000    # 启动开发服务器
uv run python backend/main.py                           # 备用启动方式
```

## 测试

```bash
uv run pytest                                    # 运行所有测试
uv run pytest tests/test_game.py                # 测试单个文件
uv run pytest tests/test_game.py::test_func     # 测试单个函数
uv run pytest -v                                # 详细输出
uv run pytest --cov=backend                     # 生成覆盖率报告
uv run pytest --cov=backend --cov-report=html   # HTML覆盖率报告
```

## 代码质量

```bash
uv run mypy backend/                            # 类型检查
uv run ruff check backend/                      # 代码检查
uv run ruff format backend/                     # 格式化代码
uv run ruff check --fix backend/ && uv run ruff format backend/  # 修复+格式化
```

## 开发流程

1. 新增功能前先写测试
2. 运行 `uv run mypy backend/` 确保类型正确
3. 运行 `uv run ruff check --fix backend/ && uv run ruff format backend/`
4. 运行 `uv run pytest` 确保测试通过
5. 提交前确保覆盖率不低于80%
