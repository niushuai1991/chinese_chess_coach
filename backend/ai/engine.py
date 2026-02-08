"""AI引擎"""

import json
import logging
import os
import time

from zhipuai import ZhipuAI

from backend.ai.prompts import SYSTEM_PROMPT
from backend.game.state import GameManager
from backend.models.schemas import Piece, PieceType, PlayerColor

logger = logging.getLogger(__name__)


class AIEngine:
    """AI对弈引擎"""

    def __init__(self, game_manager=None) -> None:
        self.client = ZhipuAI(
            api_key=os.getenv("OPENAI_API_KEY")  # 智谱API key
        )
        self.model = os.getenv("MODEL_NAME", "glm-4")
        self.game_manager = game_manager or GameManager()
        self.timeout = int(os.getenv("THINKING_TIMEOUT", "30"))

        logger.info(f"AI引擎初始化: Model={self.model}, Timeout={self.timeout}秒, 使用智谱官方SDK")

        # 棋子名称映射
        self._piece_names = {
            (PieceType.KING, PlayerColor.BLACK): "将",
            (PieceType.KING, PlayerColor.RED): "帅",
            (PieceType.ADVISOR, PlayerColor.BLACK): "士",
            (PieceType.ADVISOR, PlayerColor.RED): "仕",
            (PieceType.ELEPHANT, PlayerColor.BLACK): "象",
            (PieceType.ELEPHANT, PlayerColor.RED): "相",
            (PieceType.HORSE, PlayerColor.BLACK): "马",
            (PieceType.HORSE, PlayerColor.RED): "马",
            (PieceType.CHARIOT, PlayerColor.BLACK): "车",
            (PieceType.CHARIOT, PlayerColor.RED): "车",
            (PieceType.CANNON, PlayerColor.BLACK): "炮",
            (PieceType.CANNON, PlayerColor.RED): "炮",
            (PieceType.PAWN, PlayerColor.BLACK): "卒",
            (PieceType.PAWN, PlayerColor.RED): "兵",
        }

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

        # 获取当前玩家的所有棋子位置
        pieces_desc = self._get_pieces_description(game_state.board, game_state.current_player)

        ai_player = "红方" if game_state.current_player.value == "red" else "黑方"
        logger.info(f"🤖 {ai_player}AI正在思考...")
        print(f"\n{'=' * 60}")
        print(f"🤖 {ai_player}AI正在思考...")
        print(f"   棋盘FEN: {board_fen}")
        print(f"   当前{ai_player}棋子: {pieces_desc}")

        # 调用AI
        try:
            # 构建请求消息
            user_message = f"""当前{ai_player}棋子：
{pieces_desc}

当前棋盘FEN（仅供参考）：{board_fen}
当前执子: {ai_player}

请从上述列表中选择一个棋子，移动到合法位置。

注意：
- 炮的初始位置：黑方在第2行，红方在第7行
- 马的初始位置：黑方在第0行，红方在第9行
- 象的初始位置：黑方在第0行，红方在第9行

请下棋并解释，返回JSON格式。"""

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

            # 打印详细的走棋信息
            if complete_move and complete_move.piece:
                piece_name = self._get_piece_name(complete_move.piece)
                logger.info(f"✅ AI决定走: {result['move']} (棋子: {piece_name})")
                print(f"✅ AI决定走: {result['move']} (棋子: {piece_name})")

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

    def _get_pieces_description(self, board: list, color: PlayerColor) -> str:
        """生成棋子位置描述

        Args:
            board: 棋盘
            color: 玩家颜色

        Returns:
            棋子位置描述字符串，如："将(0,4), 车(0,0), 马(0,1)..."
        """
        pieces = []
        for row in range(10):
            for col in range(9):
                piece = board[row][col]
                if piece and piece.color == color:
                    piece_name = self._piece_names.get((piece.type, piece.color), "棋子")
                    pieces.append(f"{piece_name}({row},{col})")

        return ", ".join(pieces) if pieces else "无棋子"

    def _get_piece_name(self, piece: Piece) -> str:
        """获取棋子的中文名称

        Args:
            piece: 棋子对象

        Returns:
            棋子的中文名称，如"将"、"帅"、"马"等
        """
        return self._piece_names.get((piece.type, piece.color), "棋子")

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
