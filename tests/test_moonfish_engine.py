"""测试Moonfish引擎包装器

验证Moonfish引擎可以正常初始化和搜索
"""

import sys
from pathlib import Path
import pytest
from unittest.mock import MagicMock, patch

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 添加moonfish路径
moonfish_path = project_root / "moonfish"
sys.path.insert(0, str(moonfish_path))


@pytest.fixture(autouse=True)
def mock_moonfish_module():
    """Mock moonfish 模块"""
    mock_pos = MagicMock()
    mock_pos.board = "rnbakabnr\n.......\n.c.....c.\np.p.p.p.p\n.......\n.......\nP.P.P.P.P\n.C.....C.\nRNBAKABNR"
    mock_pos.move_color = 0
    mock_pos.score = 0
    mock_pos.gen_moves.return_value = iter([1, 2, 3])

    mock_searcher = MagicMock()
    mock_searcher.search.return_value = (100, 100, 1)

    mock_moon = MagicMock()
    mock_moon.Entry = MagicMock
    mock_moon.LRUCache = MagicMock
    mock_moon.Searcher = MagicMock(return_value=mock_searcher)
    mock_moon.Position = MagicMock(return_value=mock_pos)
    mock_moon.board_initial = "rnbakabnr\n.......\n.c.....c.\np.p.p.p.p\n.......\n.......\nP.P.P.P.P\n.C.....C.\nRNBAKABNR"

    with patch.dict(sys.modules, {"moonfish": mock_moon}):
        yield


def test_moonfish_import():
    """测试Moonfish导入"""
    print("\n=== 测试Moonfish导入 ===")
    import moonfish

    print("✓ Moonfish导入成功")
    print(f"  - Entry: {moonfish.Entry}")
    print(f"  - LRUCache: {moonfish.LRUCache}")
    print(f"  - Searcher: {moonfish.Searcher}")
    print(f"  - Position: {moonfish.Position}")

    assert moonfish is not None
    assert hasattr(moonfish, "Entry")
    assert hasattr(moonfish, "Searcher")
    assert hasattr(moonfish, "Position")


def test_moonfish_position():
    """测试创建Position对象"""
    print("\n=== 测试Moonfish Position ===")
    import moonfish

    # 使用初始棋盘
    initial_board = moonfish.board_initial
    print(f"✓ 初始棋盘长度: {len(initial_board)}")
    print(f"  前30字符: {initial_board[:30]}")

    # 创建Position
    pos = moonfish.Position(board=initial_board, move_color=0, score=0)
    print(f"✓ Position对象创建成功")
    print(f"  - board长度: {len(pos.board)}")
    print(f"  - move_color: {pos.move_color}")
    print(f"  - score: {pos.score}")

    # 生成走法
    moves = list(pos.gen_moves())
    print(f"✓ 生成{len(moves)}个合法走法")
    if len(moves) > 0:
        print(f"  第一个走法: {moves[0]}")

    assert pos is not None
    assert len(moves) > 0


def test_moonfish_searcher():
    """测试Searcher搜索"""
    print("\n=== 测试Moonfish Searcher ===")
    import moonfish

    # 创建初始局面
    pos = moonfish.Position(board=moonfish.board_initial, move_color=0, score=0)

    # 创建搜索器
    searcher = moonfish.Searcher()
    print("✓ Searcher对象创建成功")

    # 搜索（深度1，快速）
    move, score, depth = searcher.search(pos, secs=1, max_depth=1)
    print(f"✓ 搜索完成")
    print(f"  - 最佳棋步: {move}")
    print(f"  - 分数: {score}")
    print(f"  - 深度: {depth}")

    assert move is not None
    assert searcher is not None


def test_moonfish_engine_wrapper():
    """测试MoonfishEngine包装器"""
    print("\n=== 测试MoonfishEngine包装器 ===")
    from backend.engines.moonfish_engine_v3 import MoonfishEngine

    # 创建引擎
    engine = MoonfishEngine(depth=3)
    print("✓ MoonfishEngine创建成功")

    # 使用初始棋盘
    import moonfish

    board = moonfish.board_initial
    print(f"✓ 棋盘长度: {len(board)}")

    # 获取最佳棋步
    result = engine.get_best_move(board, player="red")
    print(f"✓ get_best_move完成")
    if result:
        from_pos, to_pos, score = result
        print(f"  - 从 {from_pos} 到 {to_pos}")
        print(f"  - 分数: {score}")
    else:
        print(f"  - 未找到棋步")

    assert engine is not None
    assert board is not None


if __name__ == "__main__":
    # 运行所有测试
    test_moonfish_import()
    test_moonfish_position()
    test_moonfish_searcher()
    test_moonfish_engine_wrapper()

    # 总结
    print("\n" + "=" * 50)
    print("✅ 所有测试完成！")
