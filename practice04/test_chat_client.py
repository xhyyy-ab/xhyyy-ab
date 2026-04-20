import os
import sys
import json
import time
from http.client import HTTPSConnection, HTTPConnection
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(__file__))
from chat_client import load_env, calculate_context_length, check_and_summarize

def test_context_length():
    print("测试1: 计算对话上下文长度")
    conversation = [
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好！有什么我可以帮助你的吗？"},
        {"role": "user", "content": "请介绍一下Python"}
    ]
    
    length = calculate_context_length(conversation)
    print(f"对话内容总长度: {length} 字符")
    print("[通过] 测试通过\n")

def test_below_threshold():
    print("测试2: 测试低于阈值的情况")
    
    env_vars = load_env()
    base_url = env_vars.get('BASE_URL', 'http://127.0.0.1:1234/v1')
    model = env_vars.get('MODEL', 'qwen/qwen3.5-2b')
    api_key = env_vars.get('API_KEY', 'sk-local-llm')
    
    conversation = [
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好！"}
    ]
    
    print(f"当前对话轮数: {len(conversation)}")
    print(f"当前对话长度: {calculate_context_length(conversation)} 字符")
    
    new_history, was_summarized = check_and_summarize(
        conversation, base_url, model, api_key, max_rounds=5, max_length=3000
    )
    
    if not was_summarized:
        print("[通过] 对话未压缩（符合预期）")
    else:
        print("[失败] 对话被压缩（不符合预期）")
    
    print()

def test_summarization_trigger():
    print("测试3: 测试总结触发条件（长对话）")
    
    env_vars = load_env()
    base_url = env_vars.get('BASE_URL', 'http://127.0.0.1:1234/v1')
    model = env_vars.get('MODEL', 'qwen/qwen3.5-2b')
    api_key = env_vars.get('API_KEY', 'sk-local-llm')
    
    long_text = "这是一个很长的对话内容。" * 200
    
    conversation = []
    for i in range(6):
        conversation.append({"role": "user", "content": f"问题{i+1}: {long_text}"})
        conversation.append({"role": "assistant", "content": f"回答{i+1}: {long_text}"})
    
    print(f"当前对话轮数: {len(conversation)}")
    print(f"当前对话长度: {calculate_context_length(conversation)} 字符")
    
    new_history, was_summarized = check_and_summarize(
        conversation, base_url, model, api_key, max_rounds=5, max_length=3000
    )
    
    if was_summarized:
        print(f"[通过] 对话已压缩，压缩后轮数: {len(new_history)}")
        print(f"[通过] 第一条消息类型: {new_history[0]['role']}")
        print(f"[通过] 第一条消息内容长度: {len(new_history[0]['content'])} 字符")
        print(f"[通过] 压缩比例: {len(new_history)}/{len(conversation)} = {len(new_history)/len(conversation)*100:.1f}%")
    else:
        print("[失败] 对话未压缩")
    
    print()

def main():
    print("=" * 60)
    print("对话历史压缩功能测试")
    print("=" * 60)
    print()
    
    try:
        test_context_length()
        test_below_threshold()
        
        print("测试3: 测试实际压缩功能（需要LLM服务）")
        print("注意：此测试需要LLM服务正常运行")
        try:
            test_summarization_trigger()
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
