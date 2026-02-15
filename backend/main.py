"""中国象棋教练 - 后端应用"""

import logging
import os

from dotenv import load_dotenv

# 加载环境变量（必须在导入其他模块之前）
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api import ai, game, settings

# 配置日志
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # 输出到控制台
        logging.FileHandler("logs/xiangqi.log", encoding="utf-8"),  # 输出到文件
    ],
)

logger = logging.getLogger(__name__)
logger.info("🚀 中国象棋AI教练服务启动中...")

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
app.include_router(settings.router, tags=["settings"])

# 静态文件服务
frontend_path = os.path.join(os.path.dirname(__file__), "../frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")


@app.get("/health")
async def health_check() -> dict:
    """健康检查"""
    return {"status": "ok"}
