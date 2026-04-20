import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chat_client import anythingllm_query

if __name__ == "__main__":
    print("测试AnythingLLM查询功能...")
    test_query = "仓库中有什么文件？"
    print(f"查询内容: {test_query}")
    
    result = anythingllm_query(test_query)
    print(f"查询结果: {result}")
