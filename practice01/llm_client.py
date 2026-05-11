import os
import json
import time
from http.client import HTTPSConnection, HTTPConnection
from urllib.parse import urlparse

# 读取 .env 文件
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    env_vars = {}
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    return env_vars

# 发送请求到 LLM API
def call_llm_api(base_url, model, api_key, prompt, max_tokens):
    # 解析 URL
    parsed_url = urlparse(base_url)
    is_https = parsed_url.scheme == 'https'
    host = parsed_url.netloc
    path = parsed_url.path or '/'
    if parsed_url.query:
        path += '?' + parsed_url.query

    # 准备请求数据
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens
    }

    # 创建连接
    if is_https:
        conn = HTTPSConnection(host)
    else:
        conn = HTTPConnection(host)

    # 准备请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # 记录开始时间
    start_time = time.time()

    # 发送请求
    conn.request("POST", path + "/chat/completions", body=json.dumps(data), headers=headers)

    # 获取响应
    response = conn.getresponse()
    response_data = response.read().decode('utf-8')
    conn.close()

    # 记录结束时间
    end_time = time.time()
    elapsed_time = end_time - start_time

    # 解析响应
    try:
        result = json.loads(response_data)
        if "error" in result:
            print(f"Error: {result['error']['message']}")
            return None, 0, 0, 0
        
        # 提取 token 信息
        usage = result.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)
        
        # 计算速度
        if elapsed_time > 0:
            tokens_per_second = total_tokens / elapsed_time
        else:
            tokens_per_second = 0
        
        # 提取回复内容
        message = result["choices"][0]["message"]["content"]
        
        return message, total_tokens, elapsed_time, tokens_per_second
    except json.JSONDecodeError:
        print(f"Failed to decode response: {response_data}")
        return None, 0, 0, 0

# 主函数
def main():
    # 加载环境变量
    env_vars = load_env()
    base_url = env_vars.get('BASE_URL', 'http://127.0.0.1:1234/v1')
    model = env_vars.get('MODEL', 'qwen/qwen3.5-2b')
    api_key = env_vars.get('API_KEY', 'sk-local-llm')
    prompt = env_vars.get('PROMPT', '请用一句话介绍什么是LLM')
    max_tokens = int(env_vars.get('MAX_TOKENS', 500))

    print(f"Base URL: {base_url}")
    print(f"Model: {model}")
    print(f"Prompt: {prompt}")
    print("=" * 50)

    # 调用 LLM API
    response, total_tokens, elapsed_time, tokens_per_second = call_llm_api(
        base_url, model, api_key, prompt, max_tokens
    )

    if response:
        print(f"Response: {response}")
        print("=" * 50)
        print(f"Token Usage: {total_tokens} tokens")
        print(f"Time Taken: {elapsed_time:.2f} seconds")
        print(f"Speed: {tokens_per_second:.2f} tokens/second")

if __name__ == "__main__":
    main()
