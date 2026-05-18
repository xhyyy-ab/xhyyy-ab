import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chat_client import load_env, anythingllm_query

def test_anythingllm():
    load_env()

    print("=== 测试 AnythingLLM 查询功能 ===\n")

    test_message = "你好，请介绍一下你自己"

    print(f"测试消息: {test_message}")
    print("正在查询...\n")

    result = anythingllm_query(test_message)

    print("查询结果:")
    print(result)

if __name__ == "__main__":
    test_anythingllm()