"""AI引擎"""

import json
import logging
import os
import time

from zhipuai import ZhipuAI

from backend.ai.prompts import SYSTEM_PROMPT
from backend.game.state import GameManager
from backend.models.schemas import Piece, PieceType, PlayerColor
from backend.engines.moonfish_adapter import MoonfishAdapter

logger = logging.getLogger(__name__)


class AIEngine:
    """AI对弈引擎"""

    def __init__(self, game_manager=None) -> None:
        self.game_manager = game_manager or GameManager()

        # 引擎类型：llm 或 moonfish
        self.engine_type = os.getenv("AI_ENGINE_TYPE", "moonfish").lower()

        if self.engine_type == "moonfish":
            self._init_moonfish_engine()
        else:
            self._init_llm_engine()

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

    def _init_moonfish_engine(self):
        """初始化Moonfish引擎"""
        from backend.engines.moonfish_engine_v3 import MoonfishEngine

        # 搜索深度：从环境变量读取，默认3
        search_depth = int(os.getenv("MOONFISH_DEPTH", "3"))

        self.moonfish_engine = MoonfishEngine(depth=search_depth)
        self.engine_type = "moonfish"

        logger.info(f"🤖 AI引擎初始化: Moonfish本地引擎, 搜索深度={search_depth}")

    def _init_llm_engine(self):
        """初始化LLM引擎（智谱AI）"""
        self.client = ZhipuAI(
            api_key=os.getenv("OPENAI_API_KEY")  # 智谱API key
        )
        self.model = os.getenv("MODEL_NAME", "glm-4")
        self.timeout = int(os.getenv("THINKING_TIMEOUT", "30"))

        logger.info(f"AI引擎初始化: Model={self.model}, Timeout={self.timeout}秒, 使用智谱官方SDK")

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

        # 使用Moonfish引擎
        if self.engine_type == "moonfish":
            return await self._make_move_with_moonfish(game_state, session_id)

        # 使用LLM引擎（原始逻辑）
        return await self._make_move_with_llm(game_state, session_id)

    async def _make_move_with_moonfish(self, game_state, session_id: str) -> dict:
        """使用Moonfish引擎下棋

        Args:
            game_state: 游戏状态
            session_id: 会话ID

        Returns:
            包含move, explanation, game_state的字典
        """
        player = game_state.current_player
        ai_player = "红方" if player.value == "red" else "黑方"

        logger.info(f"🤖 {ai_player}AI正在思考... (Moonfish引擎)")
        print(f"\n{'=' * 60}")
        print(f"🤖 {ai_player}AI正在思考... (Moonfish引擎)")

        # 记录请求开始时间
        start_time = time.time()

        try:
            # 将游戏状态棋盘转换为Moonfish格式
            import moonfish
            from backend.engines.moonfish_adapter import MoonfishAdapter

            # 转换棋盘
            moonfish_board = MoonfishAdapter.board_to_moonfish(game_state.board)
            logger.info(f"游戏棋盘转换为Moonfish格式，长度: {len(moonfish_board)}")
            logger.debug(f"紧凑棋盘内容:\n{repr(moonfish_board)}")

            # 转换为Moonfish的182字符格式（添加padding）
            # Moonfish格式：14行，每行12个字符 + \n = 13字符
            moonfish_lines = []

            # 顶部padding（2行）- 每行12个空格
            moonfish_lines.append(" " * 12)
            moonfish_lines.append(" " * 12)

            # 棋盘行（添加左右padding，每行2个空格+9个字符+1个空格=12）
            lines = moonfish_board.split("\n")
            for line in lines:
                # 确保每行都是9个字符（填充右侧空格）
                line = line.ljust(9)
                moonfish_lines.append(f"  {line} ")

            # 底部padding（2行）- 每行12个空格
            moonfish_lines.append(" " * 12)
            moonfish_lines.append(" " * 12)

            moonfish_board = "\n".join(moonfish_lines) + "\n"
            logger.info(f"Moonfish棋盘长度: {len(moonfish_board)}")
            logger.debug(f"最终棋盘行数: {len(moonfish_lines)}")
            logger.debug(f"最终棋盘内容:\n{repr(moonfish_board)}")

            # 确定move_color：0=红方，1=黑方
            move_color = 0 if game_state.current_player.value == "red" else 1
            logger.info(f"当前玩家: {game_state.current_player.value}, move_color: {move_color}")

            # 创建Position
            # 注意：Moonfish的gen_moves()只生成大写字母的走法
            # 当move_color=1（黑方）时，需要旋转棋盘使黑方棋子变成大写
            if move_color == 1:
                # 黑方走棋，需要旋转棋盘
                pos = moonfish.Position(
                    board=moonfish_board[::-1].swapcase(), move_color=move_color, score=0
                )
            else:
                # 红方走棋，使用原始棋盘
                pos = moonfish.Position(board=moonfish_board, move_color=move_color, score=0)

            # 生成走法
            moves = list(pos.gen_moves())
            logger.info(f"生成的走法数量: {len(moves)}")

            # 创建Searcher
            searcher = moonfish.Searcher()

            # 搜索
            move, score, depth = searcher.search(pos, secs=2, max_depth=1)
            logger.info(f"搜索完成: move={move}, score={score}")

            if move is None:
                raise Exception("Moonfish未找到合法棋步")

            # 转换移动坐标（Moonfish返回的索引需要转换为2D坐标）
            # Moonfish使用0-181索引，需要转换为row, col
            # 182字符 = 14行 x 13列
            # row = idx // 13, col = idx % 13
            # 然后减去padding（row -= 2, col -= 2）
            from_idx, to_idx = move

            # 如果是黑方走棋，索引需要旋转回来（因为棋盘被旋转了）
            if move_color == 1:
                from_idx = 181 - from_idx
                to_idx = 181 - to_idx

            # 转换from_idx
            from_row = from_idx // 13 - 2
            from_col = from_idx % 13 - 2
            if 0 <= from_row < 10 and 0 <= from_col < 9:
                from backend.models.schemas import Position

                from_pos = Position(row=from_row, col=from_col)
            else:
                # 超出范围，使用默认值
                from_pos = Position(row=0, col=0)
                logger.warning(f"Moonfish返回的from_idx超出范围: {from_idx}")

            # 转换to_idx
            to_row = to_idx // 13 - 2
            to_col = to_idx % 13 - 2
            if 0 <= to_row < 10 and 0 <= to_col < 9:
                import backend.models.schemas

                to_pos = Position(row=to_row, col=to_col)
            else:
                # 超出范围，使用默认值
                to_pos = Position(row=0, col=0)
                logger.warning(f"Moonfish返回的to_idx超出范围: {to_idx}")

            logger.info(f"Moonfish棋步: from_idx={from_idx}, to_idx={to_idx}")
            logger.info(f"转换后坐标: from_pos={from_pos}, to_pos={to_pos}")

            # 执行棋步
            new_state = self.game_manager.make_move(session_id, from_pos, to_pos)

            # 从游戏状态中获取完整的Move对象
            complete_move = new_state.move_history[-1] if new_state.move_history else None

            # 获取棋子名称
            if complete_move and complete_move.piece:
                piece_name = self._get_piece_name(complete_move.piece)
                logger.info(f"✅ AI决定走: ({from_pos}->{to_pos}) (棋子: {piece_name})")
                print(f"✅ AI决定走: ({from_pos}->{to_pos}) (棋子: {piece_name})")

            # 计算请求耗时
            elapsed_time = time.time() - start_time
            logger.info(f"   ⏱️  响应时间: {elapsed_time:.2f}秒")
            print(f"   ⏱️  响应时间: {elapsed_time:.2f}秒")

            # 生成解释
            explanation = self._generate_moonfish_explanation(complete_move, score, elapsed_time)

            print(f"💭 AI解释: {explanation}")
            print(f"{'=' * 60}\n")

            return {
                "move": complete_move,
                "explanation": explanation,
                "game_state": new_state,
            }

        except Exception as e:
            elapsed_time = time.time() - start_time if "start_time" in locals() else 0

            logger.error(f"   ❌ Moonfish下棋失败:")
            logger.error(f"      - 错误类型: {type(e).__name__}")
            logger.error(f"      - 错误信息: {str(e)}")
            logger.error(f"      - 耗用时间: {elapsed_time:.2f}秒")

            print(f"❌ Moonfish下棋失败: {str(e)}")
            print(f"   错误类型: {type(e).__name__}")
            print(f"   耗用时间: {elapsed_time:.2f}秒")

            raise Exception(f"Moonfish下棋失败: {str(e)}")

    def _generate_moonfish_explanation(self, move, score: int, elapsed_time: float) -> str:
        """生成Moonfish棋步解释

        Args:
            move: Move对象
            score: 评估分数
            elapsed_time: 响应时间

        Returns:
            解释文本
        """
        if not move:
            return "使用本地搜索引擎快速分析后选择的最佳走法。"

        piece_name = self._get_piece_name(move.piece)
        from_pos = move.from_pos
        to_pos = move.to_pos

        # 基础解释
        explanation = f"经过本地搜索引擎深度分析（{elapsed_time:.2f}秒），选择"

        # 吃子解释
        if move.captured:
            captured_name = self._get_piece_name(move.captured)
            explanation += f"{piece_name}从{from_pos}移动到{to_pos}，吃掉对方的{captured_name}。"
        else:
            explanation += f"{piece_name}从{from_pos}移动到{to_pos}。"

        # 分数解释
        if score > 100:
            explanation += f" 评估显示这是一步优势棋步（评分：+{score}）。"
        elif score < -100:
            explanation += f" 评估显示这是一步防守棋步（评分：{score}）。"
        else:
            explanation += " 评估显示局面平稳。"

        return explanation

    async def _make_move_with_llm(self, game_state, session_id: str) -> dict:
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
                thinking={"type": "disabled"},  # 显式禁用思考模式，优化响应速度
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
            logger.info(
                f"   尝试执行棋步: {parsed_move['from_pos'].model_dump()} -> {parsed_move['to_pos'].model_dump()}"
            )
            new_state = self.game_manager.make_move(
                session_id, parsed_move["from_pos"], parsed_move["to_pos"]
            )

            # 从游戏状态中获取完整的Move对象
            complete_move = new_state.move_history[-1] if new_state.move_history else None

            logger.info(
                f"   返回的 Move 对象包含: {complete_move.model_dump() if complete_move else None}"
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
