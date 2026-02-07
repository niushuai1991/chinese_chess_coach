"""测试AI API连接"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

print("=== 测试 AI API 连接 ===")
print(f"API Key: {os.getenv('OPENAI_API_KEY')[:20]}...")
print(f"Base URL: {os.getenv('OPENAI_BASE_URL')}")
print(f"Model: {os.getenv('MODEL_NAME')}")
print("")

try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL"))

    print("正在调用 API...")
    response = client.chat.completions.create(
        model=os.getenv("MODEL_NAME"),
        messages=[{"role": "user", "content": "你好，请用一句话回复"}],
        timeout=30,
    )

    print(f"✅ API 调用成功！")
    print(f"响应: {response.choices[0].message.content}")

except Exception as e:
    print(f"❌ API 调用失败: {e}")
    print(f"错误类型: {type(e).__name__}")
    import traceback

    traceback.print_exc()
