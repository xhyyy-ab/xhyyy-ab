import sys
import os

# 添加practice02目录到Python路径
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'practice02'))

# 直接复制curl_request函数进行测试
def curl_request(url, method='GET', headers=None, data=None):
    """
    执行 HTTP 请求
    Args:
        url: 请求 URL
        method: 请求方法 (GET, POST, etc.)
        headers: 请求头
        data: 请求数据
    Returns:
        响应内容
    """
    from urllib.parse import urlparse, quote
    from http.client import HTTPSConnection, HTTPConnection
    import json
    
    # 处理URL中的中文字符
    parsed_url = urlparse(url)
    host = parsed_url.netloc
    path = parsed_url.path or '/'
    
    # 对路径部分进行编码
    path_parts = path.split('/')
    encoded_path = '/'.join(quote(part) for part in path_parts)
    
    if parsed_url.query:
        encoded_path += '?' + parsed_url.query
    
    if parsed_url.scheme == 'https':
        conn = HTTPSConnection(host)
    else:
        conn = HTTPConnection(host)
    
    headers = headers or {}
    if data and 'Content-Type' not in headers:
        headers['Content-Type'] = 'application/json'
    
    try:
        conn.request(
            method,
            encoded_path,
            body=json.dumps(data) if data else None,
            headers=headers
        )
        
        response = conn.getresponse()
        content = response.read().decode('utf-8')
        
        result = {
            'status': response.status,
            'reason': response.reason,
            'content': content
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"错误：{str(e)}"
    finally:
        conn.close()

# 测试curl_request函数
print("测试curl工具访问天气网站...")
result = curl_request("https://wttr.in/青城山")
print("\n响应结果:")
print(result)
