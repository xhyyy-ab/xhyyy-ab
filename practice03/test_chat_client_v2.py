import os
import sys
import json
import time

sys.path.insert(0, os.path.dirname(__file__))
from chat_client_v2 import (
    load_env, calculate_context_length, check_and_summarize,
    extract_key_information, save_key_information, check_and_extract_key_info,
    search_chat_history, should_search_chat_history
)

def test_key_information_extraction():
    print("测试1: 关键信息提取功能")
    
    env_vars = load_env()
    base_url = env_vars.get('BASE_URL', 'http://127.0.0.1:1234/v1')
    model = env_vars.get('MODEL', 'qwen/qwen3.5-2b')
    api_key = env_vars.get('API_KEY', 'sk-local-llm')
    
    test_messages = [
        {"role": "user", "content": "张三，你明天下午3点在会议室A和李四讨论项目进度"},
        {"role": "assistant", "content": "好的，我会准时参加会议，准备好项目进度报告"}
    ]
    
    key_info, error = extract_key_information(base_url, model, api_key, test_messages)
    
    if error:
        print(f"[失败] 提取关键信息失败: {error}")
    else:
        print("[通过] 关键信息提取成功")
        print("提取的关键信息:")
        print(key_info)
        save_key_information(key_info)
    
    print()

def test_chat_history_search():
    print("测试2: 聊天历史搜索功能")
    
    env_vars = load_env()
    base_url = env_vars.get('BASE_URL', 'http://127.0.0.1:1234/v1')
    model = env_vars.get('MODEL', 'qwen/qwen3.5-2b')
    api_key = env_vars.get('API_KEY', 'sk-local-llm')
    
    test_query = "张三和李四的会议安排"
    
    try:
        result = search_chat_history(test_query, base_url, model, api_key)
        print("[通过] 聊天历史搜索成功")
        print("搜索结果:")
        print(result)
    except Exception as e:
        print(f"[失败] 搜索失败: {e}")
    
    print()

def test_search_trigger_detection():
    print("测试3: 搜索触发检测")
    
    test_cases = [
        "/search 张三的会议",
        "查找聊天历史",
        "搜索聊天记录",
        "聊天记录里有什么",
        "之前聊了什么",
        "普通对话内容"
    ]
    
    for test_case in test_cases:
        should_search = should_search_chat_history(test_case)
        expected = test_case != "普通对话内容"
        status = "[通过]" if should_search == expected else "[失败]"
        print(f"{status} '{test_case}' -> 应该搜索: {expected}, 实际: {should_search}")
    
    print()

def test_extraction_trigger():
    print("测试4: 关键信息提取触发")
    
    env_vars = load_env()
    base_url = env_vars.get('BASE_URL', 'http://127.0.0.1:1234/v1')
    model = env_vars.get('MODEL', 'qwen/qwen3.5-2b')
    api_key = env_vars.get('API_KEY', 'sk-local-llm')
    
    conversation = []
    for i in range(5):
        conversation.append({"role": "user", "content": f"测试消息{i+1}"})
        conversation.append({"role": "assistant", "content": f"回复消息{i+1}"})
    
    print(f"当前对话轮数: {len(conversation)}")
    
    was_extracted = check_and_extract_key_info(conversation, base_url, model, api_key, extraction_interval=5)
    
    if was_extracted:
        print("[通过] 关键信息提取触发成功")
    else:
        print("[失败] 关键信息提取未触发")
    
    print()

def test_log_file_creation():
    print("测试5: 日志文件创建")
    
    log_dir = "D:\\chat-log"
    log_file = os.path.join(log_dir, "log.txt")
    
    if os.path.exists(log_file):
        print(f"[通过] 日志文件存在: {log_file}")
        file_size = os.path.getsize(log_file)
        print(f"[通过] 日志文件大小: {file_size} 字节")
    else:
        print("[失败] 日志文件不存在")
    
    print()

def main():
    print("=" * 60)
    print("聊天客户端v2功能测试")
    print("=" * 60)
    print()
    
    try:
        test_search_trigger_detection()
        test_log_file_creation()
        
        print("测试6: 实际功能测试（需要LLM服务）")
        print("注意：此测试需要LLM服务正常运行")
        try:
            test_key_information_extraction()
            test_extraction_trigger()
            test_chat_history_search()
        except Exception as e:
            print(f"[失败] 测试失败（可能是LLM服务未启动）: {e}\n")
        
        print("=" * 60)
        print("测试完成")
        print("=" * 60)
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
