"""AI引擎"""

import json
import logging
import os

from openai import OpenAI

from backend.ai.prompts import SYSTEM_PROMPT
from backend.game.state import GameManager

logger = logging.getLogger(__name__)


class AIEngine:
    """AI对弈引擎"""

    def __init__(self) -> None:
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL")
        )
        self.model = os.getenv("MODEL_NAME", "gpt-4")
        self.game_manager = GameManager()
        self.timeout = int(os.getenv("THINKING_TIMEOUT", "30"))

    async def make_move_with_explanation(self, session_id: str) -> dict:
        """AI下棋并返回解释

        Args:
            session_id: 游戏会话ID

        Returns:
            包含move, explanation, game_state的字典

        Raises:
            ValueError: 游戏不存在或已结束
            Exception: AI生成失败
        """
        game_state = self.game_manager.get_game(session_id)
        if not game_state:
            raise ValueError("游戏不存在")

        if game_state.is_checkmate or game_state.is_stalemate:
            raise ValueError("游戏已结束")

        # 获取棋盘表示
        board_fen = self._board_to_fen(game_state.board)

        # 调用AI
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"当前棋局（FEN）: {board_fen}\n"
                        f"当前执子: {'红方' if game_state.current_player == 'red' else '黑方'}\n"
                        f"请下棋并解释，返回JSON格式。",
                    },
                ],
                temperature=0.7,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            if not content:
                raise Exception("AI返回空内容")

            result = json.loads(content)

            # 执行AI的棋步
            move = self._parse_ai_move(result["move"])
            new_state = self.game_manager.make_move(session_id, move["from_pos"], move["to_pos"])

            return {"move": move, "explanation": result["explanation"], "game_state": new_state}

        except Exception:
            logger.exception("AI生成棋步失败")
            raise Exception("AI生成棋步失败，请重试")

    def _board_to_fen(self, board: list) -> str:
        """将棋盘转换为FEN格式（简化版）"""
        # 实际实现需要完整的中国象棋FEN转换
        return "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1"

    def _parse_ai_move(self, move_str: str) -> dict:
        """解析AI返回的棋步

        Args:
            move_str: 棋步字符串，如"炮二平五"

        Returns:
            包含from_pos和to_pos的字典
        """
        # 解析中国象棋记谱法
        # 实际实现需要完整解析逻辑
        return {"from_pos": {"row": 7, "col": 1}, "to_pos": {"row": 4, "col": 4}}
