"""游戏逻辑测试"""

import pytest
from backend.game.state import GameManager
from backend.models.schemas import PlayerColor, Position


def test_create_game():
    """测试创建游戏"""
    manager = GameManager()
    session_id, game_state = manager.create_game(PlayerColor.RED)

    assert session_id
    assert game_state.current_player == PlayerColor.RED
    assert len(game_state.move_history) == 0
    assert game_state.board[9][4] is not None  # 红帅


def test_make_move():
    """测试下棋"""
    manager = GameManager()
    session_id, game_state = manager.create_game(PlayerColor.RED)

    # 简单测试：移动一个兵
    from_pos = Position(row=6, col=0)
    to_pos = Position(row=5, col=0)

    new_state = manager.make_move(session_id, from_pos, to_pos)
    assert new_state.current_player == PlayerColor.BLACK
    assert len(new_state.move_history) == 1


def test_undo_moves():
    """测试悔棋"""
    manager = GameManager()
    session_id, game_state = manager.create_game(PlayerColor.RED)

    # 下两步棋
    manager.make_move(session_id, Position(row=6, col=0), Position(row=5, col=0))
    manager.make_move(session_id, Position(row=3, col=0), Position(row=4, col=0))

    # 悔棋
    new_state = manager.undo_moves(session_id, 2)
    assert len(new_state.move_history) == 0
    assert new_state.current_player == PlayerColor.RED


def test_invalid_move():
    """测试无效棋步"""
    manager = GameManager()
    session_id, game_state = manager.create_game(PlayerColor.RED)

    # 尝试移动空位置
    from_pos = Position(row=5, col=0)
    to_pos = Position(row=4, col=0)

    with pytest.raises(ValueError, match="无效的棋步"):
        manager.make_move(session_id, from_pos, to_pos)


def test_get_nonexistent_game():
    """测试获取不存在的游戏"""
    manager = GameManager()
    game = manager.get_game("nonexistent")
    assert game is None


def test_king_capture_ends_game():
    """测试将/帅被吃掉时游戏结束"""
    from backend.models.schemas import Piece, PieceType

    manager = GameManager()
    session_id, game_state = manager.create_game(PlayerColor.RED)

    # 创建一个简单局面：红车在(0,3)可以直接吃掉黑将(0,4)
    # 清空(0,3)和(0,2)，移动红车到(0,3)
    game_state.board[0][3] = Piece(type=PieceType.CHARIOT, color=PlayerColor.RED)
    game_state.board[0][2] = None

    # 黑将仍在(0,4)

    # 红车吃黑将
    new_state = manager.make_move(session_id, Position(row=0, col=3), Position(row=0, col=4))

    # 验证游戏结束
    assert new_state.is_checkmate is True
    assert new_state.is_check is False
    assert len(new_state.move_history) > 0
    # 最后一步应该吃掉了将
    last_move = new_state.move_history[-1]
    assert last_move.captured is not None
    assert last_move.captured.type == PieceType.KING


def test_cannot_move_after_game_ends():
    """测试游戏结束后无法继续下棋"""
    from backend.models.schemas import Piece, PieceType

    manager = GameManager()
    session_id, game_state = manager.create_game(PlayerColor.RED)

    # 创建一个局面让红车吃掉黑将
    game_state.board[0][3] = Piece(type=PieceType.CHARIOT, color=PlayerColor.RED)
    game_state.board[0][2] = None

    # 红车吃黑将，游戏结束
    manager.make_move(session_id, Position(row=0, col=3), Position(row=0, col=4))

    # 尝试继续下棋（黑马移动）
    with pytest.raises(ValueError, match="游戏已结束"):
        manager.make_move(session_id, Position(row=0, col=1), Position(row=1, col=2))
