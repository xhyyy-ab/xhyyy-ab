import os
import json
import time
from http.client import HTTPSConnection, HTTPConnection
from urllib.parse import urlparse

# 读取.env文件（适配当前目录结构：.env和脚本在同一个practice01文件夹）
def load_env():
    # 脚本在practice01内，.env也在practice01内，直接取当前目录
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip().strip('"')
    return env_vars

# 构建并发送请求
def call_llm_api(base_url, model, api_key, prompt, max_tokens=500):
    # 解析URL
    parsed_url = urlparse(base_url)
    host = parsed_url.netloc
    path = parsed_url.path or '/'
    if not path.endswith('/'):
        path += '/'
    path += 'chat/completions'
    
    # 准备请求数据
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens
    }
    
    # 准备请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # 建立连接
    if parsed_url.scheme == 'https':
        conn = HTTPSConnection(host)
    else:
        conn = HTTPConnection(host)
    
    # 发送请求
    start_time = time.time()
    conn.request(
        "POST",
        path,
        body=json.dumps(data),
        headers=headers
    )
    
    # 获取响应
    response = conn.getresponse()
    response_data = response.read().decode('utf-8')
    conn.close()
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # 解析响应
    try:
        result = json.loads(response_data)
        if 'error' in result:
            return None, elapsed_time, f"Error: {result['error']['message']}"
        
        # 提取token使用情况
        usage = result.get('usage', {})
        prompt_tokens = usage.get('prompt_tokens', 0)
        completion_tokens = usage.get('completion_tokens', 0)
        total_tokens = usage.get('total_tokens', 0)
        
        # 提取生成的内容
        content = result['choices'][0]['message']['content']
        
        # 计算速度
        if elapsed_time > 0:
            tokens_per_second = total_tokens / elapsed_time
        else:
            tokens_per_second = 0
        
        return {
            'content': content,
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'total_tokens': total_tokens,
            'tokens_per_second': tokens_per_second,
            'time_taken': elapsed_time
        }, None, None
    except Exception as e:
        return None, elapsed_time, f"Error parsing response: {str(e)}"

# 主函数
def main():
    # 加载环境变量
    env_vars = load_env()
    
    # 获取配置（默认值适配你的本地模型，避免.env缺失报错）
    base_url = env_vars.get('BASE_URL', 'http://127.0.0.1:1234/v1')
    model = env_vars.get('MODEL', 'qwen/qwen3.5-2b')
    api_key = env_vars.get('API_KEY', 'sk-local-llm')
    prompt = env_vars.get('PROMPT', '写一个机器人学画画的小故事')
    max_tokens = int(env_vars.get('MAX_TOKENS', 500))
    
    print("LLM API Client")
    print("=" * 50)
    print(f"Base URL: {base_url}")
    print(f"Model: {model}")
    print(f"Prompt: {prompt}")
    print("=" * 50)
    
    # 调用API
    result, time_taken, error = call_llm_api(base_url, model, api_key, prompt, max_tokens)
    
    if error:
        print(f"Error: {error}")
        if time_taken:
            print(f"Time taken: {time_taken:.2f} seconds")
        return
    
    # 输出结果
    print("\nGenerated Content:")
    print("-" * 50)
    print(result['content'])
    print("-" * 50)
    
    print("\nPerformance Metrics:")
    print(f"Prompt tokens: {result['prompt_tokens']}")
    print(f"Completion tokens: {result['completion_tokens']}")
    print(f"Total tokens: {result['total_tokens']}")
    print(f"Time taken: {result['time_taken']:.2f} seconds")
    print(f"Tokens per second: {result['tokens_per_second']:.2f}")

if __name__ == "__main__":
    main()