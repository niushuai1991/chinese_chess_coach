"""Moonfish引擎包装器

使用真实的Moonfish引擎（Python 3版本）
"""

import sys
import logging
from pathlib import Path
from typing import Tuple, Optional, List

# 添加moonfish到Python路径
moonfish_path = Path(__file__).parent.parent.parent / "moonfish"
sys.path.insert(0, str(moonfish_path))

try:
    import moonfish
except ImportError:
    raise ImportError(f"无法导入moonfish，请确保moonfish目录存在于: {moonfish_path}")

logger = logging.getLogger(__name__)


class MoonfishEngine:
    """Moonfish引擎包装器"""

    def __init__(self, depth: int = 4):
        """初始化引擎

        Args:
            depth: 搜索深度（3-5）
        """
        self.depth = depth
        self.searcher = moonfish.Searcher()
        logger.info(f"🤖 Moonfish引擎初始化: 搜索深度={depth}")

    def get_best_move(
        self, board: str, player: str = "red"
    ) -> Optional[Tuple[Tuple[int, int], Tuple[int, int], int]]:
        """获取最佳棋步

        Args:
            board: Moonfish格式的182字符字符串
            player: 'red' 或 'black'

        Returns:
            ((from_row, from_col), (to_row, to_col), score) 或 None
        """
        # 将10x9棋盘转换为Moonfish格式
        moonfish_board = self._to_moonfish_board(board)

        # 创建Position对象
        # move_color: 0=RED, 1=BLACK
        move_color = 0 if player == "red" else 1

        # 初始分数
        score = self._evaluate_initial_board(moonfish_board, player)

        pos = moonfish.Position(board=moonfish_board, move_color=move_color, score=score)

        # 搜索
        try:
            move, score, depth = self.searcher.search(pos, secs=2, max_depth=self.depth)

            if move is None:
                logger.warning("Moonfish未找到合法棋步")
                return None

            # 转换移动坐标
            from_pos = self._moonfish_idx_to_2d(move[0])
            to_pos = self._moonfish_idx_to_2d(move[1])

            logger.info(f"✅ 最佳棋步: {from_pos}->{to_pos}, 分数={score}, 深度={depth}")

            return (from_pos, to_pos, score)

        except Exception as e:
            logger.error(f"Moonfish搜索失败: {e}")
            return None

    def _to_moonfish_board(self, board: str) -> str:
        """将10x9棋盘字符串转换为Moonfish格式

        Moonfish格式：182字符，包含padding
        格式：14行 x 13列（上下2行padding，左右2列padding）
        """
        # 如果已经是182字符，直接返回
        if len(board) == 182:
            return board

        # 否则，假设是10x9的紧凑格式，转换
        lines = board.split("\n") if "\n" in board else [board[i : i + 9] for i in range(0, 90, 9)]

        # 添加padding
        moonfish_lines = []

        # 顶部padding（2行）
        moonfish_lines.append(" " * 13)
        moonfish_lines.append(" " * 13)

        # 棋盘行（添加左右padding）
        for line in lines:
            moonfish_lines.append(f"  {line}  ")

        # 底部padding（2行）
        moonfish_lines.append(" " * 13)
        moonfish_lines.append(" " * 13)

        return "\n".join(moonfish_lines)

    def _moonfish_idx_to_2d(self, idx: int) -> Tuple[int, int]:
        """将Moonfish的0-181索引转换为2D坐标

        Moonfish使用182字符字符串，布局为14行x13列
        实际棋盘：10行x9列，上下左右有padding
        """
        # Moonfish布局：14行，13列
        row = idx // 13
        col = idx % 13

        # 减去padding（上下2行，左右2列）
        actual_row = row - 2
        actual_col = col - 2

        # 检查边界
        if not (0 <= actual_row < 10 and 0 <= actual_col < 9):
            logger.warning(f"Moonfish索引{idx}超出范围: ({actual_row}, {actual_col})")

        return (actual_row, actual_col)

    def _evaluate_initial_board(self, board: str, player: str) -> int:
        """评估初始棋盘分数

        使用Moonfish的piece-square tables
        """
        # 简单评估：计算双方棋子价值差
        piece_values = {
            "K": 10000,  # 将/帅
            "R": 900,  # 车
            "N": 400,  # 马
            "B": 200,  # 相/象
            "A": 200,  # 仕/士
            "C": 450,  # 炮
            "P": 100,  # 兵/卒
        }

        score = 0

        for char in board:
            if char == "." or char.isspace():
                continue

            # 大写=红方，小写=黑方
            value = piece_values.get(char.upper(), 0)

            if char.isupper():
                # 红方
                if player == "red":
                    score += value
                else:
                    score -= value
            else:
                # 黑方
                if player == "black":
                    score += value
                else:
                    score -= value

        return score
