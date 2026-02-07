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

    def __init__(self, game_manager=None) -> None:
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL")
        )
        self.model = os.getenv("MODEL_NAME", "gpt-4")
        self.game_manager = game_manager or GameManager()
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

        ai_player = "红方" if game_state.current_player.value == "red" else "黑方"
        logger.info(f"🤖 {ai_player}AI正在思考...")
        print(f"\n{'=' * 60}")
        print(f"🤖 {ai_player}AI正在思考...")
        print(f"   棋盘FEN: {board_fen}")

        # 调用AI
        try:
            logger.info(f"   正在调用 {self.model} API... (超时: {self.timeout}秒)")
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
                timeout=self.timeout,
            )

            content = response.choices[0].message.content
            if not content:
                raise Exception("AI返回空内容")

            logger.info(f"   AI原始响应: {content}")

            result = json.loads(content)
            logger.info(f"✅ AI决定走: {result['move']}")
            print(f"✅ AI决定走: {result['move']}")
            print(f"💭 AI解释: {result['explanation']}")
            print(f"{'=' * 60}\n")

            # 执行AI的棋步
            move = self._parse_ai_move(result["move"])
            new_state = self.game_manager.make_move(session_id, move["from_pos"], move["to_pos"])

            return {"move": move, "explanation": result["explanation"], "game_state": new_state}

        except Exception as e:
            logger.exception(f"❌ AI生成棋步失败: {str(e)}")
            print(f"❌ AI生成棋步失败: {str(e)}")
            print(f"   错误类型: {type(e).__name__}")
            raise Exception(f"AI生成棋步失败: {str(e)}")

    def _board_to_fen(self, board: list) -> str:
        """将棋盘转换为FEN格式"""
        rows = []
        for row in board:
            row_str = ""
            empty_count = 0
            for piece in row:
                if piece is None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        row_str += str(empty_count)
                        empty_count = 0

                    char = piece.type.value
                    if piece.color.value == "red":
                        char = char.upper()
                    row_str += char

            if empty_count > 0:
                row_str += str(empty_count)

            rows.append(row_str)

        return "/".join(rows)

    def _parse_ai_move(self, move_str: str) -> dict:
        """解析AI返回的棋步

        Args:
            move_str: 棋步字符串，支持格式：
                - 坐标格式: "(3,4)->(5,4)" 或 "(3,4)-(5,4)"
                - JSON格式: '{"from": {"row": 3, "col": 4}, "to": {"row": 5, "col": 4}}'

        Returns:
            包含from_pos和to_pos的字典
        """
        from backend.models.schemas import Position

        try:
            # 尝试解析 JSON 格式
            if "{" in move_str:
                data = json.loads(move_str)
                if "from" in data and "to" in data:
                    return {
                        "from_pos": Position(**data["from"]),
                        "to_pos": Position(**data["to"]),
                    }

            # 尝试解析坐标格式 "(row,col)->(row,col)"
            import re

            match = re.match(r"\((\d+),(\d+)\)->\((\d+),(\d+)\)", move_str.strip())
            if match:
                return {
                    "from_pos": Position(row=int(match.group(1)), col=int(match.group(2))),
                    "to_pos": Position(row=int(match.group(3)), col=int(match.group(4))),
                }

            raise ValueError(f"无法解析棋步: {move_str}")

        except Exception as e:
            logger.error(f"解析棋步失败: {move_str}, 错误: {e}")
            raise ValueError(f"无效的棋步格式: {move_str}")
