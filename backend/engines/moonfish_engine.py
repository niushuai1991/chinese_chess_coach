"""Moonfish引擎（内嵌简化版）

这个文件包含Moonfish的搜索算法，完全内嵌到项目中
避免导入moonfish.py，避免类型错误
"""

from typing import Tuple, List, Optional
import logging
import time

logger = logging.getLogger(__name__)


class MoonfishEngine:
    """Moonfish搜索引擎（内嵌版）"""

    def __init__(self, depth: int = 4):
        """初始化引擎

        Args:
            depth: 搜索深度（3-5）
        """
        self.depth = depth
        self.max_depth = depth
        logger.info(f"🤖 Moonfish引擎初始化: 搜索深度={depth}")

        # 搜索统计
        self.nodes = 0

    def search(
        self, moonfish_board: List[List[str]], secs: int = 2, max_depth: int = None
    ) -> Optional[Tuple[int, int, int, int]]:
        """MTD-bi搜索

        Args:
            moonfish_board: 182字符的棋盘表示
            secs: 超时（秒）
            max_depth: 最大搜索深度

        Returns:
            ((from_idx, to_idx), score) 最佳棋步和分数，None表示无合法棋步
        """
        start_time = time.time()

        # 迭代加深
        for depth in range(1, self.max_depth + 1 if max_depth is None else self.max_depth):
            logger.debug(f"搜索深度: {depth}")

            score = self._alpha_beta(
                moonfish_board,
                depth,
                -10000,  # 负无穷大
                10000,  # 正无穷大
            )

            # 剪枝条件：如果找到必胜棋步或超时，停止
            if score >= 10000 or score <= -10000:
                break

        elapsed = time.time() - start_time
        logger.info(f"🔍 搜索完成: 深度={self.depth}, 耗时={elapsed:.2f}秒")

        return score

    def _alpha_beta(
        self, moonfish_board: List[List[str]], depth: int, alpha: int, beta: int
    ) -> int:
        """Alpha-Beta剪枝搜索"""
        best = -10000
        best_move = None

        # 生成所有合法走法并排序（启发式）
        moves = self._generate_ordered_moves(moonfish_board)

        for move in moves:
            # 模拟执行走法
            from_idx, to_idx = move

            # 评估走法
            score = self._evaluate_move(moonfish_board, from_idx, to_idx)

            # 剪枝
            if score > best:
                best = score
                best_move = move
            elif score == best and best_move is None:
                best_move = move

        return best

    def _generate_ordered_moves(self, moonfish_board: List[List[str]]) -> List[Tuple[int, int]]:
        """生成所有合法走法并排序（按价值）"""
        moves = []

        # 遍历所有棋子
        for row in range(10):
            for col in range(9):
                piece = moonfish_board[row][col]
                if piece == ".":
                    continue

                # 判断颜色
                is_red = piece.isupper()

                # 生成当前颜色的所有走法
                piece_moves = self._get_piece_moves(moonfish_board, row, col, is_red)

                # 添加到总列表
                moves.extend(piece_moves)

        # 排序：按走法价值降序
        moves.sort(key=lambda m: m[2], reverse=True)

        return moves

    def _get_piece_moves(
        self, moonfish_board: List[List[str]], row: int, col: int, is_red: bool
    ) -> List[Tuple[int, int]]:
        """获取单个棋子的所有合法走法"""
        piece = moonfish_board[row][col]
        piece_upper = piece.upper()

        # 兵/卒：向前1格，过河后可横走
        if piece_upper in "PA":  # Pawn
            moves = []

            # 向前
            new_row = row + 1 if is_red else row - 1
            if 0 <= new_row <= 9 and self._is_valid_position(moonfish_board, new_row, col):
                moves.append((row, col, new_row, col))

            # 过河判断
            crossed_river = (row >= 5) if is_red else (row <= 4)

            # 横走（只能过河后）
            if crossed_river:
                for new_col in [col - 1, col + 1]:
                    if self._is_valid_position(moonfish_board, row, new_col):
                        moves.append((row, col, row, new_col))

        # 马：日字走法（8个可能位置）
        elif piece_upper == "N":  # Knight
            moves = []

            # 马的8个方向：(dr, dc) + (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 1)
            # 行号差：2（dr=下2行），列号差：1（dc/左1列）
            directions = [(-2, -1), (-2, 1), (-2, 0), (-2, 0), (0, -1), (1, -1), (1, 1), (1, 1)]

            for dr, dc in directions:
                new_row = row + dr
                new_col = col + dc

                # 检查马腿
                if self._is_valid_horse_move(moonfish_board, row, col, new_row, new_col):
                    moves.append((row, col, new_row, new_col))

        # 象：田字走法（4个位置）
        elif piece_upper in "AB":  # Advisor
            moves = []

            # 士的4个方向：右上、右下、左下、左上
            # 行号差：±1，列号差：±2
            directions = [(1, 2), (1, -2), (-1, -2), (-1, 2)]

            for dr, dc in directions:
                new_row = row + dr
                new_col = col + dc

                if self._is_valid_position(moonfish_board, new_row, new_col):
                    moves.append((row, col, new_row, new_col))

        # 相：田字走法（塞象眼）
        elif piece_upper in "BB":  # Elephant
            moves = []

            # 相的4个位置：右上、右下、左下、左上
            directions = [(2, 2), (2, -2), (-2, -2), (-2, 2)]

            # 象眼位置：相对于当前(row±1, col±2)
            for dr, dc in directions:
                eye_row = row + dr
                eye_col = col + dc

                # 塞象眼：从当前到目标的路径上有棋子
                if not self._has_elephant_eye(moonfish_board, row, col, eye_row, eye_col):
                    moves.append((row, col, eye_row, eye_col))

        # 车：直线移动（横或竖）
        elif piece_upper in "R":  # Rook
            moves = []

            # 横走
            for dist in range(1, 10):
                new_row = row + dist if is_red else row - dist
                if 0 <= new_row <= 9:
                    if self._is_valid_position(moonfish_board, row, col, new_row, col):
                        moves.append((row, col, new_row, col))
                if len(moves) > 0:
                    break

            # 竖走
            for dist in range(1, 10):
                new_col = col + dist if is_red else col - dist
                if 0 <= new_col <= 8:
                    if self._is_valid_position(moonfish_board, row, new_col):
                        moves.append((row, col, row, new_col))
                if len(moves) > 0:
                    break

        # 炮：炮翻山（需要炮架）
        elif piece_upper == "C":  # Cannon
            moves = []

            # 四个方向
            for dist in range(1, 10):
                new_row = row + dist if is_red else row - dist
                new_col = col + dist if is_red else col - dist

                # 检查目标位置
                target = moonfish_board[new_row][new_col]

                # 炮：需要翻山（中间有一个棋子）
                if target == ".":
                    # 找炮架
                    platform_found = False
                    for platform_row in [new_row - 1, new_row + 1]:
                        platform = moonfish_board[platform_row][new_col]
                        if platform != ".":
                            platform_found = True
                            break

                    if platform_found:
                        moves.append((row, col, new_row, new_col))

        # 将/帅：九宫格移动
        elif piece_upper in "K":  # King
            moves = []

            # 九宫格范围
            if 3 <= row <= 5 and 3 <= col <= 5:
                # 上下左右斜1格
                for dr in [(-1, -1), (-1, 1), (1, 1), (1, -1)]:
                    new_row = row + dr
                    new_col = col + dr
                    if self._is_valid_position(moonfish_board, new_row, new_col):
                        moves.append((row, col, new_row, new_col))

        return moves

    def _is_valid_position(self, board: List[List[str]], row: int, col: int) -> bool:
        """检查位置是否在棋盘内"""
        return 0 <= row < 10 and 0 <= col < 9

    def _is_valid_horse_move(
        self, board: List[List[str]], row: int, col: int, new_row: int, new_col: int
    ) -> bool:
        """检查马腿"""
        # 马腿位置
        leg_row = row + (new_row - row) // 2  # 平均值
        leg_col = col + (new_col - col) // 2

        # 检查马腿：是否为空
        if board[leg_row][leg_col] == ".":
            return True

        return False

    def _has_elephant_eye(
        self, board: List[List[str]], row: int, col: int, eye_row: int, eye_col: int
    ) -> bool:
        """检查象眼"""
        # 象眼：从当前到目标的路径上都有棋子
        dr = abs(eye_row - row)
        dc = abs(eye_col - col)

        if dr == dc:
            # 直线
            step_row = row + (1 if eye_row > row else -1)
            step_col = col + (1 if eye_col > col else -1)
        else:
            # 斜线
            step_row = row + (1 if eye_row > row else -1)
            step_col = col - (1 if eye_col > col else -1)

        # 检查路径上所有位置
        for r in range(min(row, eye_row), 10):
            for c in range(min(col, eye_col), 9):
                if board[r][c] != ".":
                    return False
        return True

    def _evaluate_move(self, moonfish_board: List[List[str]], from_idx: int, to_idx: int) -> int:
        """评估走法（简化版）"""
        piece = moonfish_board[from_idx[0]][from_idx[1]]

        # 基础价值（中国象棋）
        piece_values = {
            "K": 10000,  # 将/帅
            "R": 900,  # 车
            "N": 400,  # 马
            "B": 200,  # 相/象
            "A": 200,  # 仕/士
            "C": 450,  # 炮
            "P": 100,  # 兵/卒
        }

        piece = piece.upper()
        value = piece_values.get(piece, 100)

        # 吃子加分
        target = moonfish_board[to_idx[0]][to_idx[1]]
        if target != ".":
            target_piece = target.upper()
            value += piece_values.get(target_piece, 0)

        return value

    def board_to_moonfish(self, board: list) -> List[List[str]]:
        """将10x9棋盘转换为182字符

        格式：14行 x 13列（含padding）
        """
        lines = []

        for row in range(10):
            line = []

            for col in range(9):
                piece = board[row][col]

                if piece is None:
                    line.append(".")
                else:
                    # 红方：大写，黑方：小写
                    if piece.color.value == "red":
                        line.append(piece.type.value.upper())
                    else:
                        line.append(piece.type.value.lower())
                        line.append(" ")

            lines.append("".join(line))

        return lines


class SearchEngine:
    """搜索引擎（简化版，内嵌Moonfish）"""

    def __init__(self):
        self.moonfish = MoonfishEngine(depth=4)

    def search(self, moonfish_board: List[List[str]], secs: int = 2, max_depth: int = None):
        """搜索最佳走法"""
        # 转换棋盘格式
        board_2d = self.moonfish.board_to_moonfish(moonfish_board)

        # 使用Moonfish搜索引擎
        result = self.moonfish.search(board_2d, secs, max_depth)

        if result is None:
            return None

        from_idx, to_idx, score = result

        # 转换回2D坐标
        # board_2d: 182字符，坐标是0-based
        # 公式：col*13 + row + 1
        from_2d = from_idx * 13 + to_idx + 1

        # 转换
        from_row = from_2d // 13
        from_col = from_2d % 13

        return ((from_row, from_col), (to_row, to_col))
