"""测试Moonfish适配器"""

import pytest
from backend.engines.moonfish_adapter import MoonfishAdapter
from backend.models.schemas import Piece, PieceType, PlayerColor, Position


def test_board_to_moonfish_empty():
    """测试空棋盘转换"""
    board = [[None for _ in range(9)] for _ in range(10)]
    moonfish_str = MoonfishAdapter.board_to_moonfish(board)

    # 验证：应该是182个字符（10行×9列 + 9个换行）
    lines = moonfish_str.split("\n")
    assert len(lines) == 10, f"棋盘应该有10行，实际{len(lines)}行"

    # 验证：每行应该是9个字符
    for i, line in enumerate(lines):
        assert len(line) == 9, f"第{i}行应该有9列，实际{len(line)}列"

    # 验证：全都是空格
    assert all(c == "." for line in lines for c in line), "空棋盘应该全是点"
    print("✅ 空棋盘转换测试通过")


def test_board_to_moonfish_initial():
    """测试初始棋盘转换"""
    # 创建初始棋盘（红方在下）
    board = [[None for _ in range(9)] for _ in range(10)]

    # 黑方棋子（第0-4行）
    # 车马象士将士象马车
    board[0][0] = Piece(type=PieceType.CHARIOT, color=PlayerColor.BLACK)
    board[0][1] = Piece(type=PieceType.HORSE, color=PlayerColor.BLACK)
    board[0][2] = Piece(type=PieceType.ELEPHANT, color=PlayerColor.BLACK)
    board[0][3] = Piece(type=PieceType.ADVISOR, color=PlayerColor.BLACK)
    board[0][4] = Piece(type=PieceType.KING, color=PlayerColor.BLACK)
    board[0][5] = Piece(type=PieceType.ADVISOR, color=PlayerColor.BLACK)
    board[0][6] = Piece(type=PieceType.ELEPHANT, color=PlayerColor.BLACK)
    board[0][7] = Piece(type=PieceType.HORSE, color=PlayerColor.BLACK)
    board[0][8] = Piece(type=PieceType.CHARIOT, color=PlayerColor.BLACK)

    # 炮
    board[2][1] = Piece(type=PieceType.CANNON, color=PlayerColor.BLACK)
    board[2][7] = Piece(type=PieceType.CANNON, color=PlayerColor.BLACK)

    # 卒
    board[3][0] = Piece(type=PieceType.PAWN, color=PlayerColor.BLACK)
    board[3][2] = Piece(type=PieceType.PAWN, color=PlayerColor.BLACK)
    board[3][4] = Piece(type=PieceType.PAWN, color=PlayerColor.BLACK)
    board[3][6] = Piece(type=PieceType.PAWN, color=PlayerColor.BLACK)
    board[3][8] = Piece(type=PieceType.PAWN, color=PlayerColor.BLACK)

    # 红方棋子（第6-9行）
    board[9][0] = Piece(type=PieceType.CHARIOT, color=PlayerColor.RED)
    board[9][1] = Piece(type=PieceType.HORSE, color=PlayerColor.RED)
    board[9][2] = Piece(type=PieceType.ELEPHANT, color=PlayerColor.RED)
    board[9][3] = Piece(type=PieceType.ADVISOR, color=PlayerColor.RED)
    board[9][4] = Piece(type=PieceType.KING, color=PlayerColor.RED)
    board[9][5] = Piece(type=PieceType.ADVISOR, color=PlayerColor.RED)
    board[9][6] = Piece(type=PieceType.ELEPHANT, color=PlayerColor.RED)
    board[9][7] = Piece(type=PieceType.HORSE, color=PlayerColor.RED)
    board[9][8] = Piece(type=PieceType.CHARIOT, color=PlayerColor.RED)

    # 炮
    board[7][1] = Piece(type=PieceType.CANNON, color=PlayerColor.RED)
    board[7][7] = Piece(type=PieceType.CANNON, color=PlayerColor.RED)

    # 兵
    board[6][0] = Piece(type=PieceType.PAWN, color=PlayerColor.RED)
    board[6][2] = Piece(type=PieceType.PAWN, color=PlayerColor.RED)
    board[6][4] = Piece(type=PieceType.PAWN, color=PlayerColor.RED)
    board[6][6] = Piece(type=PieceType.PAWN, color=PlayerColor.RED)
    board[6][8] = Piece(type=PieceType.PAWN, color=PlayerColor.RED)

    moonfish_str = MoonfishAdapter.board_to_moonfish(board)
    lines = moonfish_str.split("\n")

    # 验证：黑方底线（第0行）
    assert lines[0][0] == "r", "第0行第0列应该是黑车"
    assert lines[0][4] == "k", "第0行第4列应该是黑将"

    # 验证：红方底线（第9行）
    assert lines[9][0] == "R", "第9行第0列应该是红车"
    assert lines[9][4] == "K", "第9行第4列应该是红帅"

    print("✅ 初始棋盘转换测试通过")


def test_moonfish_to_board():
    """测试Moonfish字符串转回棋盘"""
    moonfish_board = """rnbakabnr
.......
.c.....c.
p.p.p.p.p
.......
.......
P.P.P.P.P
.C.....C.
RNBAKABNR"""

    board = MoonfishAdapter.moonfish_to_board(moonfish_board)

    # 验证：棋盘尺寸
    assert len(board) == 10, "棋盘应该有10行"
    assert len(board[0]) == 9, "每行应该有9列"

    # 验证：黑将位置
    king_piece = board[0][4]
    assert king_piece.type == PieceType.KING, "第0行第4列应该是将/帅"
    assert king_piece.color == PlayerColor.BLACK, "应该是黑方"

    print("✅ Moonfish字符串转棋盘测试通过")


def test_move_to_moonfish():
    """测试移动格式转换"""
    # 测试：e2e4（e列第2行到e列第4行）
    # 注意：输入使用0-based行号
    from_pos = Position(row=1, col=4)  # e2
    to_pos = Position(row=3, col=4)  # e4
    piece = Piece(type=PieceType.PAWN, color=PlayerColor.RED)

    ucci_move = MoonfishAdapter.move_to_moonfish(from_pos, to_pos, piece)

    # UCCI格式：e2e4
    assert ucci_move == "e2e4", f"移动格式应该是e2e4，实际{ucci_move}"

    print(f"✅ 移动格式转换测试通过: {ucci_move}")


def test_moonfish_to_move():
    """测试Moonfish索引转项目坐标"""
    # Moonfish索引计算：13*row + (col+2)，其中col+2是因为有2列padding
    # from: row=4, col=4 => 13*4 + 6 = 58
    # to: row=6, col=4 => 13*6 + 6 = 84
    from_idx, to_idx = 58, 84

    from_pos, to_pos = MoonfishAdapter.moonfish_to_move((from_idx, to_idx))

    # 验证：坐标范围
    assert 0 <= from_pos.row <= 9, f"起始行号{from_pos.row}超出范围"
    assert 0 <= from_pos.col <= 8, f"起始列号{from_pos.col}超出范围"
    assert 0 <= to_pos.row <= 9, f"目标行号{to_pos.row}超出范围"
    assert 0 <= to_pos.col <= 8, f"目标列号{to_pos.col}超出范围"

    # 验证：位置正确
    assert from_pos == Position(row=4, col=4), "起始位置应该是(4,4)"
    assert to_pos == Position(row=6, col=4), "目标位置应该是(6,4)"

    print(
        f"✅ Moonfish索引转换测试通过: ({from_pos.row},{from_pos.col})->({to_pos.row},{to_pos.col})"
    )


def test_boundary_handling():
    """测试边界处理"""
    # 测试：超出范围的索引
    from_idx, to_idx = 200, 210  # 超出14×12范围

    from_pos, to_pos = MoonfishAdapter.moonfish_to_move((from_idx, to_idx))

    # 应该返回警告但仍处理
    print(f"✅ 边界处理测试: ({from_pos.row},{from_pos.col})->({to_pos.row},{to_pos.col})")


if __name__ == "__main__":
    # 运行所有测试
    test_board_to_moonfish_empty()
    test_board_to_moonfish_initial()
    test_moonfish_to_board()
    test_move_to_moonfish()
    test_moonfish_to_move()
    test_boundary_handling()

    print("\n🎉 所有适配器测试通过！")
