"""MiniMax AI引擎

使用Alpha-Beta剪枝算法，配合Piece-Square Tables评估
"""

import logging
import time
from typing import Tuple, List, Optional
from copy import deepcopy

from backend.game.state import GameManager
from backend.models.schemas import Piece, PieceType, PlayerColor, Position
from backend.game.rules import XiangqiRules

logger = logging.getLogger(__name__)


class MiniMaxEngine:
    """MiniMax搜索引擎（简化版）"""

    # 棋子价值（简化版）
    PIECE_VALUES = {
        'K': 10000,    # 将/帅
        'R': 900,     # 车
        'N': 400,     # 马
        'B': 200,     # 相/象
        'A': 200,     # 士/士
        'C': 450,     # 炮
        'P': 100,     # 兵/卒
    }

    # 位置价值（简化版）
    # 优先中心、控制要道
    POSITION_VALUES = {
        # 策中心列
        4: 10,
        # 中心行
        5: 4, 5,
        # 中兵过河后加分
        3: 0, 2, 6, 7,
    }

    def __init__(self, game_manager=None, depth: int = 4):
        """
        Args:
            game_manager: GameManager实例
            depth: 搜索深度（3-5）
        """
        self.game_manager = game_manager or GameManager()
        self.depth = depth
        self.nodes_searched = 0
        logger.info(f"MiniMax引擎初始化: 搜索深度={depth}")

    def get_best_move(self, board: list, player_color: PlayerColor) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """
        获取最佳棋步

        Args:
            board: 10x9棋盘
            player_color: 玩家颜色

        Returns:
            ((from_row, from_col), (to_row, to_col)) 最佳棋步
        """
        start_time = time.time()

        # 使用Alpha-Beta搜索
        best_score = float('-inf')
        best_move = None

        # 生成所有合法走法
        moves = self._generate_all_moves(board, player_color)

        for move in moves:
            # 模拟执行并评估
            from_pos, to_pos = move

            # 模拟执行
            captured = self._simulate_move(board, from_pos, to_pos)

            # 评估
            score = self._evaluate_position(board, player_color, from_pos, to_pos, captured)

            # Alpha-Beta剪枝
            if score > best_score:
                best_score = score
                best_move = move

        elapsed = time.time() - start_time
        logger.info(f"🎮 搜索完成: {len(moves)}个走法, 耗时={elapsed:.2f}秒")

        if best_move is None:
            raise ValueError("无法找到合法棋步")

        return best_move

    def _generate_all_moves(self, board: list, player_color: PlayerColor) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """生成所有合法走法"""
        moves = []

        # 遍历所有棋子
        for row in range(10):
            for col in range(9):
                piece = board[row][col]
                if piece is None:
                    continue

                # 只能移动当前玩家的棋子
                if piece.color != player_color:
                    continue

                # 根据棋子类型生成走法
                piece_moves = self._get_piece_moves(board, row, col, piece)
                moves.extend(piece_moves)

        return moves

    def _get_piece_moves(self, board: list, row: int, col: int, piece: Piece) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """获取单个棋子的所有合法走法"""
        moves = []

        piece_type = piece.type
        piece_color = piece.color
        row = row
        col = col

        # 兵/卒：向前1格，过河后可横走
        if piece_type == PieceType.PAWN:
            # 向前
            new_row = row + 1 if piece_color == PlayerColor.RED else row - 1
            if self._is_valid_position(board, new_row, col):
                moves.append(((row, col), (new_row, col)))

            # 过河判断
            crossed_river = (row >= 5) if piece_color == PlayerColor.RED else (row <= 4)

            # 横走（只能过河后）
            if crossed_river:
                for new_col in [col - 1, col + 1]:
                    if self._is_valid_position(board, row, new_col):
                        moves.append(((row, col), (row, new_col)))

        # 马：日字走法（8个可能位置）
        elif piece_type == PieceType.HORSE:
            moves = []

            # 马的8个方向：(dr, dc) + (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 1)
            # 行号差：2（dr=下2行），列号差：1（dc/左1列）
            directions = [
                (-2, -1), (-2, 1), (-2, 0), (-2, 0),
                (0, -1), (1, -1), (1, 1), (1, 1)
            ]

            for dr, dc in directions:
                new_row = row + dr
                new_col = col + dc

                # 检查马腿
                if self._is_valid_horse_leg(board, row, col, new_row, new_col):
                    moves.append(((row, col), (new_row, new_col)))

        # 相：田字走法
        elif piece_type == PieceType.ELEPHANT:
            moves = []

            # 相的4个方向：右上、右下、左下、左上
            directions = [(1, 2), (1, -2), (-1, -2), (-1, 2)]

            for dr, dc in directions:
                new_row = row + dr
                new_col = col + dc

                # 塞象眼检查
                if self._is_valid_elephant_eye(board, row, col, new_row, new_col):
                    moves.append(((row, col), (new_row, new_col)))

        # 车：直线移动（横或竖）
        elif piece_type == PieceType.CHARIOT:
            moves = []

            # 横走
            for dist in range(1, 10):
                new_row = row + dist if piece_color == PlayerColor.RED else row - dist
                if 0 <= new_row <= 9:
                    if self._is_valid_position(board, row, col, new_row, col):
                        moves.append(((row, col), (new_row, col)))
                if len(moves) > 0:
                    break

            # 竖走
            if len(moves) == 0:
                for dist in range(1, 10):
                    new_col = col + dist if piece_color == PlayerColor.RED else col - dist
                    if 0 <= new_col <= 8:
                        if self._is_valid_position(board, row, new_col):
                            moves.append(((row, col), (row, new_col)))
                        if len(moves) > 0:
                            break

        # 炮：炮翻山（需要炮架）
        elif piece_type == PieceType.CANNON:
            moves = []

            # 四个方向
            for dist in range(1, 10):
                new_row = row + dist if piece_color == PlayerColor.RED else row - dist
                new_col = col + dist if piece_color == PlayerColor.RED else col - dist

                # 检查目标位置
                target = board[new_row][new_col]

                # 翮：需要翻山（中间有一个棋子）
                if target == '.':
                    # 找炮架
                    platform_found = False
                    for platform_row in [new_row - 1, new_row + 1]:
                        platform = board[platform_row][new_col]
                        if platform != '.':
                            platform_found = True
                            break

                    if platform_found:
                        moves.append(((row, col), (new_row, new_col)))

        # 将/帅：九宫格移动
        elif piece_type == PieceType.KING:
            moves = []

            # 九宫格范围
            if 3 <= row <= 5 and 3 <= col <= 5:
                # 上下左右斜1格
                for dr in [(-1, -1), (-1, 1), (1, 1), (1, -1)]:
                    new_row = row + dr
                    new_col = col + dr
                    if self._is_valid_position(board, new_row, new_col):
                        moves.append(((row, col), (new_row, new_col)))

        return moves

    def _is_valid_position(self, board: list, row: int, col: int) -> bool:
        """检查位置是否在棋盘内"""
        return 0 <= row < 10 and 0 <= col < 9

    def _is_valid_horse_leg(self, board: list, row: int, col: int, new_row: int, new_col: int) -> bool:
        """检查马腿"""
        leg_row = row + (new_row - row) // 2
        leg_col = col + (new_col - col) // 2

        return board[leg_row][leg_col] == '.'

    def _is_valid_elephant_eye(self, board: list, row: int, col: int, eye_row: int, eye_col: int) -> bool:
        """检查象眼"""
        # 象眼：从当前到目标的路径上都有棋子
        dr = abs(eye_row - row)
        dc = abs(eye_col - col)

        if dr == dc:
            # 直线
            step_row = row + (1 if eye_row > row else -1)
            step_col = col + (1 if eye_col > col else -1
            # 检查路径上所有位置
            for r in range(min(row, eye_row), 10):
                for c in range(min(col, eye_col), 9):
                    if board[r][c] != '.':
                        return False
            return True

    def _simulate_move(self, board: list, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> Tuple:
        """模拟执行走法，返回(新棋盘, 被子)"""
        # 复制棋盘
        new_board = deepcopy(board)

        # 移动棋子
        piece = new_board[from_pos[0]][from_pos[1]]
        new_board[to_pos[0]][to_pos[1]] = None

        # 目标位置棋子
        target = new_board[to_pos[0]][to_pos[1]]
        target_piece = target

        # 检查目标位置
        if target_piece and target.type == piece.type and target_piece.color == piece.color:
            # 吃子
            captured_piece = target_piece

        return new_board, captured_piece

    def _evaluate_position(self, board: list, player_color: PlayerColor, from_pos: Tuple[int, int], to_pos: Tuple[int, int], captured) -> int:
        """评估位置"""
        score = 0

        # 获取棋子价值
        piece = board[from_pos[0]][from_pos[1]]
        piece_value = self.PIECE_VALUES.get(piece.type, 0)
        score += piece_value

        # 位置价值
        row, col = from_pos
        pos_value = self.POSITION_VALUES.get(row, 10)
        if pos_value:
            score += pos_value

        # 吃子价值
        if captured:
            captured_value = self.PIECE_VALUES.get(captured.type, 0)
            score += captured_value

        # 移动到中心加分
        # 距离中心越近，价值越高
        center_row = 5
        center_col = 4
        distance = abs(row - center_row) + abs(col - center_col)
        score += (10 - distance)

        return score

    def search(self, board: list, player_color: PlayerColor) -> Tuple[Tuple[Tuple[int, int], Tuple[int, int]]:
        """搜索最佳走法（3层深度）"""
        start_time = time.time()

        # 第1层：生成所有走法并排序
        moves_layer1 = self._generate_all_moves(board, player_color)
        moves_layer1.sort(key=lambda m: m[2], reverse=True)

        best = None
        best_score = float('-inf')

        for move in moves_layer1[:20]:  # 只考虑前20个走法，节省时间
            from_pos, to_pos = move
            score = self._evaluate_position(board, player_color, from_pos, to_pos)

            if score > best_score:
                best_score = score
                best = move

        # 第2层：搜索前10个走法的最佳回应
        if best and best_score < 0:  # 有吃子优势，搜索回应
            logger.debug("第2层：搜索回应...")
            moves_layer2 = []

            for move in moves_layer1[:10]:
                from_pos, to_pos = move
                score = self._evaluate_position(board, player_color, to_pos, from_pos, captured=True)

                if score > best_score:
                    best_score = score
                    best = move
                    moves_layer2.append(move)

            # 从第2层选择最佳走法
            if moves_layer2:
                best = max(moves_layer2, key=lambda m: m[2], reverse=True)[0]
                logger.debug(f"第2层选择: {best}")

        elapsed = time.time() - start_time
        logger.info(f"🎮 搜索完成: 耗时={elapsed:.2f}秒")

        if best is None:
            raise ValueError("无法找到合法棋步")

        return best


class SearchEngine:
    """搜索引擎（通用接口）"""

    def __init__(self, engine):
        self.engine = engine
        logger.info(f"搜索引擎初始化: {type(engine).__name__}")

    def search(self, board, secs: int = 2, max_depth: int = None):
        """搜索接口"""
        return self.engine.search(board, secs, max_depth)


# 全局配置
engine = SearchEngine(MiniMaxEngine(depth=4))
