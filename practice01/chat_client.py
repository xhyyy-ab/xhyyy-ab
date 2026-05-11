import os
import json
import http.client
import ssl
from urllib.parse import urlparse
import sys

# 读取.env文件（从前一个代码优化：增加文件不存在判断 + 编码utf-8）
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    if not os.path.exists(env_path):
        print(f"错误：{env_path} 文件不存在，请从 env.example 复制并填写正确参数")
        exit(1)
    
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

# 流式调用LLM API（完全保留你原来的流式逻辑）
def stream_llm(messages):
    # 获取配置
    base_url = os.getenv('BASE_URL')
    model = os.getenv('MODEL')
    api_key = os.getenv('API_KEY')
    
    if not all([base_url, model, api_key]):
        print("错误：请在.env文件中配置BASE_URL、MODEL和API_KEY")
        exit(1)
    
    # 解析URL
    parsed_url = urlparse(base_url)
    host = parsed_url.netloc
    path = parsed_url.path.rstrip('/') + '/chat/completions'
    protocol = parsed_url.scheme
    
    # 准备请求数据
    data = {
        "model": model,
        "messages": messages,
        "temperature": float(os.getenv('TEMPERATURE', '0.7')),
        "max_tokens": int(os.getenv('MAX_TOKENS', '8192')),
        "stream": True
    }
    
    # 根据协议选择连接类型
    if protocol == 'https':
        # 创建不验证证书的 SSL 上下文
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        conn = http.client.HTTPSConnection(host, context=context)
    else:
        conn = http.client.HTTPConnection(host)
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    try:
        conn.request('POST', path, json.dumps(data), headers)
        response = conn.getresponse()
        
        if response.status != 200:
            error_data = json.loads(response.read().decode())
            print(f"API错误: {error_data.get('error', {}).get('message', '未知错误')}")
            return None
        
        # 处理流式响应
        full_response = ""
        for line in response:
            line = line.decode().strip()
            if not line:
                continue
            if line.startswith('data: '):
                line = line[6:]
                if line == '[DONE]':
                    break
                try:
                    chunk = json.loads(line)
                    if 'choices' in chunk and len(chunk['choices']) > 0:
                        delta = chunk['choices'][0].get('delta', {})
                        if 'content' in delta:
                            content = delta['content']
                            print(content, end='', flush=True)
                            full_response += content
                except json.JSONDecodeError:
                    pass
        print()
        return full_response
    finally:
        conn.close()

def main():
    load_env()
    
    chat_history = []
    
    print("=== LLM 聊天客户端 ===")
    print("输入消息开始聊天，按 Ctrl+C 退出")
    print("====================\n")
    
    try:
        while True:
            user_input = input("你: ")
            chat_history.append({"role": "user", "content": user_input})
            
            print("助手: ", end='', flush=True)
            assistant_response = stream_llm(chat_history)
            
            if assistant_response is None:
                print("请求失败")
            elif assistant_response:
                chat_history.append({"role": "assistant", "content": assistant_response})
            
            print()
    except KeyboardInterrupt:
        print("\n退出聊天客户端")
        sys.exit(0)

if __name__ == "__main__":
    main()