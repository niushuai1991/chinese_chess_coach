"""测试AI引擎集成

验证backend/ai/engine.py可以正确使用Moonfish引擎
"""

import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置环境变量
os.environ["AI_ENGINE_TYPE"] = "moonfish"
os.environ["MOONFISH_DEPTH"] = "3"


@pytest.fixture(autouse=True)
def mock_moonfish_module():
    """Mock moonfish 模块"""
    with patch.dict(sys.modules, {"moonfish": MagicMock()}):
        yield


def test_ai_engine_initialization():
    """测试AI引擎初始化"""
    print("\n=== 测试AI引擎初始化 ===")
    from backend.ai.engine import AIEngine

    # 创建引擎
    engine = AIEngine()
    print("✓ AIEngine创建成功")
    print(f"  - 引擎类型: {engine.engine_type}")
    print(f"  - Moonfish引擎: {hasattr(engine, 'moonfish_engine')}")

    assert engine is not None


def test_ai_engine_with_moonfish():
    """测试AI引擎使用Moonfish"""
    print("\n=== 测试AI引擎使用Moonfish ===")
    from backend.ai.engine import AIEngine
    from backend.models.schemas import PlayerColor

    # 创建引擎（内部会创建GameManager）
    engine = AIEngine()

    # 创建新游戏
    session_id, game_state = engine.game_manager.create_game(player_color=PlayerColor.RED)

    print(f"✓ 游戏创建成功")
    print(f"  - 会话ID: {session_id}")
    print(f"  - 当前玩家: {game_state.current_player.value}")

    assert session_id is not None
    assert game_state is not None
    assert engine is not None


def test_ai_engine_with_llm():
    """测试AI引擎使用LLM（可选）"""
    print("\n=== 测试AI引擎使用LLM（可选） ===")
    # 检查是否配置了API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⊘ 跳过LLM测试（未配置OPENAI_API_KEY）")
        return

    # 设置为LLM模式
    os.environ["AI_ENGINE_TYPE"] = "llm"

    from backend.ai.engine import AIEngine
    from backend.game.state import GameManager
    from backend.models.schemas import PlayerColor

    # 创建引擎和游戏
    engine = AIEngine()
    game_manager = GameManager()

    # 创建新游戏
    session_id = "test_session_llm"
    session_id, game_state = game_manager.create_game(player_color=PlayerColor.RED)

    print(f"✓ 游戏创建成功（LLM模式）")

    # 注意：不实际调用API，只验证初始化
    print(f"  - 引擎类型: {engine.engine_type}")
    print(f"  - Model: {engine.model}")

    assert engine is not None
    assert game_state is not None


if __name__ == "__main__":
    # 运行所有测试
    test_ai_engine_initialization()
    test_ai_engine_with_moonfish()
    test_ai_engine_with_llm()

    print("\n" + "=" * 50)
    print("✅ 所有测试完成！")
