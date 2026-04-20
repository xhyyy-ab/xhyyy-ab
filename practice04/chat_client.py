import os
import json
import time
import sys
import subprocess
from http.client import HTTPSConnection, HTTPConnection
from urllib.parse import urlparse

def load_env():
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip().strip('"')
    return env_vars

def anythingllm_query(message):
    """使用subprocess模块调用curl命令访问AnythingLLM的API接口"""
    env_vars = load_env()
    api_key = env_vars.get('ANYTHINGLLM_API_KEY', '')
    
    if not api_key:
        return "[错误] 未配置ANYTHINGLLM_API_KEY环境变量"
    
    url = "http://localhost:3001/api/v1/workspace/assistant-chats/chat"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "message": message
    }
    
    # 构建curl命令
    curl_cmd = [
        "curl",
        "-X", "POST",
        url,
        "-H", f"Content-Type: {headers['Content-Type']}",
        "-H", f"Authorization: {headers['Authorization']}",
        "-d", json.dumps(data)
    ]
    
    try:
        # 执行curl命令
        result = subprocess.run(
            curl_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30
        )
        
        # 检查返回码
        if result.returncode != 0:
            stderr = result.stderr.decode('utf-8', errors='replace')
            return f"[错误] curl命令执行失败: {stderr}"
        
        # 解析响应
        try:
            stdout = result.stdout.decode('utf-8', errors='replace')
            response = json.loads(stdout)
            if 'error' in response and response['error'] is not None:
                error_message = response['error'] or "未知错误"
                return f"[错误] API返回错误: {error_message}"
            
            # 提取响应内容
            if 'textResponse' in response:
                return response['textResponse']
            elif 'content' in response:
                return response['content']
            elif 'message' in response:
                return response['message']
            elif 'data' in response:
                return str(response['data'])
            else:
                return f"[错误] API返回格式不正确: {stdout}"
        except json.JSONDecodeError as e:
            stdout = result.stdout.decode('utf-8', errors='replace')
            return f"[错误] 无法解析API响应: {stdout}"
    except subprocess.TimeoutExpired:
        return "[错误] 请求超时，请检查AnythingLLM服务是否运行"
    except Exception as e:
        return f"[错误] 发生未知错误: {str(e)}"

def calculate_context_length(conversation_history):
    total_length = 0
    for message in conversation_history:
        total_length += len(message.get('content', ''))
    return total_length

def summarize_conversation(base_url, model, api_key, messages_to_summarize):
    prompt = "请总结以下对话内容，保留关键信息：\n\n"
    
    total_chars = 0
    max_chars = 1500
    
    for msg in messages_to_summarize:
        role = msg.get('role', '')
        content = msg.get('content', '')
        
        if total_chars + len(content) > max_chars:
            remaining = max_chars - total_chars
            if remaining > 0:
                content = content[:remaining]
                prompt += f"{role}: {content}...\n"
            break
        
        prompt += f"{role}: {content}\n"
        total_chars += len(content)
    
    parsed_url = urlparse(base_url)
    host = parsed_url.netloc
    path = parsed_url.path or '/'
    if not path.endswith('/'):
        path += '/'
    path += 'chat/completions'
    
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    if parsed_url.scheme == 'https':
        conn = HTTPSConnection(host)
    else:
        conn = HTTPConnection(host)
    
    conn.request(
        "POST",
        path,
        body=json.dumps(data),
        headers=headers
    )
    
    response = conn.getresponse()
    response_data = response.read().decode('utf-8')
    conn.close()
    
    try:
        result = json.loads(response_data)
        if 'error' in result:
            return None, f"Error: {result['error']['message']}"
        
        if 'choices' not in result or len(result['choices']) == 0:
            return None, f"Error: No choices in response: {response_data[:200]}"
        
        if 'message' not in result['choices'][0]:
            return None, f"Error: No message in choice: {str(result['choices'][0])[:200]}"
        
        content = result['choices'][0]['message']['content']
        return content, None
    except Exception as e:
        return None, f"Error parsing response: {str(e)}, response: {response_data[:200]}"

def check_and_summarize(conversation_history, base_url, model, api_key, max_rounds=5, max_length=3000):
    if len(conversation_history) < max_rounds:
        return conversation_history, False
    
    context_length = calculate_context_length(conversation_history)
    if context_length < max_length:
        return conversation_history, False
    
    print(f"\n[系统提示] 检测到对话历史过长（{len(conversation_history)}轮，{context_length}字符），正在压缩...")
    
    split_point = int(len(conversation_history) * 0.7)
    messages_to_summarize = conversation_history[:split_point]
    messages_to_keep = conversation_history[split_point:]
    
    summary, error = summarize_conversation(base_url, model, api_key, messages_to_summarize)
    
    if error:
        print(f"[错误] 总结失败: {error}")
        return conversation_history, False
    
    print(f"[系统提示] 对话历史已压缩")
    
    new_history = [
        {"role": "system", "content": f"以下是之前对话的总结：{summary}"}
    ]
    new_history.extend(messages_to_keep)
    
    return new_history, True

def stream_llm_response(base_url, model, api_key, messages, max_tokens=500):
    parsed_url = urlparse(base_url)
    host = parsed_url.netloc
    path = parsed_url.path or '/'
    if not path.endswith('/'):
        path += '/'
    path += 'chat/completions'
    
    data = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "stream": True
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    if parsed_url.scheme == 'https':
        conn = HTTPSConnection(host)
    else:
        conn = HTTPConnection(host)
    
    conn.request(
        "POST",
        path,
        body=json.dumps(data),
        headers=headers
    )
    
    response = conn.getresponse()
    
    full_content = ""
    start_time = time.time()
    
    try:
        while True:
            line = response.readline().decode('utf-8')
            if not line:
                break
            
            line = line.strip()
            if line.startswith('data: '):
                data_str = line[6:]
                if data_str == '[DONE]':
                    break
                
                try:
                    chunk = json.loads(data_str)
                    if 'choices' in chunk and len(chunk['choices']) > 0:
                        delta = chunk['choices'][0].get('delta', {})
                        content = delta.get('content', '')
                        if content:
                            print(content, end='', flush=True)
                            full_content += content
                except json.JSONDecodeError:
                    continue
    except KeyboardInterrupt:
        print("\n\n[用户中断]")
    finally:
        conn.close()
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print()
    return full_content, elapsed_time

def should_use_anythingllm(user_input):
    """检测用户输入是否包含仓库相关关键词"""
    user_input_lower = user_input.lower()
    
    # 仓库相关关键词
    repo_keywords = [
        "文档仓库", "文件仓库", "仓库", "anythingllm",
        "文档", "文件", "资料", "知识库"
    ]
    
    for keyword in repo_keywords:
        if keyword in user_input_lower:
            return True
    
    return False

def print_welcome():
    print("=" * 60)
    print("AI 智能体交互式聊天客户端 (带对话历史压缩和AnythingLLM集成)")
    print("=" * 60)
    print("提示：")
    print("  - 输入消息与AI对话")
    print("  - 输入 'quit' 或 'exit' 退出")
    print("  - 按 Ctrl+C 中断当前响应")
    print("  - 对话超过5轮或3000字符时自动压缩历史")
    print("  - 当提到'文档仓库'、'文件仓库'、'仓库'时自动查询AnythingLLM")
    print("=" * 60)

def main():
    env_vars = load_env()
    
    base_url = env_vars.get('BASE_URL', 'http://127.0.0.1:1234/v1')
    model = env_vars.get('MODEL', 'qwen/qwen3.5-2b')
    api_key = env_vars.get('API_KEY', 'sk-local-llm')
    max_tokens = int(env_vars.get('MAX_TOKENS', 500))
    
    print_welcome()
    print(f"连接到: {base_url}")
    print(f"使用模型: {model}")
    print("=" * 60)
    
    conversation_history = []
    
    try:
        while True:
            try:
                user_input = input("\n你: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', '退出']:
                    print("再见！")
                    break
                
                # 检查是否需要使用AnythingLLM
                if should_use_anythingllm(user_input):
                    print("[系统提示] 正在查询AnythingLLM文档仓库...")
                    anythingllm_response = anythingllm_query(user_input)
                    print(f"[AnythingLLM] {anythingllm_response}")
                    
                    # 将查询和响应添加到对话历史
                    conversation_history.append({"role": "user", "content": user_input})
                    conversation_history.append({"role": "assistant", "content": f"[AnythingLLM查询结果]\n{anythingllm_response}"})
                    continue
                
                conversation_history.append({"role": "user", "content": user_input})
                
                print("AI: ", end='', flush=True)
                
                ai_response, time_taken = stream_llm_response(
                    base_url, model, api_key, conversation_history, max_tokens
                )
                
                if ai_response:
                    conversation_history.append({"role": "assistant", "content": ai_response})
                    print(f"\n[耗时: {time_taken:.2f}秒]")
                    
                    conversation_history, was_summarized = check_and_summarize(
                        conversation_history, base_url, model, api_key
                    )
                    
                    if was_summarized:
                        print(f"[当前对话轮数: {len(conversation_history)}]")
                
            except KeyboardInterrupt:
                print("\n\n检测到 Ctrl+C，继续聊天...")
                continue
                
    except KeyboardInterrupt:
        print("\n\n程序已退出。")

if __name__ == "__main__":
    main()
