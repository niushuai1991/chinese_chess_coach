"""测试AI引擎功能"""

import os
import pytest
from unittest.mock import Mock, patch

from backend.game.state import GameManager
from backend.models.schemas import PlayerColor, Position


class TestAIEngine:
    """AI引擎测试"""

    def test_board_to_fen(self):
        """测试棋盘转FEN"""
        game_manager = GameManager()
        session_id, game_state = game_manager.create_game(PlayerColor.RED)

        # Mock AIEngine to avoid API key requirement
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            from backend.ai.engine import AIEngine

            ai_engine = AIEngine()
            fen = ai_engine._board_to_fen(game_state.board)

            # 初始局面应该有正确的FEN
            assert "rheakaehr" in fen  # 黑方底线 (r=horse, h=elephant)
            assert "RHEAKAEHR" in fen  # 红方底线
            assert "c" in fen  # 黑炮
            assert "C" in fen  # 红炮
            assert "p" in fen  # 黑卒
            assert "P" in fen  # 红兵

    def test_parse_ai_move_json_format(self):
        """测试解析JSON格式棋步"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            from backend.ai.engine import AIEngine

            ai_engine = AIEngine()

            move = ai_engine._parse_ai_move(
                '{"from": {"row": 3, "col": 1}, "to": {"row": 4, "col": 4}}'
            )

            assert move["from_pos"] == Position(row=3, col=1)
            assert move["to_pos"] == Position(row=4, col=4)

    def test_parse_ai_move_coordinate_format(self):
        """测试解析坐标格式棋步"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            from backend.ai.engine import AIEngine

            ai_engine = AIEngine()

            move = ai_engine._parse_ai_move("(3,1)->(4,4)")

            assert move["from_pos"] == Position(row=3, col=1)
            assert move["to_pos"] == Position(row=4, col=4)

    def test_parse_ai_move_invalid_format(self):
        """测试解析无效格式"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            from backend.ai.engine import AIEngine

            ai_engine = AIEngine()

            with pytest.raises(ValueError):
                ai_engine._parse_ai_move("invalid move")
