"""Moonfish引擎核心逻辑（内嵌版本，避免类型错误）

# 直接从moonfish.py复制的核心逻辑，避免导入
# 修改为与中国象棋兼容

from typing import Tuple, List, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class MoonfishCore:
    """Moonfish引擎核心（内嵌版本）"""

    # 棋子类型映射（Moonfish国际象棋 → 中国象棋）
    PIECE_TO_XIANGQI = {
        'K': 'K',      # King → 将/帅
        'Q': 'R',      # Queen（中国象棋无，映射为车）
        'R': 'R',      # Rook → 车
        'B': 'E',      # Bishop → 相/象
        'N': 'H',      # Knight → 马
        'P': 'P',      # Pawn → 兵/卒
        '.': '.',      # Empty
    }

    XIANGQI_TO_PIECE = {
        'K': 'KING',    # 将/帅
        'R': 'CHARIOT', # 车
        'E': 'ELEPHANT', # 相/象
        'H': 'HORSE',   # 马
        'P': 'PAWN',    # 兵/卒
        '.': None,
    }

    # 棋子中文名（用于日志）
    PIECE_NAMES_CN = {
        'KING': '将',
        'CHARIOT': '车',
        'ELEPHANT': '相',
        'HORSE': '马',
        'PAWN': '兵',
    }

    def __init__(self, depth: int = 4):
        """
        Args:
            depth: 搜索深度（3-5），默认4（中等水平）
        """
        self.depth = depth
        self.max_depth = depth
        self.nodes = 0
        self.tp_score = {}
        self.tp_move = {}

        # 棋子价值（中国象棋）
        self.piece_values = {
            'KING': 10000,   # 将/帅
            'CHARIOT': 200,    # 车
            'CANNON': 120,    # 炮
            'HORSE': 100,    # 马
            'ELEPHANT': 20,     # 相/象
            'PAWN': 10,      # 兵/卒
        }

        logger.info(f"🤖 Moonfish引擎初始化: 搜索深度={depth}")

    def board_to_moonfish(self, board: list) -> str:
        """
        将10x9的中国象棋棋盘转换为Moonfish的182字符字符串

        Args:
            board: 10x9的2D数组

        Returns:
            182字符字符串（Moonfish格式）
        """
        lines = []

        # Moonfish格式：从第0行（黑方底线）到第9行（红方底线）
        for row in range(10):
            line_chars = []
            for col in range(9):
                piece = board[row][col]
                if piece is None:
                    line_chars.append('.')
                else:
                    # 中国象棋棋子类型转换为Moonfish字符
                    moon_type = MoonfishCore.PIECE_TO_XIANGQI[piece.type]
                    # 大写=红方，小写=黑方
                    char = moon_type.upper() if piece.color.value == 'red' else moon_type.lower()
                    line_chars.append(char)
            lines.append(''.join(line_chars))

        return '\n'.join(lines)

    def moonfish_to_board(self, moonfish_board: str) -> list:
        """
        将Moonfish的182字符字符串转换为10x9的中国象棋棋盘

        Args:
            moonfish_board: 182字符字符串

        Returns:
            10x9的2D数组
        """
        board = [[None for _ in range(9)] for _ in range(10)]
        lines = moonfish_board.split('\n')

        for row_idx, line in enumerate(lines):
            for col_idx, char in enumerate(line):
                if char == '.':
                    continue

                # 判断颜色（大写=红方，小写=黑方）
                is_upper = char.isupper()
                piece_type_str = char.upper()

                # 映射回中国象棋棋子类型
                piece_type = MoonfishCore.XIANGQI_TO_PIECE.get(piece_type_str)
                if piece_type is None:
                    logger.warning(f"未知棋子字符: {char} at ({row_idx}, {col_idx})")
                    continue

                # 创建棋子对象
                from backend.models.schemas import Piece, PieceType, PlayerColor
                piece = Piece(
                    type=piece_type,
                    color=PlayerColor.RED if is_upper else PlayerColor.BLACK
                )
                board[row_idx][col_idx] = piece

        return board

    def search(self, moonfish_board: str, secs: int = 2, max_depth: int = None):
        """
        Moonfish MTD-bi搜索

        Args:
            moonfish_board: 182字符字符串棋盘
            secs: 超时时间（秒）
            max_depth: 最大搜索深度

        Returns:
            最佳棋步的(from_idx, to_idx)索引
        """
        import time
        start_time = time.time()

        # 迭代加深
        depth = 1
        if max_depth is None:
            max_depth = self.max_depth

        while depth <= max_depth:
            self.nodes += 1

            # MTD-bi搜索
            score = self._bound(
                moonfish_board,
                -10000,  # alpha
                10000,    # beta
                depth
            )

            elapsed = time.time() - start_time
            if elapsed > secs:
                logger.info(f"搜索超时: {elapsed:.2f}秒，深度={depth}")
                break

            depth += 1

        return self.tp_move.get(moonfish_board)

    def _bound(self, moonfish_board: str, alpha: int, beta: int, depth: int) -> int:
        """
        Alpha-Beta剪枝搜索
        """
        # 从缓存获取
        key = (moonfish_board, depth, True)
        entry = self.tp_score.get(key)
        if entry is not None and entry.lower >= beta and entry.upper <= alpha:
            return entry.upper

        # 生成所有走法
        best = -10000
        best_move = None

        for move in self._generate_moves(moonfish_board):
            score = -self._search(move, depth - 1, -beta)
            if score > best:
                best = score
                best_move = move

        # 存储结果
        if best_move:
            self.tp_score[key] = (best, -10000)
            self.tp_move[moonfish_board] = best_move

        return best

    def _search(self, move: tuple, depth: int, beta: int) -> int:
        """
        递归搜索
        """
        from_idx, to_idx = move
        moonfish_board = self._make_move(move)

        # 获取棋子
        piece = moonfish_board[from_idx]
        if piece == '.':
            return 0  # 空格

        # 棋子价值
        is_upper = piece.isupper()
        piece_type_str = piece.upper()
        piece_type = MoonfishCore.XIANGQI_TO_PIECE[piece_type_str]
        value = self.piece_values.get(piece_type, 0)

        # 吃子价值
        target = moonfish_board[to_idx]
        if target != '.':
            target_type_str = target.upper()
            target_type = MoonfishCore.XIANGQI_TO_PIECE.get(target_type_str)
            if target_type:
                value += self.piece_values.get(target_type, 0)

        # 中国象棋规则：检查合法性
        if self._is_valid_xiangqi_move(from_idx, to_idx, piece_type, moonfish_board):
            return value

        return -value

    def _generate_moves(self, moonfish_board: str):
        """
        生成所有合法走法

        Args:
            moonfish_board: 182字符字符串棋盘

        Returns:
            生成器：(from_idx, to_idx)
        """
        for from_idx in range(182):
            piece = moonfish_board[from_idx]
            if piece == '.':
                continue

            # 判断颜色
            is_upper = piece.isupper()
            if not is_upper and not piece.islower():
                continue

            piece_type_str = piece.upper()
            piece_type = MoonfishCore.XIANGQI_TO_PIECE.get(piece_type_str)
            if piece_type is None:
                continue

            # 中国象棋棋子类型
            color = 'red' if is_upper else 'black'

            # 生成走法
            if piece_type == 'PAWN':  # 兵/卒
                # 兵的走法：向前、过河后可横走
                row = from_idx // 13  # 0-based行号
                col = from_idx % 13  # 0-based列号（0-12实际列，需要-2得到0-10）
                actual_col = col - 2 if col >= 2 else col

                # 向前
                to_idx = from_idx + 13
                if self._is_valid_position(to_idx) and self._is_empty(to_idx):
                    yield (from_idx, to_idx)

                # 过河后横走
                if row >= 5:  # 黑方过河
                    for new_col in [actual_col - 1, actual_col, actual_col + 1]:
                        to_idx = row * 13 + new_col
                        if self._is_valid_position(to_idx) and self._is_empty(to_idx):
                            yield (from_idx, to_idx)

            elif piece_type == 'CANNON':  # 炮
                # 炮的走法：直走、翻山吃子
                row = from_idx // 13
                col = from_idx % 13
                actual_col = col - 2 if col >= 2 else col

                # 直走（四个方向）
                for dr in [-13, 13, 1, -1]:
                    to_idx = from_idx + dr
                    if self._is_valid_position(to_idx) and self._is_empty(to_idx):
                        yield (from_idx, to_idx)

                # 翻山（需要炮架）
                # 简化：寻找同一直线上的两个棋子，中间有一个棋子
                for dr in [13, -13, 26, -26]:  # 横2，竖向2
                    mid_idx = from_idx + dr
                    if self._is_valid_position(mid_idx):
                        # 检查中间是否有棋子
                        if moonfish_board[mid_idx] != '.':
                            # 找到炮架
                            for jump_idx in range(from_idx + 1, from_idx + dr, 1):
                                if mid_idx < jump_idx < to_idx:
                                    target = moonfish_board[to_idx]
                                    if target != '.':
                                        # 吃子
                                        yield (from_idx, to_idx)
                                        break
                                    break

            elif piece_type == 'CHARIOT':  # 车
                # 车的走法：横走或竖走（直线）
                row = from_idx // 13
                col = from_idx % 13
                actual_col = col - 2 if col >= 2 else col

                # 横走
                for dist in range(1, 9):  # 尝试1-8格
                    to_idx = from_idx + dist
                    if self._is_valid_position(to_idx):
                        if self._is_empty(to_idx):
                            yield (from_idx, to_idx)
                    else:
                        break

                # 竖走
                for dist in range(1, 9):
                    to_idx = from_idx + dist * 13
                    if self._is_valid_position(to_idx):
                        if self._is_empty(to_idx):
                            yield (from_idx, to_idx)
                    else:
                        break

            elif piece_type == 'HORSE':  # 马
                # 马的走法：日字（优先蹩马腿）
                row = from_idx // 13
                col = from_idx % 13
                actual_col = col - 2 if col >= 2 else col

                # 马的8个可能位置（相对于当前位置）
                # 这里的索引是0-based，需要转换为Moonfish的0-based
                horse_moves = [
                    (row - 2, col - 1),   # 上左
                    (row - 2, col + 1),   # 上右
                    (row - 1, col - 2),   # 左上
                    (row - 1, col + 2),   # 右上
                    (row + 1, col - 2),   # 左下
                    (row + 1, col + 2),   # 右下
                ]

                for new_row, new_col in horse_moves:
                    to_idx = new_row * 13 + new_col
                    # 检查位置和蹩马腿
                    if self._is_valid_position(to_idx):
                        # 蹩马腿：从当前到目标位置，如果在"日"字上有棋子
                        # "日"字的四个位置
                        leg_positions = [
                            from_idx - 2 * 13 - 1,  # 上左
                            from_idx - 2 * 13 + 1,   # 上右
                            from_idx + 1 * 13 - 1,   # 左上
                            from_idx + 1 * 13 + 1,   # 右上
                        ]
                        blocked = False
                        for leg_idx in leg_positions:
                            if moonfish_board[leg_idx] != '.':
                                blocked = True
                                break

                        if not blocked:
                            yield (from_idx, to_idx)

            elif piece_type == 'ELEPHANT':  # 相/象
                # 相的走法：田字（塞象眼）
                row = from_idx // 13
                col = from_idx % 13
                actual_col = col - 2 if col >= 2 else col

                # 相的4个可能位置
                elephant_moves = [
                    (row - 2, col - 2),   # 左上
                    (row - 2, col + 2),   # 右上
                    (row + 2, col - 2),   # 左下
                    (row + 2, col + 2),   # 右下
                ]

                for new_row, new_col in elephant_moves:
                    to_idx = new_row * 13 + new_col

                    # 塞象眼：从当前到目标位置的"日"字位置
                    # "日"字的四个位置
                    eye_positions = [
                        new_row * 13 + (new_col - 1),  # 左
                        new_row * 13 + (new_col + 1),  # 右
                        new_row * 13 + new_col - 1,   # 下
                        new_row * 13 + new_col,       # 上
                    ]
                    blocked = False
                    for eye_idx in eye_positions:
                        if moonfish_board[eye_idx] != '.':
                                blocked = True
                                break

                    if not blocked:
                        # 检查是否过河
                        if is_upper:  # 红方
                            if new_row <= 4:  # 不能过河
                                yield (from_idx, to_idx)
                        else:  # 黑方
                            if new_row >= 5:  # 过河后才能飞象
                                yield (from_idx, to_idx)

            elif piece_type == 'KING':  # 将/帅
                # 将/帅的走法：九宫格内直走或斜走1格
                row = from_idx // 13
                col = from_idx % 13
                actual_col = col - 2 if col >= 2 else col

                # 九宫格范围
                if is_upper:  # 红方（7-9行，3-5列）
                    if not (7 <= row <= 9 and 3 <= col <= 5):
                        continue
                else:  # 黑方（0-2行，3-5列）
                    if not (0 <= row <= 2 and 3 <= col <= 5):
                        continue

                # 九宫格内移动（上、下、左、右、斜）
                moves_1 = [(row - 1, col), (row + 1, col)]  # 上、下
                moves_2 = [(row, col - 1), (row, col + 1)]  # 左、右

                for new_row, new_col in moves_1 + moves_2:
                    to_idx = new_row * 13 + new_col
                    if self._is_valid_position(to_idx):
                        yield (from_idx, to_idx)

        raise StopIteration

    def _make_move(self, from_idx: int, to_idx: int) -> str:
        """执行走法，返回新棋盘"""
        board = list(self._moonfish_board)
        piece = board[from_idx]
        board[to_idx] = piece
        return ''.join(board)

    def _is_valid_position(self, idx: int) -> bool:
        """检查位置是否在棋盘内"""
        return 0 <= idx < 182

    def _is_empty(self, idx: int) -> bool:
        """检查位置是否为空"""
        self._moonfish_board[idx] == '.'

    def _is_valid_xiangqi_move(self, from_idx: int, to_idx: int, piece_type: str, board: str) -> bool:
        """验证中国象棋走法合法性"""
        # 基本验证
        if not self._is_valid_position(to_idx):
            return False
        if self._is_empty(to_idx):
            return False

        # 获取棋子
        piece = board[from_idx]
        if piece == '.':
            return False

        is_upper = piece.isupper()
        color = 'red' if is_upper else 'black'

        # 转换为行列
        from_row = from_idx // 13
        from_col = (from_idx % 13) - 2
        to_row = to_idx // 13
        to_col = (to_idx % 13) - 2

        # 走棋子
        if piece_type == 'PAWN':  # 兵/卒
            # 兵向前1格
            if is_upper:  # 红方向下
                if to_row == from_row + 1 and to_col == from_col:
                    return True
            else:  # 黑方向上
                if to_row == from_row - 1 and to_col == from_col:
                    return True

            # 过河后可横走（不能后退）
            if is_upper and from_row >= 5:
                if to_row != from_row and abs(to_col - from_col) == 1:
                    return True
            elif not is_upper and from_row <= 4:
                if to_row != from_row and abs(to_col - from_col) == 1:
                    return True

        elif piece_type == 'CANNON':  # 炮
            # 炮直线移动
            if from_row == to_row:  # 横走
                return abs(to_col - from_col) <= 8
            elif from_col == to_col:  # 竖走
                return abs(to_row - from_row) <= 8

        elif piece_type == 'CHARIOT':  # 车
            # 车直线移动（横或竖）
            if from_row == to_row or from_col == to_col:
                # 检查路径上是否有阻挡
                step = 1 if to_row > from_row else -1
                dist = abs(to_row - from_row) + abs(to_col - from_col)
                for i in range(1, dist):
                    if from_row + i * step == to_row:
                        if board[from_row + i * step + from_col] != '.':
                            return False
                    if from_col + i * step == to_col:
                        if board[from_row + i * step + to_col] != '.':
                            return False
                return True

        elif piece_type == 'HORSE':  # 马
            # 马走日字
            # 检查8个位置
            moves = [
                (from_row - 2, from_col - 1),
                (from_row - 2, from_col + 1),
                (from_row - 1, from_col - 2),
                (from_row - 1, from_col + 2),
            ]

            for new_row, new_col in moves:
                # 蹩马腿检查
                leg_row = (from_row + new_row) // 2
                leg_col = (from_col + new_col) // 2
                leg_idx = leg_row * 13 + leg_col

                # 检查蹩马腿
                if board[leg_idx] != '.':
                    continue  # 被住

                yield (from_idx, new_row * 13 + new_col)

        elif piece_type == 'ELEPHANT':  # 相/象
            # 相走田字（塞象眼）
            moves = [
                (from_row - 2, from_col - 2),
                (from_row - 2, from_col + 2),
                (from_row + 2, from_col - 2),
                (from_row + 2, from_col + 2),
            ]

            for new_row, new_col in moves:
                to_idx = new_row * 13 + new_col

                # 塞象眼检查（4个位置）
                eye_row = (from_row + new_row) // 2
                eye_col = (from_col + new_col) // 2
                eye_indices = [
                    eye_row * 13 + (eye_col - 1),
                    eye_row * 13 + (eye_col + 1),
                    eye_row * 13 + eye_col,
                    eye_row * 13 + (eye_col + 1),
                ]

                blocked = False
                for eye_idx in eye_indices:
                    if board[eye_idx] != '.':
                        blocked = True
                        break

                if not blocked:
                    # 过河检查
                    piece = board[from_idx]
                    is_upper = piece.isupper()
                    if is_upper:  # 红方
                        if new_row <= 4:  # 不能过河
                            continue
                    else:  # 黑方
                        if new_row >= 5:
                            yield (from_idx, to_idx)
                    else:
                        continue

        elif piece_type == 'KING':  # 将/帅
            # 九宫格内移动
            if not (7 <= from_row <= 9 and 3 <= from_col <= 5 if is_upper else (0 <= from_row <= 2 and 3 <= from_col <= 5):
                return False

            # 基本移动：上下左右斜
            moves = [
                (from_row - 1, from_col),
                (from_row + 1, from_col),
                (from_row, from_col - 1),
                (from_row, from_col + 1),
            ]

            for new_row, new_col in moves:
                yield (from_idx, new_row * 13 + new_col)

        return False

    def evaluate_board(self, moonfish_board: str) -> int:
        """评估棋盘（简化版）"""
        score = 0
        for idx in range(182):
            piece = moonfish_board[idx]
            if piece == '.':
                continue

            is_upper = piece.isupper()
            piece_type_str = piece.upper()
            piece_type = MoonfishCore.XIANGQI_TO_PIECE.get(piece_type_str)
            if piece_type is None:
                continue

            value = self.piece_values.get(piece_type, 0)
            if is_upper:
                score += value
            else:
                score -= value

        return score

    def _moonfish_board(self) -> str:
        """获取当前Moonfish棋盘"""
        if not hasattr(self, '_moonfish_board'):
            from game.state import GameManager
            self.game_manager = GameManager()
            session_id, game_state = self.game_manager.create_game('red')
            self._moonfish_board = self.board_to_moonfish(game_state.board)
        return self._moonfish_board
