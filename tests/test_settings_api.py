"""测试设置API

验证难度设置功能
"""

import sys
import os
from pathlib import Path
import pytest

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.mark.skip(reason="需要运行中的服务器和requests模块")
def test_settings_get_difficulty():
    """测试获取难度设置"""
    print("\n=== 测试GET /api/settings/difficulty ===")
    import requests

    response = requests.get("http://localhost:8000/api/settings/difficulty")
    print(f"✓ 请求成功: {response.status_code}")
    print(f"  响应: {response.json()}")

    assert response.status_code == 200


@pytest.mark.skip(reason="需要运行中的服务器和requests模块")
def test_settings_set_difficulty():
    """测试设置难度"""
    print("\n=== 测试POST /api/settings/difficulty ===")
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

    assert response.status_code == 200
    assert data["difficulty"] == 4


@pytest.mark.skip(reason="需要运行中的服务器和requests模块")
def test_settings_invalid_difficulty():
    """测试无效难度值"""
    print("\n=== 测试POST /api/settings/difficulty（无效值）===")
    import requests

    response = requests.post(
        "http://localhost:8000/api/settings/difficulty", json={"difficulty": 10}
    )
    print(f"✓ 请求成功: {response.status_code}")
    print(f"  预期400: {response.status_code == 400}")
    print(f"  响应: {response.json()}")

    assert response.status_code == 400


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

    # 运行所有测试
    test_settings_get_difficulty()
    test_settings_set_difficulty()
    test_settings_invalid_difficulty()

    # 停止服务器
    server_process.terminate()
    server_process.wait()

    # 总结
    print("\n" + "=" * 50)
    print("✅ 所有测试完成！")
