"""难度设置API

允许用户调整AI搜索深度
"""

import logging
import os
from typing import Dict

from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/settings", tags=["settings"])

# 全局难度设置（默认值从环境变量读取）
_current_difficulty = int(os.getenv("MOONFISH_DEPTH", "3"))


@router.get("/difficulty")
async def get_difficulty() -> Dict[str, int]:
    """获取当前难度设置

    Returns:
        包含难度值的字典
    """
    return {"difficulty": _current_difficulty}


@router.post("/difficulty")
async def set_difficulty(difficulty: int) -> Dict[str, str]:
    """设置难度

    Args:
        difficulty: 难度值（3-5）

    Returns:
        成功消息
    """
    global _current_difficulty

    # 验证难度值
    if difficulty not in [3, 4, 5]:
        raise HTTPException(
            status_code=400,
            detail=f"无效的难度值: {difficulty}。必须是3、4或5。",
        )

    _current_difficulty = difficulty

    # 更新环境变量（供后续引擎初始化使用）
    os.environ["MOONFISH_DEPTH"] = str(difficulty)

    logger.info(f"✅ 难度设置为: {difficulty}")

    return {
        "message": f"难度已设置为{difficulty}",
        "difficulty": difficulty,
    }
