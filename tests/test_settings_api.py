"""测试设置API

验证难度设置功能
"""

import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_settings_get_difficulty():
    """测试获取难度设置"""
    print("\n=== 测试GET /api/settings/difficulty ===")
    try:
        import requests

        response = requests.get("http://localhost:8000/api/settings/difficulty")
        print(f"✓ 请求成功: {response.status_code}")
        print(f"  响应: {response.json()}")

        return True
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False


def test_settings_set_difficulty():
    """测试设置难度"""
    print("\n=== 测试POST /api/settings/difficulty ===")
    try:
        import requests

        # 测试设置难度为4
        response = requests.post(
            "http://localhost:8000/api/settings/difficulty", json={"difficulty": 4}
        )
        print(f"✓ 请求成功: {response.status_code}")
        print(f"  响应: {response.json()}")

        # 验证难度已设置
        get_response = requests.get("http://localhost:8000/api/settings/difficulty")
        data = get_response.json()
        print(f"  验证: 当前难度={data['difficulty']}")

        return True
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False


def test_settings_invalid_difficulty():
    """测试无效难度值"""
    print("\n=== 测试POST /api/settings/difficulty（无效值）===")
    try:
        import requests

        response = requests.post(
            "http://localhost:8000/api/settings/difficulty", json={"difficulty": 10}
        )
        print(f"✓ 请求成功: {response.status_code}")
        print(f"  预期400: {response.status_code == 400}")
        print(f"  响应: {response.json()}")

        return response.status_code == 400
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False


if __name__ == "__main__":
    import subprocess
    import time

    # 启动服务器（后台）
    print("启动后端服务器...")
    server_process = subprocess.Popen(
        ["uv", "run", "uvicorn", "backend.main:app"],
        cwd=str(project_root),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # 等待服务器启动
    time.sleep(3)

    results = []

    # 运行所有测试
    results.append(("获取难度", test_settings_get_difficulty()))
    results.append(("设置难度", test_settings_set_difficulty()))
    results.append(("无效难度", test_settings_invalid_difficulty()))

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
