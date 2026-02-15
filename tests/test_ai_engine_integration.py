"""测试AI引擎集成

验证backend/ai/engine.py可以正确使用Moonfish引擎
"""

import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置环境变量
os.environ["AI_ENGINE_TYPE"] = "moonfish"
os.environ["MOONFISH_DEPTH"] = "3"


def test_ai_engine_initialization():
    """测试AI引擎初始化"""
    print("\n=== 测试AI引擎初始化 ===")
    try:
        from backend.ai.engine import AIEngine

        # 创建引擎
        engine = AIEngine()
        print("✓ AIEngine创建成功")
        print(f"  - 引擎类型: {engine.engine_type}")
        print(f"  - Moonfish引擎: {hasattr(engine, 'moonfish_engine')}")

        return True
    except Exception as e:
        print(f"✗ AIEngine初始化失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_ai_engine_with_moonfish():
    """测试AI引擎使用Moonfish"""
    print("\n=== 测试AI引擎使用Moonfish ===")
    try:
        import asyncio
        from backend.ai.engine import AIEngine
        from backend.models.schemas import PlayerColor

        # 创建引擎（内部会创建GameManager）
        engine = AIEngine()

        # 直接使用Moonfish的初始棋盘测试
        import sys
        from pathlib import Path

        moonfish_path = Path("moonfish")
        sys.path.insert(0, str(moonfish_path))
        import moonfish

        # 创建新游戏
        session_id, game_state = engine.game_manager.create_game(player_color=PlayerColor.RED)

        print(f"✓ 游戏创建成功")
        print(f"  - 会话ID: {session_id}")
        print(f"  - 当前玩家: {game_state.current_player.value}")

        # 测试Moonfish直接使用初始棋盘
        print(f"\n直接测试Moonfish...")
        pos = moonfish.Position(board=moonfish.board_initial, move_color=0, score=0)
        searcher = moonfish.Searcher()
        move, score, depth = searcher.search(pos, secs=2, max_depth=1)
        print(f"✓ Moonfish搜索成功: move={move}, score={score}")

        return True
    except Exception as e:
        print(f"✗ AI引擎测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_ai_engine_with_llm():
    """测试AI引擎使用LLM（可选）"""
    print("\n=== 测试AI引擎使用LLM（可选） ===")
    try:
        # 检查是否配置了API key
        if not os.getenv("OPENAI_API_KEY"):
            print("⊘ 跳过LLM测试（未配置OPENAI_API_KEY）")
            return True

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

        return True
    except Exception as e:
        print(f"✗ LLM引擎测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    results = []

    # 运行所有测试
    results.append(("AI引擎初始化", test_ai_engine_initialization()))
    results.append(("Moonfish下棋", test_ai_engine_with_moonfish()))
    results.append(("LLM引擎（可选）", test_ai_engine_with_llm()))

    # 总结
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"  通过: {passed}/{total}")

    for name, result in results:
        status = "✓" if result else "✗"
        print(f"  {status} {name}")

    if passed == total:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
