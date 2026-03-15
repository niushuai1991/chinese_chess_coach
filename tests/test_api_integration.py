"""API路由集成测试

验证所有API端点可访问
"""

import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置环境变量
os.environ["AI_ENGINE_TYPE"] = "moonfish"


def test_api_docs():
    """测试API文档可访问"""
    print("\n=== 测试API文档 ===")
    try:
        import requests

        response = requests.get("http://localhost:8005/docs")
        print(f"✓ API文档可访问: {response.status_code}")
        print(f"  Content-Type: {response.headers.get('Content-Type')}")

        return response.status_code == 200
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False


def test_health_check():
    """测试健康检查"""
    print("\n=== 测试健康检查 ===")
    try:
        import requests

        response = requests.get("http://localhost:8005/health")
        print(f"✓ 健康检查: {response.status_code}")
        print(f"  响应: {response.json()}")

        return response.status_code == 200
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False


def test_settings_endpoints():
    """测试设置API端点"""
    print("\n=== 测试设置API ===")
    try:
        import requests

        # GET difficulty
        response = requests.get("http://localhost:8005/api/settings/difficulty")
        print(f"✓ GET /api/settings/difficulty: {response.status_code}")
        data = response.json()
        print(f"  当前难度: {data.get('difficulty')}")

        # POST difficulty
        response = requests.post(
            "http://localhost:8005/api/settings/difficulty", json={"difficulty": 4}
        )
        print(f"✓ POST /api/settings/difficulty: {response.status_code}")
        print(f"  响应: {response.json()}")

        return True
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False


def test_game_endpoints():
    """测试游戏API端点"""
    print("\n=== 测试游戏API ===")
    try:
        import requests

        # 创建新游戏
        response = requests.post("http://localhost:8005/api/game/new", json={"player_color": "red"})
        print(f"✓ POST /api/game/new: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            session_id = data.get("session_id")
            print(f"  会话ID: {session_id}")

            # 获取游戏状态
            response = requests.get(f"http://localhost:8005/api/game/{session_id}")
            print(f"✓ GET /api/game/{{session_id}}: {response.status_code}")

        return True
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False


if __name__ == "__main__":
    import subprocess
    import time

    # 启动服务器（后台）
    print("启动后端服务器...")
    server_process = subprocess.Popen(
        ["uv", "run", "uvicorn", "backend.main:app", "--port", "8005"],
        cwd=str(project_root),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # 等待服务器启动
    time.sleep(3)

    results = []

    # 运行所有测试
    results.append(("API文档", test_api_docs()))
    results.append(("健康检查", test_health_check()))
    results.append(("设置API", test_settings_endpoints()))
    results.append(("游戏API", test_game_endpoints()))

    # 停止服务器
    server_process.terminate()
    server_process.wait()

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
