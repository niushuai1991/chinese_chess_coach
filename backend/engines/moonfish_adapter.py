"""Moonfish引擎适配器"""

import logging
from typing import Tuple, Optional, Dict

from backend.models.schemas import Piece, PieceType, PlayerColor, Position

logger = logging.getLogger(__name__)


class MoonfishAdapter:
    """处理当前项目与Moonfish之间的棋盘格式转换"""

    # 棋子类型映射（当前项目 → Moonfish）
    PIECE_TO_MOONFISH = {
        PieceType.KING: "K",  # 帅/将 → K
        PieceType.ADVISOR: "A",  # 仕/士 → A
        PieceType.ELEPHANT: "B",  # 相/象 → B
        PieceType.HORSE: "N",  # 马 → N
        PieceType.CHARIOT: "R",  # 车 → R
        PieceType.CANNON: "C",  # 炮 → C
        PieceType.PAWN: "P",  # 兵/卒 → P
    }

    # Moonfish棋子 → 当前项目
    MOONFISH_TO_PIECE = {
        "K": PieceType.KING,
        "A": PieceType.ADVISOR,
        "B": PieceType.ELEPHANT,
        "N": PieceType.HORSE,
        "R": PieceType.CHARIOT,
        "C": PieceType.CANNON,
        "P": PieceType.PAWN,
        ".": None,  # 空格
    }

    @staticmethod
    def board_to_moonfish(board: list) -> str:
        """
        将10x9的2D数组转换为Moonfish的182字符字符串

        Args:
            board: 当前项目的棋盘[10][9]

        Returns:
            182字符字符串（Moonfish格式）
        """
        lines = []

        # Moonfish的字符串是从第0行（黑方底线）到第9行（红方底线）
        for row in range(10):
            line_chars = []

            for col in range(9):
                piece = board[row][col]

                if piece is None:
                    # 空格
                    line_chars.append(".")
                else:
                    # Moonfish字符：大写=红方，小写=黑方
                    moon_char = MoonfishAdapter.PIECE_TO_MOONFISH[piece.type]

                    # 判断颜色
                    if piece.color == PlayerColor.RED:
                        char = moon_char.upper()
                    else:
                        char = moon_char.lower()

                    line_chars.append(char)

            line = "".join(line_chars)
            lines.append(line)

        return "\n".join(lines)

    @staticmethod
    def moonfish_to_board(moonfish_board: str) -> list:
        """
        将Moonfish的182字符字符串转换为10x9的2D数组

        Args:
            moonfish_board: 182字符字符串

        Returns:
            10x9的2D数组
        """
        board = [[None for _ in range(9)] for _ in range(10)]
        lines = moonfish_board.split("\n")

        for row_idx, line in enumerate(lines):
            for col_idx, char in enumerate(line):
                if char == ".":
                    continue

                # 判断颜色和棋子类型
                is_upper = char.isupper()
                piece_type = MoonfishAdapter.MOONFISH_TO_PIECE.get(char.upper())

                if piece_type is None:
                    logger.warning(f"未知棋子字符: {char} at ({row_idx}, {col_idx})")
                    continue

                # 确定颜色
                color = PlayerColor.RED if is_upper else PlayerColor.BLACK

                # 创建棋子对象
                board[row_idx][col_idx] = Piece(type=piece_type, color=color)

        return board

    @staticmethod
    def move_to_moonfish(from_pos: Position, to_pos: Position, piece: Piece) -> str:
        """
        将项目的移动格式转换为Moonfish UCCI格式

        Args:
            from_pos, to_pos: Position(row, col)
            piece: 棋子对象

        Returns:
            UCCI格式字符串，如"e2e4"
        """
        # Moonfish使用0-based索引，行号0-9，列号0-8
        # UCCI格式：列字母(a-i) + 行数字(1-9)
        # 注意：行号从1开始，不是0
        col_letters = "abcdefghi"

        # UCCI使用从0开始，行号=当前行+1
        from_str = f"{col_letters[from_pos.col]}{from_pos.row + 1}"
        to_str = f"{col_letters[to_pos.col]}{to_pos.row + 1}"

        return f"{from_str}{to_str}"

    @staticmethod
    def moonfish_to_move(moonfish_move: Tuple[int, int]) -> Tuple[Position, Position]:
        """
        将Moonfish的移动索引转换为项目坐标

        Args:
            moonfish_move: (from_idx, to_idx)，每个索引是0-181

        Returns:
            ((from_row, from_col), (to_row, to_col))
        """
        # Moonfish棋盘布局：14行 × 13列（包含padding）
        # 实际棋盘：10行 × 9列（0-8列）
        # padding：上下2行，左右2列
        # 棋盘列范围：列2-10（对应实际0-8列）

        from_idx, to_idx = moonfish_move

        # 转换索引为2D坐标（包含padding）
        from_row = from_idx // 13
        from_col = from_idx % 13
        to_row = to_idx // 13
        to_col = to_idx % 13

        # 减去padding，得到实际棋盘坐标
        # 列0-1和11-12是padding，列2-10是实际棋盘
        actual_from_col = from_col - 2 if from_col >= 2 else 0
        actual_to_col = to_col - 2 if to_col >= 2 else 0

        # 检查边界（Moonfish可能返回超出范围）
        if from_row > 9 or actual_from_col > 8 or to_row > 9 or actual_to_col > 8:
            logger.warning(
                f"Moonfish返回的坐标超出范围: ({from_row},{actual_from_col})->({to_row},{actual_to_col})"
            )
            # 仍然返回，让上层处理

        return (
            Position(row=from_row, col=actual_from_col),
            Position(row=to_row, col=actual_to_col),
        )
