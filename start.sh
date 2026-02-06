#!/bin/bash

echo "中国象棋AI教练 - 启动脚本"
echo "========================"
echo ""

# 检查.env文件
if [ ! -f .env ]; then
    echo "错误: .env文件不存在"
    echo "请先复制.env.example为.env并配置API密钥"
    exit 1
fi

# 检查依赖
if ! uv run python -c "import fastapi" 2>/dev/null; then
    echo "正在安装依赖..."
    uv sync
fi

# 启动服务
echo ""
echo "🚀 启动服务器..."
echo "访问地址: http://localhost:8000"
echo ""
echo "按Ctrl+C停止服务器"
echo ""

uv run uvicorn backend.main:app --reload --port 8000
