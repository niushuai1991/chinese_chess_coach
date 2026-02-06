"""中国象棋规则测试"""

import pytest

from backend.game.rules import XiangqiRules
from backend.models.schemas import Piece, PieceType, PlayerColor, Position


class TestPositionValidation:
    """位置验证测试"""

    def test_valid_positions(self):
        """测试有效位置"""
        # Position模型有内置验证，创建时已检查有效性
        assert Position(row=0, col=0)
        assert Position(row=9, col=8)
        assert Position(row=5, col=4)

    def test_position_model_validation(self):
        """测试Position模型内置验证"""
        # 测试row超出范围会抛出异常
        with pytest.raises(Exception):
            Position(row=10, col=0)

        # 测试col超出范围会抛出异常
        with pytest.raises(Exception):
            Position(row=0, col=9)


class TestPalaceValidation:
    """九宫格验证测试"""

    def test_black_king_in_palace(self):
        """测试黑将在九宫内"""
        assert XiangqiRules.is_in_palace(0, 3, PlayerColor.BLACK)
        assert XiangqiRules.is_in_palace(1, 4, PlayerColor.BLACK)
        assert XiangqiRules.is_in_palace(2, 5, PlayerColor.BLACK)

    def test_red_king_in_palace(self):
        """测试红帅在九宫内"""
        assert XiangqiRules.is_in_palace(7, 3, PlayerColor.RED)
        assert XiangqiRules.is_in_palace(8, 4, PlayerColor.RED)
        assert XiangqiRules.is_in_palace(9, 5, PlayerColor.RED)

    def test_king_outside_palace(self):
        """测试将帅在九宫外"""
        assert not XiangqiRules.is_in_palace(3, 4, PlayerColor.BLACK)
        assert not XiangqiRules.is_in_palace(6, 4, PlayerColor.RED)
        assert not XiangqiRules.is_in_palace(0, 2, PlayerColor.BLACK)
        assert not XiangqiRules.is_in_palace(0, 6, PlayerColor.BLACK)


class TestRiverCrossing:
    """过河验证测试"""

    def test_black_piece_crossed_river(self):
        """测试黑方棋子过河"""
        assert not XiangqiRules.has_crossed_river(0, PlayerColor.BLACK)
        assert not XiangqiRules.has_crossed_river(4, PlayerColor.BLACK)
        assert XiangqiRules.has_crossed_river(5, PlayerColor.BLACK)
        assert XiangqiRules.has_crossed_river(9, PlayerColor.BLACK)

    def test_red_piece_crossed_river(self):
        """测试红方棋子过河"""
        assert XiangqiRules.has_crossed_river(0, PlayerColor.RED)
        assert XiangqiRules.has_crossed_river(4, PlayerColor.RED)
        assert not XiangqiRules.has_crossed_river(5, PlayerColor.RED)
        assert not XiangqiRules.has_crossed_river(9, PlayerColor.RED)


class TestKingMovement:
    """将/帅走法测试"""

    def setup_board(self):
        """创建初始棋盘"""
        return [[None for _ in range(9)] for _ in range(10)]

    def test_king_valid_moves(self):
        """测试将/帅的合法走法"""
        board = self.setup_board()
        board[9][4] = Piece(type=PieceType.KING, color=PlayerColor.RED)

        # 前进一步
        assert XiangqiRules.validate_king_move(
            board, Position(row=9, col=4), Position(row=8, col=4), board[9][4]
        )

        # 横移一步
        assert XiangqiRules.validate_king_move(
            board, Position(row=9, col=4), Position(row=9, col=3), board[9][4]
        )

    def test_king_invalid_moves(self):
        """测试将/帅的非法走法"""
        board = self.setup_board()
        board[9][4] = Piece(type=PieceType.KING, color=PlayerColor.RED)

        # 斜行
        assert not XiangqiRules.validate_king_move(
            board, Position(row=9, col=4), Position(row=8, col=3), board[9][4]
        )

        # 走两步
        assert not XiangqiRules.validate_king_move(
            board, Position(row=9, col=4), Position(row=7, col=4), board[9][4]
        )

        # 走出九宫
        assert not XiangqiRules.validate_king_move(
            board, Position(row=9, col=4), Position(row=9, col=2), board[9][4]
        )


class TestAdvisorMovement:
    """士/仕走法测试"""

    def setup_board(self):
        """创建初始棋盘"""
        return [[None for _ in range(9)] for _ in range(10)]

    def test_advisor_valid_moves(self):
        """测试士/仕的合法走法"""
        board = self.setup_board()
        board[9][3] = Piece(type=PieceType.ADVISOR, color=PlayerColor.RED)

        # 斜行一步
        assert XiangqiRules.validate_advisor_move(
            board, Position(row=9, col=3), Position(row=8, col=4), board[9][3]
        )

    def test_advisor_invalid_moves(self):
        """测试士/仕的非法走法"""
        board = self.setup_board()
        board[9][3] = Piece(type=PieceType.ADVISOR, color=PlayerColor.RED)

        # 直行
        assert not XiangqiRules.validate_advisor_move(
            board, Position(row=9, col=3), Position(row=8, col=3), board[9][3]
        )

        # 走出九宫
        assert not XiangqiRules.validate_advisor_move(
            board, Position(row=9, col=3), Position(row=8, col=2), board[9][3]
        )


class TestElephantMovement:
    """象/相走法测试"""

    def setup_board(self):
        """创建初始棋盘"""
        return [[None for _ in range(9)] for _ in range(10)]

    def test_elephant_valid_moves(self):
        """测试象/相的合法走法"""
        board = self.setup_board()
        board[2][2] = Piece(type=PieceType.ELEPHANT, color=PlayerColor.BLACK)

        # 象行田
        assert XiangqiRules.validate_elephant_move(
            board, Position(row=2, col=2), Position(row=4, col=4), board[2][2]
        )

        # 另一个方向
        assert XiangqiRules.validate_elephant_move(
            board, Position(row=2, col=2), Position(row=0, col=4), board[2][2]
        )

    def test_elephant_blocked_eye(self):
        """测试塞象眼"""
        board = self.setup_board()
        board[2][2] = Piece(type=PieceType.ELEPHANT, color=PlayerColor.BLACK)
        board[3][3] = Piece(type=PieceType.PAWN, color=PlayerColor.RED)  # 塞象眼

        # 象眼被堵
        assert not XiangqiRules.validate_elephant_move(
            board, Position(row=2, col=2), Position(row=4, col=4), board[2][2]
        )

    def test_elephant_cross_river(self):
        """测试象不能过河"""
        board = self.setup_board()
        board[2][2] = Piece(type=PieceType.ELEPHANT, color=PlayerColor.BLACK)

        # 试图过河
        assert not XiangqiRules.validate_elephant_move(
            board, Position(row=2, col=2), Position(row=6, col=4), board[2][2]
        )

    def test_elephant_invalid_moves(self):
        """测试象的非法走法"""
        board = self.setup_board()
        board[2][2] = Piece(type=PieceType.ELEPHANT, color=PlayerColor.BLACK)

        # 直行
        assert not XiangqiRules.validate_elephant_move(
            board, Position(row=2, col=2), Position(row=3, col=2), board[2][2]
        )

        # 马走日
        assert not XiangqiRules.validate_elephant_move(
            board, Position(row=2, col=2), Position(row=3, col=4), board[2][2]
        )


class TestHorseMovement:
    """马/傌走法测试"""

    def setup_board(self):
        """创建初始棋盘"""
        return [[None for _ in range(9)] for _ in range(10)]

    def test_horse_valid_moves(self):
        """测试马的合法走法"""
        board = self.setup_board()
        board[5][4] = Piece(type=PieceType.HORSE, color=PlayerColor.RED)

        # 马行日 - 8个方向
        valid_moves = [
            (3, 3),
            (3, 5),  # 前方两个
            (4, 2),
            (4, 6),  # 左右两个
            (6, 2),
            (6, 6),  # 后方两个
            (7, 3),
            (7, 5),  # 再后方两个
        ]

        for to_row, to_col in valid_moves:
            assert XiangqiRules.validate_horse_move(
                board, Position(row=5, col=4), Position(row=to_row, col=to_col), board[5][4]
            )

    def test_horse_blocked_leg(self):
        """测试蹩马腿"""
        board = self.setup_board()
        board[5][4] = Piece(type=PieceType.HORSE, color=PlayerColor.RED)

        # 在正前方放置棋子蹩马腿
        board[4][4] = Piece(type=PieceType.PAWN, color=PlayerColor.BLACK)

        # 向前跳的两个方向都被堵
        assert not XiangqiRules.validate_horse_move(
            board, Position(row=5, col=4), Position(row=3, col=3), board[5][4]
        )
        assert not XiangqiRules.validate_horse_move(
            board, Position(row=5, col=4), Position(row=3, col=5), board[5][4]
        )

    def test_horse_invalid_moves(self):
        """测试马的非法走法"""
        board = self.setup_board()
        board[5][4] = Piece(type=PieceType.HORSE, color=PlayerColor.RED)

        # 直行
        assert not XiangqiRules.validate_horse_move(
            board, Position(row=5, col=4), Position(row=4, col=4), board[5][4]
        )

        # 斜行两格
        assert not XiangqiRules.validate_horse_move(
            board, Position(row=5, col=4), Position(row=3, col=6), board[5][4]
        )


class TestChariotMovement:
    """车/俥走法测试"""

    def setup_board(self):
        """创建初始棋盘"""
        return [[None for _ in range(9)] for _ in range(10)]

    def test_chariot_valid_horizontal_move(self):
        """测试车横向移动"""
        board = self.setup_board()
        board[5][2] = Piece(type=PieceType.CHARIOT, color=PlayerColor.RED)

        # 横向移动多格
        assert XiangqiRules.validate_chariot_move(
            board, Position(row=5, col=2), Position(row=5, col=6), board[5][2]
        )

    def test_chariot_valid_vertical_move(self):
        """测试车纵向移动"""
        board = self.setup_board()
        board[5][4] = Piece(type=PieceType.CHARIOT, color=PlayerColor.RED)

        # 纵向移动多格
        assert XiangqiRules.validate_chariot_move(
            board, Position(row=5, col=4), Position(row=2, col=4), board[5][4]
        )

    def test_chariot_blocked(self):
        """测试车被阻挡"""
        board = self.setup_board()
        board[5][2] = Piece(type=PieceType.CHARIOT, color=PlayerColor.RED)
        board[5][4] = Piece(type=PieceType.PAWN, color=PlayerColor.BLACK)  # 阻挡

        # 路径被挡
        assert not XiangqiRules.validate_chariot_move(
            board, Position(row=5, col=2), Position(row=5, col=6), board[5][2]
        )

    def test_chariot_invalid_move(self):
        """测试车的非法走法"""
        board = self.setup_board()
        board[5][4] = Piece(type=PieceType.CHARIOT, color=PlayerColor.RED)

        # 斜行
        assert not XiangqiRules.validate_chariot_move(
            board, Position(row=5, col=4), Position(row=6, col=5), board[5][4]
        )


class TestCannonMovement:
    """炮/炮走法测试"""

    def setup_board(self):
        """创建初始棋盘"""
        return [[None for _ in range(9)] for _ in range(10)]

    def test_cannon_move_without_capturing(self):
        """测试炮不吃子时的移动"""
        board = self.setup_board()
        board[5][2] = Piece(type=PieceType.CANNON, color=PlayerColor.RED)

        # 不吃子时移动
        assert XiangqiRules.validate_cannon_move(
            board, Position(row=5, col=2), Position(row=5, col=6), board[5][2], False
        )

    def test_cannon_capture_with_platform(self):
        """测试炮吃子（需要炮架）"""
        board = self.setup_board()
        board[5][2] = Piece(type=PieceType.CANNON, color=PlayerColor.RED)
        board[5][4] = Piece(type=PieceType.PAWN, color=PlayerColor.BLACK)  # 炮架
        board[5][6] = Piece(type=PieceType.PAWN, color=PlayerColor.BLACK)  # 目标

        # 吃子
        assert XiangqiRules.validate_cannon_move(
            board, Position(row=5, col=2), Position(row=5, col=6), board[5][2], True
        )

    def test_cannon_capture_without_platform(self):
        """测试炮没有炮架不能吃子"""
        board = self.setup_board()
        board[5][2] = Piece(type=PieceType.CANNON, color=PlayerColor.RED)
        board[5][6] = Piece(type=PieceType.PAWN, color=PlayerColor.BLACK)  # 目标

        # 没有炮架
        assert not XiangqiRules.validate_cannon_move(
            board, Position(row=5, col=2), Position(row=5, col=6), board[5][2], True
        )

    def test_cannon_invalid_move(self):
        """测试炮的非法走法"""
        board = self.setup_board()
        board[5][4] = Piece(type=PieceType.CANNON, color=PlayerColor.RED)

        # 斜行
        assert not XiangqiRules.validate_cannon_move(
            board, Position(row=5, col=4), Position(row=6, col=5), board[5][4], False
        )


class TestSoldierMovement:
    """卒/兵走法测试"""

    def setup_board(self):
        """创建初始棋盘"""
        return [[None for _ in range(9)] for _ in range(10)]

    def test_soldier_forward_before_river(self):
        """测试卒过河前只能前行"""
        board = self.setup_board()
        board[3][2] = Piece(type=PieceType.PAWN, color=PlayerColor.BLACK)

        # 前进
        assert XiangqiRules.validate_soldier_move(
            board, Position(row=3, col=2), Position(row=4, col=2), board[3][2]
        )

    def test_soldier_cannot_move_backward_before_river(self):
        """测试卒不能后退"""
        board = self.setup_board()
        board[3][2] = Piece(type=PieceType.PAWN, color=PlayerColor.BLACK)

        # 后退
        assert not XiangqiRules.validate_soldier_move(
            board, Position(row=3, col=2), Position(row=2, col=2), board[3][2]
        )

    def test_soldier_cannot_move_sideways_before_river(self):
        """测试卒过河前不能横移"""
        board = self.setup_board()
        board[3][2] = Piece(type=PieceType.PAWN, color=PlayerColor.BLACK)

        # 横移
        assert not XiangqiRules.validate_soldier_move(
            board, Position(row=3, col=2), Position(row=3, col=3), board[3][2]
        )

    def test_soldier_sideways_after_river(self):
        """测试卒过河后可以横移"""
        board = self.setup_board()
        board[5][2] = Piece(type=PieceType.PAWN, color=PlayerColor.BLACK)

        # 横移
        assert XiangqiRules.validate_soldier_move(
            board, Position(row=5, col=2), Position(row=5, col=3), board[5][2]
        )

    def test_soldier_diagonal_move(self):
        """测试卒不能斜行"""
        board = self.setup_board()
        board[5][2] = Piece(type=PieceType.PAWN, color=PlayerColor.BLACK)

        # 斜行
        assert not XiangqiRules.validate_soldier_move(
            board, Position(row=5, col=2), Position(row=6, col=3), board[5][2]
        )


class TestFacingKings:
    """将帅不能对面测试"""

    def setup_board(self):
        """创建初始棋盘"""
        return [[None for _ in range(9)] for _ in range(10)]

    def test_kings_facing_same_column(self):
        """测试将帅在同一列且中间无棋子"""
        board = self.setup_board()
        board[0][4] = Piece(type=PieceType.KING, color=PlayerColor.BLACK)
        board[9][4] = Piece(type=PieceType.KING, color=PlayerColor.RED)

        # 将帅对脸
        assert XiangqiRules.is_facing_kings(board, PlayerColor.RED)

    def test_kings_facing_with_piece_between(self):
        """测试将帅中间有棋子"""
        board = self.setup_board()
        board[0][4] = Piece(type=PieceType.KING, color=PlayerColor.BLACK)
        board[5][4] = Piece(type=PieceType.PAWN, color=PlayerColor.BLACK)  # 中间有子
        board[9][4] = Piece(type=PieceType.KING, color=PlayerColor.RED)

        # 中间有子，不是对脸
        assert not XiangqiRules.is_facing_kings(board, PlayerColor.RED)

    def test_kings_different_columns(self):
        """测试将帅不在同一列"""
        board = self.setup_board()
        board[0][3] = Piece(type=PieceType.KING, color=PlayerColor.BLACK)
        board[9][4] = Piece(type=PieceType.KING, color=PlayerColor.RED)

        # 不同列
        assert not XiangqiRules.is_facing_kings(board, PlayerColor.RED)


class TestCheckDetection:
    """将军检测测试"""

    def setup_board(self):
        """创建初始棋盘"""
        return [[None for _ in range(9)] for _ in range(10)]

    def test_chariot_checking_king(self):
        """测试车将军"""
        board = self.setup_board()
        board[9][4] = Piece(type=PieceType.KING, color=PlayerColor.RED)
        board[3][4] = Piece(type=PieceType.CHARIOT, color=PlayerColor.BLACK)

        # 红将被黑车将军
        assert XiangqiRules.is_in_check(board, PlayerColor.RED)

    def test_cannon_checking_king(self):
        """测试炮将军"""
        board = self.setup_board()
        board[9][4] = Piece(type=PieceType.KING, color=PlayerColor.RED)
        board[5][4] = Piece(type=PieceType.PAWN, color=PlayerColor.BLACK)  # 炮架
        board[1][4] = Piece(type=PieceType.CANNON, color=PlayerColor.BLACK)

        # 红将被黑炮将军
        assert XiangqiRules.is_in_check(board, PlayerColor.RED)

    def test_king_not_in_check(self):
        """测试未将军"""
        board = self.setup_board()
        board[9][4] = Piece(type=PieceType.KING, color=PlayerColor.RED)

        # 没有被将军
        assert not XiangqiRules.is_in_check(board, PlayerColor.RED)


class TestCheckmateDetection:
    """将死检测测试"""

    def setup_board(self):
        """创建初始棋盘"""
        return [[None for _ in range(9)] for _ in range(10)]

    def test_simple_checkmate_scenario(self):
        """测试简单将死局面"""
        board = self.setup_board()
        # 红帅在九宫中心
        board[8][4] = Piece(type=PieceType.KING, color=PlayerColor.RED)
        # 黑车在正上方将军
        board[5][4] = Piece(type=PieceType.CHARIOT, color=PlayerColor.BLACK)
        # 黑兵占据第7行两个逃生位置
        board[7][3] = Piece(type=PieceType.PAWN, color=PlayerColor.BLACK)
        board[7][5] = Piece(type=PieceType.PAWN, color=PlayerColor.BLACK)
        # 己方仕占据了第8行位置
        board[8][3] = Piece(type=PieceType.ADVISOR, color=PlayerColor.RED)
        board[8][5] = Piece(type=PieceType.ADVISOR, color=PlayerColor.RED)
        # 第9行位置被对方控制
        board[9][3] = Piece(type=PieceType.CHARIOT, color=PlayerColor.BLACK)
        board[9][4] = Piece(type=PieceType.CHARIOT, color=PlayerColor.BLACK)
        board[9][5] = Piece(type=PieceType.CHARIOT, color=PlayerColor.BLACK)

        # 红方将被死 - 将军且无路可逃
        assert XiangqiRules.is_checkmate(board, PlayerColor.RED)

    def test_not_checkmate_when_can_escape(self):
        """测试可以解除将军的不是将死"""
        board = self.setup_board()
        board[9][4] = Piece(type=PieceType.KING, color=PlayerColor.RED)
        board[9][5] = Piece(type=PieceType.ADVISOR, color=PlayerColor.RED)
        board[3][4] = Piece(type=PieceType.CHARIOT, color=PlayerColor.BLACK)

        # 红方可以用仕挡车
        assert not XiangqiRules.is_checkmate(board, PlayerColor.RED)


class TestStalemateDetection:
    """困毙检测测试"""

    def setup_board(self):
        """创建初始棋盘"""
        return [[None for _ in range(9)] for _ in range(10)]

    def test_stalemate_scenario(self):
        """测试困毙局面"""
        # 注意：困毙是一个罕见的情况，很难构造
        # 这里简化测试：只测试函数的基本逻辑
        # 实际游戏中，困毙通常需要复杂的局面
        # 这个测试暂时跳过，因为构造困毙局面比较复杂
        pass

    def test_not_stalemate_when_in_check(self):
        """测试被将军时不是困毙"""
        board = self.setup_board()
        board[9][4] = Piece(type=PieceType.KING, color=PlayerColor.RED)
        board[3][4] = Piece(type=PieceType.CHARIOT, color=PlayerColor.BLACK)

        # 被将军，不是困毙
        assert not XiangqiRules.is_stalemate(board, PlayerColor.RED)

    def test_not_stalemate_when_can_move(self):
        """测试有子可动不是困毙"""
        board = self.setup_board()
        board[9][4] = Piece(type=PieceType.KING, color=PlayerColor.RED)
        board[6][4] = Piece(type=PieceType.PAWN, color=PlayerColor.RED)

        # 兵可以动
        assert not XiangqiRules.is_stalemate(board, PlayerColor.RED)


class TestAllValidMoves:
    """获取所有合法走法测试"""

    def setup_board(self):
        """创建初始棋盘"""
        return [[None for _ in range(9)] for _ in range(10)]

    def test_get_king_valid_moves(self):
        """测试将的合法走法"""
        board = self.setup_board()
        board[8][4] = Piece(type=PieceType.KING, color=PlayerColor.RED)  # 在九宫中心

        moves = XiangqiRules.get_all_valid_moves(board, PlayerColor.RED)
        # 将在九宫中心有4个方向可走
        assert len(moves) == 4

    def test_get_pawn_valid_moves(self):
        """测试兵的合法走法"""
        board = self.setup_board()
        board[3][4] = Piece(type=PieceType.PAWN, color=PlayerColor.RED)  # 过河兵（row=3 < 4.5）

        moves = XiangqiRules.get_all_valid_moves(board, PlayerColor.RED)
        # 过河兵可以前、左、右
        assert len(moves) == 3


class TestInsufficientMaterial:
    """子力不足检测测试"""

    def setup_board(self):
        """创建初始棋盘"""
        return [[None for _ in range(9)] for _ in range(10)]

    def test_king_vs_king(self):
        """测试双方只剩将帅"""
        board = self.setup_board()
        board[0][4] = Piece(type=PieceType.KING, color=PlayerColor.BLACK)
        board[9][4] = Piece(type=PieceType.KING, color=PlayerColor.RED)

        assert XiangqiRules.is_insufficient_material(board)

    def test_king_and_advisor_vs_king(self):
        """测试将帅+士 对 将帅"""
        board = self.setup_board()
        board[0][4] = Piece(type=PieceType.KING, color=PlayerColor.BLACK)
        board[9][4] = Piece(type=PieceType.KING, color=PlayerColor.RED)
        board[9][3] = Piece(type=PieceType.ADVISOR, color=PlayerColor.RED)

        assert XiangqiRules.is_insufficient_material(board)

    def test_sufficient_material(self):
        """测试子力足够"""
        board = self.setup_board()
        board[0][4] = Piece(type=PieceType.KING, color=PlayerColor.BLACK)
        board[9][4] = Piece(type=PieceType.KING, color=PlayerColor.RED)
        board[9][0] = Piece(type=PieceType.CHARIOT, color=PlayerColor.RED)

        assert not XiangqiRules.is_insufficient_material(board)


class TestBoardHash:
    """棋盘哈希测试"""

    def setup_board(self):
        """创建初始棋盘"""
        return [[None for _ in range(9)] for _ in range(10)]

    def test_same_board_same_hash(self):
        """测试相同棋盘有相同哈希"""
        board1 = self.setup_board()
        board1[0][4] = Piece(type=PieceType.KING, color=PlayerColor.BLACK)

        board2 = self.setup_board()
        board2[0][4] = Piece(type=PieceType.KING, color=PlayerColor.BLACK)

        assert XiangqiRules.get_board_hash(board1) == XiangqiRules.get_board_hash(board2)

    def test_different_board_different_hash(self):
        """测试不同棋盘有不同哈希"""
        board1 = self.setup_board()
        board1[0][4] = Piece(type=PieceType.KING, color=PlayerColor.BLACK)

        board2 = self.setup_board()
        board2[0][4] = Piece(type=PieceType.KING, color=PlayerColor.RED)

        assert XiangqiRules.get_board_hash(board1) != XiangqiRules.get_board_hash(board2)


class TestRepetitionDetection:
    """重复局面检测测试"""

    def setup_board(self):
        """创建初始棋盘"""
        return [[None for _ in range(9)] for _ in range(10)]

    def test_no_repetition(self):
        """测试没有重复"""
        history = []
        for i in range(5):
            board = self.setup_board()
            board[0][4] = Piece(type=PieceType.KING, color=PlayerColor.BLACK)
            board[0][4 + i] = Piece(type=PieceType.PAWN, color=PlayerColor.BLACK)
            history.append(board)

        assert not XiangqiRules.has_repetition(history)

    def test_three_fold_repetition(self):
        """测试三次重复"""
        history = []
        board1 = self.setup_board()
        board1[0][4] = Piece(type=PieceType.KING, color=PlayerColor.BLACK)
        board1[9][4] = Piece(type=PieceType.KING, color=PlayerColor.RED)

        # 添加相同的棋盘3次（每次之间有间隔）
        board_copy = [row[:] for row in board1]
        history.append(board_copy)
        history.append([row[:] for row in board_copy])  # 第2次
        history.append([row[:] for row in board_copy])  # 第3次

        assert XiangqiRules.has_repetition(history)


class TestPositionEvaluation:
    """局面评估测试"""

    def setup_board(self):
        """创建初始棋盘"""
        return [[None for _ in range(9)] for _ in range(10)]

    def test_evaluate_equal_material(self):
        """测试评估均势局面"""
        board = self.setup_board()
        board[0][4] = Piece(type=PieceType.KING, color=PlayerColor.BLACK)
        board[9][4] = Piece(type=PieceType.KING, color=PlayerColor.RED)
        board[0][0] = Piece(type=PieceType.CHARIOT, color=PlayerColor.BLACK)
        board[9][0] = Piece(type=PieceType.CHARIOT, color=PlayerColor.RED)

        score, description = XiangqiRules.evaluate_position(board, PlayerColor.RED)
        assert "均势" in description

    def test_evaluate_advantage(self):
        """测试评估优势局面"""
        board = self.setup_board()
        board[0][4] = Piece(type=PieceType.KING, color=PlayerColor.BLACK)
        board[9][4] = Piece(type=PieceType.KING, color=PlayerColor.RED)
        board[9][0] = Piece(type=PieceType.CHARIOT, color=PlayerColor.RED)  # 红方多一车

        score, description = XiangqiRules.evaluate_position(board, PlayerColor.RED)
        assert score > 0
        assert "优势" in description


class TestDrawDetection:
    """综合和棋检测测试"""

    def setup_board(self):
        """创建初始棋盘"""
        return [[None for _ in range(9)] for _ in range(10)]

    def test_draw_by_insufficient_material(self):
        """测试子力不足和棋"""
        board = self.setup_board()
        board[0][4] = Piece(type=PieceType.KING, color=PlayerColor.BLACK)
        board[9][4] = Piece(type=PieceType.KING, color=PlayerColor.RED)

        is_draw, reason = XiangqiRules.is_draw(board, [], [], PlayerColor.RED)
        assert is_draw
        assert "子力不足" in reason

    def test_draw_by_repetition(self):
        """测试重复局面和棋"""
        board = self.setup_board()
        board[0][4] = Piece(type=PieceType.KING, color=PlayerColor.BLACK)
        board[9][4] = Piece(type=PieceType.KING, color=PlayerColor.RED)
        board[0][0] = Piece(
            type=PieceType.CHARIOT, color=PlayerColor.BLACK
        )  # 添加一个车避免触发子力不足
        board[9][0] = Piece(type=PieceType.CHARIOT, color=PlayerColor.RED)

        history = [board, board, board]

        is_draw, reason = XiangqiRules.is_draw(board, history, [], PlayerColor.RED)
        assert is_draw
        assert "重复局面" in reason

    def test_draw_by_moves_without_capture(self):
        """测试60回合和棋"""
        board = self.setup_board()
        board[0][4] = Piece(type=PieceType.KING, color=PlayerColor.BLACK)
        board[9][4] = Piece(type=PieceType.KING, color=PlayerColor.RED)
        board[0][0] = Piece(
            type=PieceType.CHARIOT, color=PlayerColor.BLACK
        )  # 添加车避免触发子力不足
        board[9][0] = Piece(type=PieceType.CHARIOT, color=PlayerColor.RED)

        is_draw, reason = XiangqiRules.is_draw(
            board, [], [], PlayerColor.RED, moves_without_capture=120
        )
        assert is_draw
        assert "六十回合" in reason

    def test_not_draw(self):
        """测试非和棋局面"""
        board = self.setup_board()
        board[0][4] = Piece(type=PieceType.KING, color=PlayerColor.BLACK)
        board[9][4] = Piece(type=PieceType.KING, color=PlayerColor.RED)
        board[9][0] = Piece(type=PieceType.CHARIOT, color=PlayerColor.RED)

        is_draw, reason = XiangqiRules.is_draw(board, [], [], PlayerColor.RED)
        assert not is_draw
