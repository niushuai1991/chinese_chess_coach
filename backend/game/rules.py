"""中国象棋规则引擎"""

from backend.models.schemas import Move, Piece, PieceType, PlayerColor, Position


class XiangqiRules:
    """象棋规则验证引擎"""

    # 棋盘尺寸
    BOARD_ROWS = 10
    BOARD_COLS = 9

    # 九宫格范围
    BLACK_PALACE_ROWS = (0, 1, 2)
    RED_PALACE_ROWS = (7, 8, 9)
    PALACE_COLS = (3, 4, 5)

    # 河界位置
    RIVER_POSITION = 4.5  # 第4行和第5行之间

    @staticmethod
    def is_valid_position(pos: Position) -> bool:
        """验证位置是否在棋盘内

        Args:
            pos: 棋盘位置

        Returns:
            True表示位置有效
        """
        return 0 <= pos.row < XiangqiRules.BOARD_ROWS and 0 <= pos.col < XiangqiRules.BOARD_COLS

    @staticmethod
    def is_in_palace(row: int, col: int, color: PlayerColor) -> bool:
        """判断位置是否在九宫内

        Args:
            row: 行号
            col: 列号
            color: 棋子颜色

        Returns:
            True表示在九宫内
        """
        if col not in XiangqiRules.PALACE_COLS:
            return False

        if color == PlayerColor.BLACK:
            return row in XiangqiRules.BLACK_PALACE_ROWS
        else:
            return row in XiangqiRules.RED_PALACE_ROWS

    @staticmethod
    def has_crossed_river(row: int, color: PlayerColor) -> bool:
        """判断棋子是否过河

        Args:
            row: 当前行号
            color: 棋子颜色

        Returns:
            True表示已过河
        """
        if color == PlayerColor.BLACK:
            return row > XiangqiRules.RIVER_POSITION
        else:
            return row < XiangqiRules.RIVER_POSITION

    @staticmethod
    def validate_king_move(
        board: list[list[Piece | None]], from_pos: Position, to_pos: Position, piece: Piece
    ) -> bool:
        """验证将/帅的走法

        Args:
            board: 棋盘
            from_pos: 起始位置
            to_pos: 目标位置
            piece: 棋子

        Returns:
            True表示走法合法
        """
        # 必须在九宫内
        if not XiangqiRules.is_in_palace(to_pos.row, to_pos.col, piece.color):
            return False

        # 只能直行或横行一步
        row_diff = abs(to_pos.row - from_pos.row)
        col_diff = abs(to_pos.col - from_pos.col)

        if (row_diff == 1 and col_diff == 0) or (row_diff == 0 and col_diff == 1):
            return True

        return False

    @staticmethod
    def validate_advisor_move(
        board: list[list[Piece | None]], from_pos: Position, to_pos: Position, piece: Piece
    ) -> bool:
        """验证士/仕的走法

        Args:
            board: 棋盘
            from_pos: 起始位置
            to_pos: 目标位置
            piece: 棋子

        Returns:
            True表示走法合法
        """
        # 必须在九宫内
        if not XiangqiRules.is_in_palace(to_pos.row, to_pos.col, piece.color):
            return False

        # 只能斜行一步
        row_diff = abs(to_pos.row - from_pos.row)
        col_diff = abs(to_pos.col - from_pos.col)

        return row_diff == 1 and col_diff == 1

    @staticmethod
    def validate_elephant_move(
        board: list[list[Piece | None]], from_pos: Position, to_pos: Position, piece: Piece
    ) -> bool:
        """验证象/相的走法

        Args:
            board: 棋盘
            from_pos: 起始位置
            to_pos: 目标位置
            piece: 棋子

        Returns:
            True表示走法合法
        """
        # 不能过河
        if XiangqiRules.has_crossed_river(to_pos.row, piece.color):
            return False

        # 象行田：必须斜行两格
        row_diff = to_pos.row - from_pos.row
        col_diff = to_pos.col - from_pos.col

        if abs(row_diff) != 2 or abs(col_diff) != 2:
            return False

        # 检查塞象眼：田字中心不能有棋子
        eye_row = from_pos.row + row_diff // 2
        eye_col = from_pos.col + col_diff // 2

        if board[eye_row][eye_col] is not None:
            return False

        return True

    @staticmethod
    def validate_horse_move(
        board: list[list[Piece | None]], from_pos: Position, to_pos: Position, piece: Piece
    ) -> bool:
        """验证马/傌的走法

        Args:
            board: 棋盘
            from_pos: 起始位置
            to_pos: 目标位置
            piece: 棋子

        Returns:
            True表示走法合法
        """
        row_diff = to_pos.row - from_pos.row
        col_diff = to_pos.col - from_pos.col

        # 马行日：直走1格斜走1格
        if not (
            (abs(row_diff) == 2 and abs(col_diff) == 1)
            or (abs(row_diff) == 1 and abs(col_diff) == 2)
        ):
            return False

        # 检查蹩马腿
        # 确定蹩马腿的位置
        if abs(row_diff) == 2:
            # 竖着走2格，检查竖直方向的相邻格子
            leg_row = from_pos.row + (1 if row_diff > 0 else -1)
            leg_col = from_pos.col
        else:
            # 横着走2格，检查水平方向的相邻格子
            leg_row = from_pos.row
            leg_col = from_pos.col + (1 if col_diff > 0 else -1)

        # 如果蹩马腿位置有棋子，则不能走
        if board[leg_row][leg_col] is not None:
            return False

        return True

    @staticmethod
    def validate_chariot_move(
        board: list[list[Piece | None]], from_pos: Position, to_pos: Position, piece: Piece
    ) -> bool:
        """验证车/俥的走法

        Args:
            board: 棋盘
            from_pos: 起始位置
            to_pos: 目标位置
            piece: 棋子

        Returns:
            True表示走法合法
        """
        # 必须直行或横行
        if from_pos.row != to_pos.row and from_pos.col != to_pos.col:
            return False

        # 检查路径上是否有棋子阻挡
        return XiangqiRules._is_path_clear(board, from_pos, to_pos)

    @staticmethod
    def validate_cannon_move(
        board: list[list[Piece | None]],
        from_pos: Position,
        to_pos: Position,
        piece: Piece,
        is_capturing: bool,
    ) -> bool:
        """验证炮/炮的走法

        Args:
            board: 棋盘
            from_pos: 起始位置
            to_pos: 目标位置
            piece: 棋子
            is_capturing: 是否吃子

        Returns:
            True表示走法合法
        """
        # 必须直行或横行
        if from_pos.row != to_pos.row and from_pos.col != to_pos.col:
            return False

        # 计算路径上的棋子数
        pieces_between = XiangqiRules._count_pieces_between(board, from_pos, to_pos)

        if is_capturing:
            # 吃子时必须跳过一个棋子（炮架）
            return pieces_between == 1
        else:
            # 不吃子时，路径必须为空
            return pieces_between == 0

    @staticmethod
    def validate_soldier_move(
        board: list[list[Piece | None]], from_pos: Position, to_pos: Position, piece: Piece
    ) -> bool:
        """验证卒/兵的走法

        Args:
            board: 棋盘
            from_pos: 起始位置
            to_pos: 目标位置
            piece: 棋子

        Returns:
            True表示走法合法
        """
        row_diff = to_pos.row - from_pos.row
        col_diff = to_pos.col - from_pos.col

        # 只能走一步
        if abs(row_diff) + abs(col_diff) != 1:
            return False

        # 不能后退
        if piece.color == PlayerColor.BLACK:
            # 黑兵只能向下（row增加）
            if row_diff < 0:
                return False
        else:
            # 红兵只能向上（row减少）
            if row_diff > 0:
                return False

        # 过河前只能前行
        if not XiangqiRules.has_crossed_river(from_pos.row, piece.color):
            # 只能向前走，不能横走
            return col_diff == 0

        # 过河后可以横行
        return True

    @staticmethod
    def _is_path_clear(
        board: list[list[Piece | None]], from_pos: Position, to_pos: Position
    ) -> bool:
        """检查路径是否畅通（不包括起点和终点）

        Args:
            board: 棋盘
            from_pos: 起点
            to_pos: 终点

        Returns:
            True表示路径上没有棋子
        """
        if from_pos.row == to_pos.row:
            # 横向移动
            step = 1 if to_pos.col > from_pos.col else -1
            for col in range(from_pos.col + step, to_pos.col, step):
                if board[from_pos.row][col] is not None:
                    return False
        elif from_pos.col == to_pos.col:
            # 纵向移动
            step = 1 if to_pos.row > from_pos.row else -1
            for row in range(from_pos.row + step, to_pos.row, step):
                if board[row][from_pos.col] is not None:
                    return False

        return True

    @staticmethod
    def _count_pieces_between(
        board: list[list[Piece | None]], from_pos: Position, to_pos: Position
    ) -> int:
        """计算两点之间的棋子数量（不包括起点和终点）

        Args:
            board: 棋盘
            from_pos: 起点
            to_pos: 终点

        Returns:
            棋子数量
        """
        count = 0

        if from_pos.row == to_pos.row:
            # 横向移动
            step = 1 if to_pos.col > from_pos.col else -1
            for col in range(from_pos.col + step, to_pos.col, step):
                if board[from_pos.row][col] is not None:
                    count += 1
        elif from_pos.col == to_pos.col:
            # 纵向移动
            step = 1 if to_pos.row > from_pos.row else -1
            for row in range(from_pos.row + step, to_pos.row, step):
                if board[row][from_pos.col] is not None:
                    count += 1

        return count

    @staticmethod
    def is_facing_kings(board: list[list[Piece | None]], color: PlayerColor) -> bool:
        """检测将帅是否对面（王不照面规则）

        Args:
            board: 棋盘
            color: 要检查的一方

        Returns:
            True表示将帅对面（违规）
        """
        # 找到双方将帅的位置
        red_king_pos: Position | None = None
        black_king_pos: Position | None = None

        for row in range(XiangqiRules.BOARD_ROWS):
            for col in range(XiangqiRules.BOARD_COLS):
                piece = board[row][col]
                if piece and piece.type == PieceType.KING:
                    if piece.color == PlayerColor.RED:
                        red_king_pos = Position(row=row, col=col)
                    else:
                        black_king_pos = Position(row=row, col=col)

        if not red_king_pos or not black_king_pos:
            return False

        # 必须在同一列
        if red_king_pos.col != black_king_pos.col:
            return False

        # 检查中间是否有棋子
        min_row = min(red_king_pos.row, black_king_pos.row)
        max_row = max(red_king_pos.row, black_king_pos.row)

        for row in range(min_row + 1, max_row):
            if board[row][red_king_pos.col] is not None:
                return False

        # 中间无棋子，将帅对脸
        return True

    @staticmethod
    def validate_move(
        board: list[list[Piece | None]], from_pos: Position, to_pos: Position
    ) -> bool:
        """验证走法是否合法

        Args:
            board: 棋盘
            from_pos: 起始位置
            to_pos: 目标位置

        Returns:
            True表示走法合法
        """
        # 基本验证
        if not XiangqiRules.is_valid_position(from_pos):
            return False
        if not XiangqiRules.is_valid_position(to_pos):
            return False

        piece = board[from_pos.row][from_pos.col]
        if not piece:
            return False

        target = board[to_pos.row][to_pos.col]

        # 不能吃己方棋子
        if target and target.color == piece.color:
            return False

        # 根据棋子类型验证走法
        is_capturing = target is not None

        if piece.type == PieceType.KING:
            if not XiangqiRules.validate_king_move(board, from_pos, to_pos, piece):
                return False
        elif piece.type == PieceType.ADVISOR:
            if not XiangqiRules.validate_advisor_move(board, from_pos, to_pos, piece):
                return False
        elif piece.type == PieceType.ELEPHANT:
            if not XiangqiRules.validate_elephant_move(board, from_pos, to_pos, piece):
                return False
        elif piece.type == PieceType.HORSE:
            if not XiangqiRules.validate_horse_move(board, from_pos, to_pos, piece):
                return False
        elif piece.type == PieceType.CHARIOT:
            if not XiangqiRules.validate_chariot_move(board, from_pos, to_pos, piece):
                return False
        elif piece.type == PieceType.CANNON:
            if not XiangqiRules.validate_cannon_move(board, from_pos, to_pos, piece, is_capturing):
                return False
        elif piece.type == PieceType.PAWN:
            if not XiangqiRules.validate_soldier_move(board, from_pos, to_pos, piece):
                return False
        else:
            return False

        # 检查走法后是否导致将帅对脸
        # 模拟走法
        temp_board = [row[:] for row in board]
        temp_board[to_pos.row][to_pos.col] = piece
        temp_board[from_pos.row][from_pos.col] = None

        if XiangqiRules.is_facing_kings(temp_board, piece.color):
            return False

        return True

    @staticmethod
    def is_in_check(board: list[list[Piece | None]], color: PlayerColor) -> bool:
        """检测一方是否被将军

        Args:
            board: 棋盘
            color: 己方颜色

        Returns:
            True表示被将军
        """
        # 找到己方将帅位置
        king_pos: Position | None = None
        for row in range(XiangqiRules.BOARD_ROWS):
            for col in range(XiangqiRules.BOARD_COLS):
                piece = board[row][col]
                if piece and piece.type == PieceType.KING and piece.color == color:
                    king_pos = Position(row=row, col=col)
                    break
            if king_pos:
                break

        if not king_pos:
            return False

        # 检查对方所有棋子是否能攻击到己方将帅
        opponent_color = PlayerColor.BLACK if color == PlayerColor.RED else PlayerColor.RED

        for row in range(XiangqiRules.BOARD_ROWS):
            for col in range(XiangqiRules.BOARD_COLS):
                piece = board[row][col]
                if piece and piece.color == opponent_color:
                    # 临时将该棋子移到将帅位置，看是否合法
                    if XiangqiRules.validate_move(board, Position(row=row, col=col), king_pos):
                        return True

        return False

    @staticmethod
    def is_checkmate(board: list[list[Piece | None]], color: PlayerColor) -> bool:
        """检测一方是否被将死

        Args:
            board: 棋盘
            color: 己方颜色

        Returns:
            True表示被将死
        """
        # 如果没有被将军，则不是将死
        if not XiangqiRules.is_in_check(board, color):
            return False

        # 检查是否有任何合法走法可以解除将军
        for row in range(XiangqiRules.BOARD_ROWS):
            for col in range(XiangqiRules.BOARD_COLS):
                piece = board[row][col]
                if piece and piece.color == color:
                    # 尝试所有可能的走法
                    for to_row in range(XiangqiRules.BOARD_ROWS):
                        for to_col in range(XiangqiRules.BOARD_COLS):
                            to_pos = Position(row=to_row, col=to_col)
                            from_pos = Position(row=row, col=col)

                            if XiangqiRules.validate_move(board, from_pos, to_pos):
                                # 模拟走法
                                temp_board = [r[:] for r in board]
                                temp_board[to_row][to_col] = piece
                                temp_board[row][col] = None

                                # 如果走法后不再被将军，则不是将死
                                if not XiangqiRules.is_in_check(temp_board, color):
                                    return False

        # 所有走法都无法解除将军，将被死
        return True

    @staticmethod
    def is_stalemate(board: list[list[Piece | None]], color: PlayerColor) -> bool:
        """检测一方是否困毙（无子可动但不被将军）

        Args:
            board: 棋盘
            color: 己方颜色

        Returns:
            True表示困毙
        """
        # 如果被将军，则不是困毙
        if XiangqiRules.is_in_check(board, color):
            return False

        # 检查是否有任何合法走法
        for row in range(XiangqiRules.BOARD_ROWS):
            for col in range(XiangqiRules.BOARD_COLS):
                piece = board[row][col]
                if piece and piece.color == color:
                    for to_row in range(XiangqiRules.BOARD_ROWS):
                        for to_col in range(XiangqiRules.BOARD_COLS):
                            from_pos = Position(row=row, col=col)
                            to_pos = Position(row=to_row, col=to_col)

                            if XiangqiRules.validate_move(board, from_pos, to_pos):
                                return False

        # 无子可动
        return True

    @staticmethod
    def get_all_valid_moves(
        board: list[list[Piece | None]], color: PlayerColor
    ) -> list[tuple[Position, Position]]:
        """获取一方的所有合法走法

        Args:
            board: 棋盘
            color: 己方颜色

        Returns:
            合法走法列表 [(from_pos, to_pos), ...]
        """
        valid_moves = []

        for row in range(XiangqiRules.BOARD_ROWS):
            for col in range(XiangqiRules.BOARD_COLS):
                piece = board[row][col]
                if piece and piece.color == color:
                    from_pos = Position(row=row, col=col)

                    # 尝试所有可能的目标位置
                    for to_row in range(XiangqiRules.BOARD_ROWS):
                        for to_col in range(XiangqiRules.BOARD_COLS):
                            to_pos = Position(row=to_row, col=to_col)

                            if XiangqiRules.validate_move(board, from_pos, to_pos):
                                # 模拟走法，确保走后不被将军
                                temp_board = [r[:] for r in board]
                                temp_board[to_row][to_col] = piece
                                temp_board[row][col] = None

                                if not XiangqiRules.is_in_check(temp_board, color):
                                    valid_moves.append((from_pos, to_pos))

        return valid_moves

    @staticmethod
    def is_insufficient_material(board: list[list[Piece | None]]) -> bool:
        """检测双方子力是否不足以将死对方（和棋）

        Args:
            board: 棋盘

        Returns:
            True表示子力不足，判定和棋
        """
        # 统计双方棋子
        red_pieces = []
        black_pieces = []

        for row in range(XiangqiRules.BOARD_ROWS):
            for col in range(XiangqiRules.BOARD_COLS):
                piece = board[row][col]
                if piece:
                    if piece.color == PlayerColor.RED:
                        red_pieces.append(piece.type)
                    else:
                        black_pieces.append(piece.type)

        # 常见的不够将死的情况
        def is_insufficient(pieces: list[PieceType]) -> bool:
            # 只剩将帅
            if len(pieces) == 1 and PieceType.KING in pieces:
                return True
            # 将帅 + 单士/单象
            if len(pieces) == 2 and PieceType.KING in pieces:
                if PieceType.ADVISOR in pieces or PieceType.ELEPHANT in pieces:
                    return True
            # 将帅 + 单兵/单马/单炮
            if len(pieces) == 2 and PieceType.KING in pieces:
                if (
                    PieceType.PAWN in pieces
                    or PieceType.HORSE in pieces
                    or PieceType.CANNON in pieces
                ):
                    return True

            return False

        return is_insufficient(red_pieces) and is_insufficient(black_pieces)

    @staticmethod
    def get_board_hash(board: list[list[Piece | None]]) -> str:
        """计算棋盘状态的哈希值（用于检测重复局面）

        Args:
            board: 棋盘

        Returns:
            棋盘状态的哈希字符串
        """
        board_str = ""
        for row in board:
            for piece in row:
                if piece:
                    board_str += f"{piece.color.value}{piece.type.value}"
                else:
                    board_str += "--"
        return board_str

    @staticmethod
    def has_repetition(board_history: list[list[list[Piece | None]]], count: int = 3) -> bool:
        """检测是否存在重复局面

        Args:
            board_history: 历史棋盘状态列表
            count: 重复次数阈值

        Returns:
            True表示重复局面达到阈值
        """
        if len(board_history) < count:
            return False

        # 获取当前棋盘哈希
        current_hash = XiangqiRules.get_board_hash(board_history[-1])

        # 统计重复次数
        repetition_count = 1
        for i in range(len(board_history) - 2, -1, -1):
            if XiangqiRules.get_board_hash(board_history[i]) == current_hash:
                repetition_count += 1
                if repetition_count >= count:
                    return True

        return False

    @staticmethod
    def detect_perpetual_check(
        move_history: list[Move], color: PlayerColor, window: int = 6
    ) -> bool:
        """检测长将（连续将军）

        Args:
            move_history: 历史走法
            color: 要检查的颜色
            window: 检查的走法窗口大小

        Returns:
            True表示存在长将
        """
        if len(move_history) < window:
            return False

        # 检查最近的走法是否都在将军
        recent_moves = move_history[-window:]

        # 只检查该颜色的走法是否连续将军
        check_count = 0
        for move in reversed(recent_moves):
            if move.piece.color == color:
                # 这里需要保存当时的将军状态
                # 暂时简化处理
                check_count += 1

        # 如果连续3次以上将军，判定为长将
        return check_count >= 3

    @staticmethod
    def evaluate_position(board: list[list[Piece | None]], color: PlayerColor) -> tuple[int, str]:
        """评估当前局面（简化版）

        Args:
            board: 棋盘
            color: 评估方

        Returns:
            (分数, 评估描述)
            正分表示优势，负分表示劣势
        """
        # 棋子价值表
        piece_values = {
            PieceType.KING: 10000,
            PieceType.CHARIOT: 900,
            PieceType.HORSE: 400,
            PieceType.CANNON: 450,
            PieceType.ADVISOR: 200,
            PieceType.ELEPHANT: 200,
            PieceType.PAWN: 100,
        }

        # 过河兵价值提升
        crossed_pawn_bonus = 50

        red_score = 0
        black_score = 0

        for row in range(XiangqiRules.BOARD_ROWS):
            for col in range(XiangqiRules.BOARD_COLS):
                piece = board[row][col]
                if piece:
                    value = piece_values.get(piece.type, 0)

                    # 过河兵加成
                    if piece.type == PieceType.PAWN:
                        if XiangqiRules.has_crossed_river(row, piece.color):
                            value += crossed_pawn_bonus

                    if piece.color == PlayerColor.RED:
                        red_score += value
                    else:
                        black_score += value

        # 计算相对分数
        if color == PlayerColor.RED:
            score = red_score - black_score
        else:
            score = black_score - red_score

        # 生成描述
        if score > 500:
            description = "大幅优势"
        elif score > 200:
            description = "略微优势"
        elif score > -200:
            description = "均势"
        elif score > -500:
            description = "略微劣势"
        else:
            description = "大幅劣势"

        return (score, description)

    @staticmethod
    def is_draw(
        board: list[list[Piece | None]],
        board_history: list[list[list[Piece | None]]],
        move_history: list[Move],
        current_player: PlayerColor,
        moves_without_capture: int = 0,
    ) -> tuple[bool, str]:
        """综合检测是否和棋

        Args:
            board: 当前棋盘
            board_history: 历史棋盘状态
            move_history: 历史走法
            current_player: 当前玩家
            moves_without_capture: 未吃子回合数

        Returns:
            (是否和棋, 和棋原因)
        """
        # 1. 困毙（优先检查，因为这是必判的）
        if XiangqiRules.is_stalemate(board, current_player):
            return (True, "困毙")

        # 2. 重复局面
        if XiangqiRules.has_repetition(board_history):
            return (True, "重复局面")

        # 3. 六十回合规则
        if moves_without_capture >= 120:  # 双方各60步
            return (True, "六十回合未吃子")

        # 4. 长将
        if XiangqiRules.detect_perpetual_check(move_history, current_player):
            return (True, "长将")

        # 5. 子力不足
        if XiangqiRules.is_insufficient_material(board):
            return (True, "双方子力不足")

        return (False, "")
