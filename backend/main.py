"""中国象棋教练 - 后端应用"""

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api import ai, game

# 加载环境变量
load_dotenv()

app = FastAPI(title="中国象棋AI教练", description="与AI对弈并学习象棋策略", version="0.1.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(game.router, prefix="/api/game", tags=["game"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])

# 静态文件服务
frontend_path = os.path.join(os.path.dirname(__file__), "../frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")


@app.get("/health")
async def health_check() -> dict:
    """健康检查"""
    return {"status": "ok"}
