"""AI引擎"""

import json
import logging
import os
import time

from openai import OpenAI

from backend.ai.prompts import SYSTEM_PROMPT
from backend.game.state import GameManager

logger = logging.getLogger(__name__)


class AIEngine:
    """AI对弈引擎"""

    def __init__(self, game_manager=None) -> None:
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
            max_retries=0,  # 禁用自动重试，避免超时后多次重试
        )
        self.model = os.getenv("MODEL_NAME", "gpt-4")
        self.game_manager = game_manager or GameManager()
        self.timeout = int(os.getenv("THINKING_TIMEOUT", "30"))

        logger.info(f"AI引擎初始化: Model={self.model}, Timeout={self.timeout}秒, MaxRetries=0")

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
            # 构建请求消息
            user_message = (
                f"当前棋局（FEN）: {board_fen}\n"
                f"当前执子: {'红方' if game_state.current_player == 'red' else '黑方'}\n"
                f"请下棋并解释，返回JSON格式。"
            )

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ]

            # 记录请求开始时间
            start_time = time.time()

            logger.info(f"   正在调用 {self.model} API...")
            logger.info(f"   📤 请求参数:")
            logger.info(f"      - Model: {self.model}")
            logger.info(f"      - Temperature: 0.7")
            logger.info(f"      - Timeout: {self.timeout}秒")
            logger.info(f"      - Messages: {len(messages)}条")
            logger.info(f"      - Base URL: {os.getenv('OPENAI_BASE_URL')}")

            # 输出完整的请求体
            logger.info(f"   📋 请求体详情:")
            for i, msg in enumerate(messages):
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                # 截断过长的内容用于日志
                content_preview = content[:200] + "..." if len(content) > 200 else content
                logger.info(f"      Message[{i}] - {role.upper()}:")
                logger.info(f"        {content_preview}")
                logger.info(f"        完整长度: {len(content)}字符")

            print(f"   正在调用 {self.model} API...")
            print(f"   📤 请求参数: Model={self.model}, Timeout={self.timeout}秒")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                response_format={"type": "json_object"},
                timeout=self.timeout,
            )

            # 计算请求耗时
            elapsed_time = time.time() - start_time

            # 记录响应信息
            logger.info(f"   📥 API响应成功:")
            logger.info(f"      - 响应时间: {elapsed_time:.2f}秒")
            logger.info(f"      - HTTP Status: 200 OK")
            logger.info(f"      - Response ID: {response.id}")
            logger.info(f"      - Model: {response.model}")
            logger.info(f"      - Choices数量: {len(response.choices)}")

            if hasattr(response, "usage") and response.usage:
                logger.info(f"      - Token使用:")
                logger.info(f"        * Prompt Tokens: {response.usage.prompt_tokens}")
                logger.info(f"        * Completion Tokens: {response.usage.completion_tokens}")
                logger.info(f"        * Total Tokens: {response.usage.total_tokens}")

            content = response.choices[0].message.content
            if not content:
                raise Exception("AI返回空内容")

            logger.info(f"   📝 完整响应体:")
            logger.info(f"      - Content: {content}")
            logger.info(f"      - Content长度: {len(content)}字符")

            # 尝试解析并验证JSON格式
            try:
                result = json.loads(content)
                logger.info(f"   ✅ JSON解析成功:")
                logger.info(f"      - move字段: {result.get('move')}")
                logger.info(f"      - explanation字段: {result.get('explanation')[:100]}...")
            except json.JSONDecodeError as e:
                logger.error(f"   ❌ JSON解析失败: {e}")
                raise
            logger.info(f"✅ AI决定走: {result['move']}")
            print(f"✅ AI决定走: {result['move']}")
            print(f"💭 AI解释: {result['explanation']}")
            print(f"{'=' * 60}\n")

            # 执行AI的棋步
            parsed_move = self._parse_ai_move(result["move"])
            new_state = self.game_manager.make_move(
                session_id, parsed_move["from_pos"], parsed_move["to_pos"]
            )

            # 从游戏状态中获取完整的Move对象
            complete_move = new_state.move_history[-1] if new_state.move_history else None

            logger.info(
                f"   返回的 Move 对象包含: {complete_move.dict() if complete_move else None}"
            )

            return {
                "move": complete_move,
                "explanation": result["explanation"],
                "game_state": new_state,
            }

        except Exception as e:
            elapsed_time = time.time() - start_time if "start_time" in locals() else 0

            logger.error(f"   ❌ API调用失败:")
            logger.error(f"      - 错误类型: {type(e).__name__}")
            logger.error(f"      - 错误信息: {str(e)}")
            logger.error(f"      - 已用时间: {elapsed_time:.2f}秒")

            # 如果是超时错误
            if "timeout" in str(e).lower() or "timed out" in str(e).lower():
                logger.error(f"      - 建议: 增加 THINKING_TIMEOUT 环境变量值")

            print(f"❌ AI生成棋步失败: {str(e)}")
            print(f"   错误类型: {type(e).__name__}")
            print(f"   已用时间: {elapsed_time:.2f}秒")

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
