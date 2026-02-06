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
