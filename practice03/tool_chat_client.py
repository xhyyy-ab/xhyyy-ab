import os
import json
import http.client
import ssl
from urllib.parse import urlparse
import sys
from datetime import datetime

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

def get_tools_config():
    return [
        {
            "type": "function",
            "function": {
                "name": "list_directory",
                "description": "列出某个目录下的所有文件和子目录，包含文件基本属性和大小信息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "dir_path": {
                            "type": "string",
                            "description": "要列出的目录路径"
                        }
                    },
                    "required": ["dir_path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "rename_file",
                "description": "修改某个目录下某个文件的名字",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "dir_path": {
                            "type": "string",
                            "description": "文件所在的目录路径"
                        },
                        "old_name": {
                            "type": "string",
                            "description": "文件的旧名称"
                        },
                        "new_name": {
                            "type": "string",
                            "description": "文件的新名称"
                        }
                    },
                    "required": ["dir_path", "old_name", "new_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_file",
                "description": "删除某个目录下的某个文件",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "dir_path": {
                            "type": "string",
                            "description": "文件所在的目录路径"
                        },
                        "file_name": {
                            "type": "string",
                            "description": "要删除的文件名称"
                        }
                    },
                    "required": ["dir_path", "file_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_file",
                "description": "在某个目录下新建一个文件并写入内容",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "dir_path": {
                            "type": "string",
                            "description": "要创建文件的目录路径"
                        },
                        "file_name": {
                            "type": "string",
                            "description": "要创建的文件名称"
                        },
                        "content": {
                            "type": "string",
                            "description": "要写入文件的内容"
                        }
                    },
                    "required": ["dir_path", "file_name", "content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "读取某个目录下某个文件的内容",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "dir_path": {
                            "type": "string",
                            "description": "文件所在的目录路径"
                        },
                        "file_name": {
                            "type": "string",
                            "description": "要读取的文件名称"
                        }
                    },
                    "required": ["dir_path", "file_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "curl",
                "description": "通过HTTP/HTTPS访问网页并返回网页内容，支持使用wttr.in获取天气预报",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "要访问的网页URL地址，例如: https://wttr.in/城市名"
                        }
                    },
                    "required": ["url"]
                }
            }
        }
    ]

def call_llm_non_stream(messages):
    base_url = os.getenv('BASE_URL')
    model = os.getenv('MODEL')
    api_key = os.getenv('API_KEY')

    if not all([base_url, model, api_key]):
        print("错误：请在.env文件中配置BASE_URL、MODEL和API_KEY")
        exit(1)

    parsed_url = urlparse(base_url)
    host = parsed_url.netloc
    path = parsed_url.path.rstrip('/') + '/chat/completions'
    protocol = parsed_url.scheme

    data = {
        "model": model,
        "messages": messages,
        "temperature": float(os.getenv('TEMPERATURE', '0.7')),
        "max_tokens": int(os.getenv('MAX_TOKENS', '8192')),
        "stream": False,
        "tools": get_tools_config(),
        "tool_choice": "auto"
    }

    if protocol == 'https':
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
            try:
                error_data = json.loads(response.read().decode())
                print(f"API错误: {error_data.get('error', {}).get('message', '未知错误')}")
            except json.JSONDecodeError:
                print(f"API错误: HTTP状态码 {response.status}，响应内容不是有效的JSON格式")
            return None

        response_data = json.loads(response.read().decode())

        if 'choices' in response_data and len(response_data['choices']) > 0:
            message = response_data['choices'][0].get('message', {})
            content = message.get('content', '')
            tool_calls = message.get('tool_calls', None)

            return {"content": content, "tool_calls": tool_calls}

        return {"content": "", "tool_calls": None}
    except json.JSONDecodeError as e:
        print(f"解析JSON响应时发生错误: {str(e)}")
        return None
    except Exception as e:
        print(f"调用LLM时发生错误: {str(e)}")
        return None
    finally:
        conn.close()

def stream_llm(messages):
    base_url = os.getenv('BASE_URL')
    model = os.getenv('MODEL')
    api_key = os.getenv('API_KEY')

    if not all([base_url, model, api_key]):
        print("错误：请在.env文件中配置BASE_URL、MODEL和API_KEY")
        exit(1)

    parsed_url = urlparse(base_url)
    host = parsed_url.netloc
    path = parsed_url.path.rstrip('/') + '/chat/completions'
    protocol = parsed_url.scheme

    data = {
        "model": model,
        "messages": messages,
        "temperature": float(os.getenv('TEMPERATURE', '0.7')),
        "max_tokens": int(os.getenv('MAX_TOKENS', '8192')),
        "stream": True,
        "tools": get_tools_config(),
        "tool_choice": "auto"
    }

    if protocol == 'https':
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

        full_response = ""
        has_tool_calls = False

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
                        if 'tool_calls' in delta:
                            has_tool_calls = True
                except json.JSONDecodeError:
                    pass
        print()

        if has_tool_calls:
            result = call_llm_non_stream(messages)
            if result:
                return {"content": result.get("content", full_response), "tool_calls": result.get("tool_calls")}
            return {"content": full_response, "tool_calls": None}

        return {"content": full_response, "tool_calls": None}
    finally:
        conn.close()

def list_directory(dir_path):
    try:
        if not os.path.isdir(dir_path):
            return f"错误：{dir_path} 不是有效的目录路径"

        files_info = []
        for item in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item)
            item_stat = os.stat(item_path)

            if os.path.isdir(item_path):
                item_type = "目录"
            else:
                item_type = "文件"

            size = item_stat.st_size
            if size < 1024:
                size_str = f"{size} 字节"
            elif size < 1024 * 1024:
                size_str = f"{size / 1024:.2f} KB"
            else:
                size_str = f"{size / (1024 * 1024):.2f} MB"

            modify_time = datetime.fromtimestamp(item_stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")

            files_info.append({
                "名称": item,
                "类型": item_type,
                "大小": size_str,
                "修改时间": modify_time
            })

        return json.dumps(files_info, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"列出目录时发生错误: {str(e)}"

def rename_file(dir_path, old_name, new_name):
    try:
        old_path = os.path.join(dir_path, old_name)
        new_path = os.path.join(dir_path, new_name)

        if not os.path.exists(old_path):
            return f"错误：文件 {old_path} 不存在"

        if os.path.exists(new_path):
            return f"错误：文件 {new_path} 已存在"

        os.rename(old_path, new_path)
        return f"成功：文件已从 {old_name} 重命名为 {new_name}"
    except Exception as e:
        return f"重命名文件时发生错误: {str(e)}"

def delete_file(dir_path, file_name):
    try:
        file_path = os.path.join(dir_path, file_name)

        if not os.path.exists(file_path):
            return f"错误：文件 {file_path} 不存在"

        os.remove(file_path)
        return f"成功：文件 {file_name} 已删除"
    except Exception as e:
        return f"删除文件时发生错误: {str(e)}"

def create_file(dir_path, file_name, content):
    try:
        file_path = os.path.join(dir_path, file_name)

        if os.path.exists(file_path):
            return f"错误：文件 {file_path} 已存在"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return f"成功：文件 {file_name} 已创建并写入内容"
    except Exception as e:
        return f"创建文件时发生错误: {str(e)}"

def read_file(dir_path, file_name):
    try:
        file_path = os.path.join(dir_path, file_name)

        if not os.path.exists(file_path):
            return f"错误：文件 {file_path} 不存在"

        if not os.path.isfile(file_path):
            return f"错误：{file_path} 不是一个文件"

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return content
    except Exception as e:
        return f"读取文件时发生错误: {str(e)}"

def curl(url):
    try:
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'https://' + url

        parsed_url = urlparse(url)
        host = parsed_url.netloc
        path = parsed_url.path or '/'

        import urllib.parse
        path = urllib.parse.quote(path, safe='/')

        protocol = parsed_url.scheme

        if protocol == 'https':
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            conn = http.client.HTTPSConnection(host, context=context)
        else:
            conn = http.client.HTTPConnection(host)

        if host == 'wttr.in':
            ascii_result = ""
            json_result = ""

            conn.request('GET', path)
            response = conn.getresponse()
            if response.status == 200:
                ascii_result = response.read().decode('utf-8', errors='ignore')

            conn.close()

            json_path = path + '?format=j1'
            conn = http.client.HTTPSConnection(host, context=context) if protocol == 'https' else http.client.HTTPConnection(host)
            conn.request('GET', json_path)
            response = conn.getresponse()
            if response.status == 200:
                json_content = response.read().decode('utf-8', errors='ignore')
                try:
                    data = json.loads(json_content)
                    if 'weather' in data and len(data['weather']) > 0:
                        today = data['weather'][0]
                        json_result = f"\n📍 详细温度信息:\n"
                        json_result += f"📍 {data['nearest_area'][0]['areaName'][0]['value']}\n"
                        json_result += f"\n📅 今日 ({today['date']}):\n"
                        json_result += f"  🌡️ 最高气温: {today['maxtempC']}°C\n"
                        json_result += f"  🌡️ 最低气温: {today['mintempC']}°C\n"
                        json_result += f"  🌡️ 平均气温: {today['avgtempC']}°C\n"
                        json_result += f"  ☁️ {today['hourly'][0]['weatherDesc'][0]['value']}\n"

                        if len(data['weather']) > 1:
                            tomorrow = data['weather'][1]
                            json_result += f"\n📅 明日 ({tomorrow['date']}):\n"
                            json_result += f"  🌡️ 最高气温: {tomorrow['maxtempC']}°C\n"
                            json_result += f"  🌡️ 最低气温: {tomorrow['mintempC']}°C\n"
                            json_result += f"  🌡️ 平均气温: {tomorrow['avgtempC']}°C\n"
                            json_result += f"  ☁️ {tomorrow['hourly'][0]['weatherDesc'][0]['value']}\n"
                except json.JSONDecodeError:
                    pass

            conn.close()
            return ascii_result + json_result
        else:
            conn.request('GET', path)
            response = conn.getresponse()

            if response.status == 200:
                content = response.read().decode('utf-8', errors='ignore')
                return content
            else:
                return f"错误：HTTP请求失败，状态码: {response.status}"
    except Exception as e:
        return f"访问网页时发生错误: {str(e)}"
    finally:
        try:
            conn.close()
        except:
            pass

def execute_tool(tool_name, arguments):
    if tool_name == "list_directory":
        return list_directory(arguments.get("dir_path", ""))
    elif tool_name == "rename_file":
        return rename_file(arguments.get("dir_path", ""), arguments.get("old_name", ""), arguments.get("new_name", ""))
    elif tool_name == "delete_file":
        return delete_file(arguments.get("dir_path", ""), arguments.get("file_name", ""))
    elif tool_name == "create_file":
        return create_file(arguments.get("dir_path", ""), arguments.get("file_name", ""), arguments.get("content", ""))
    elif tool_name == "read_file":
        return read_file(arguments.get("dir_path", ""), arguments.get("file_name", ""))
    elif tool_name == "curl":
        return curl(arguments.get("url", ""))
    else:
        return f"未知工具: {tool_name}"

def calculate_context_length(messages):
    total_length = 0
    for msg in messages:
        if isinstance(msg, dict):
            content = msg.get('content', '')
            total_length += len(content)
    return total_length

def count_conversation_rounds(messages):
    user_count = 0
    for msg in messages:
        if isinstance(msg, dict) and msg.get('role') == 'user':
            user_count += 1
    return user_count

def summarize_conversation(messages_to_summarize):
    summarize_prompt = [
        {
            "role": "system",
            "content": "你是一个对话历史总结专家。请将下面的对话历史进行精简总结，保留关键信息、用户意图、重要结论和已完成的操作。要求：1. 提取所有重要的用户需求和意图 2. 记录已确定的关键信息 3. 保留工具调用和执行结果的关键信息 4. 用简洁的语言概括每段对话的核心内容 5. 保持信息的完整性和可追溯性"
        }
    ]

    history_text = ""
    for msg in messages_to_summarize:
        if not isinstance(msg, dict):
            continue
        role = msg.get('role', '')
        content = msg.get('content', '')
        if role == 'user':
            history_text += f"用户: {content}\n"
        elif role == 'assistant':
            history_text += f"助手: {content}\n"
        elif role == 'tool':
            tool_name = msg.get('name', 'unknown')
            history_text += f"工具({tool_name})返回: {content}\n"

    summarize_prompt.append({
        "role": "user",
        "content": f"请总结以下对话历史，保留关键信息：\n\n{history_text}"
    })

    result = call_llm_non_stream(summarize_prompt)
    if result:
        return result.get('content', '')
    return ""

def check_and_summarize(chat_history):
    context_length = calculate_context_length(chat_history)
    conversation_rounds = count_conversation_rounds(chat_history)

    ROUND_THRESHOLD = 5
    LENGTH_THRESHOLD = 3000

    if conversation_rounds <= ROUND_THRESHOLD and context_length <= LENGTH_THRESHOLD:
        return chat_history, False

    print(f"\n[系统] 检测到对话历史较长 ({conversation_rounds}轮, 约{context_length}字符)，正在压缩...")

    total_messages = len(chat_history)
    preserve_count = int(total_messages * 0.3)
    summarize_count = total_messages - preserve_count

    if summarize_count < 2:
        return chat_history, False

    messages_to_summarize = chat_history[:summarize_count]
    messages_to_preserve = chat_history[summarize_count:]

    summary = summarize_conversation(messages_to_summarize)

    summarized_history = [
        {
            "role": "system",
            "content": f"【之前的对话已被压缩为以下摘要】\n{summary}\n【以上为历史对话摘要，后续对话继续】"
        }
    ] + messages_to_preserve

    new_length = calculate_context_length(summarized_history)
    new_rounds = count_conversation_rounds(summarized_history)

    print(f"[系统] 压缩完成！({new_rounds}轮, 约{new_length}字符)")

    return summarized_history, True

def main():
    load_env()

    chat_history = []

    print("=== LLM 工具聊天客户端（支持对话历史压缩）===")
    print("输入消息开始聊天，按 Ctrl+C 退出")
    print("支持的工具：list_directory, rename_file, delete_file, create_file, read_file, curl")
    print("使用curl工具可以访问网页，例如：https://wttr.in/城市名 获取天气预报")
    print("功能：当对话超过5轮或3000字符时，自动压缩前70%的对话内容")
    print("==========================================\n")

    try:
        while True:
            user_input = input("你: ")
            chat_history.append({"role": "user", "content": user_input})

            chat_history, was_summarized = check_and_summarize(chat_history)

            print("助手: ", end='', flush=True)
            response = stream_llm(chat_history)

            if response is None:
                print("请求失败")
            else:
                assistant_content = response.get("content", "")
                tool_calls = response.get("tool_calls", None)

                if assistant_content:
                    chat_history.append({"role": "assistant", "content": assistant_content})

                if tool_calls and isinstance(tool_calls, list):
                    for tool_call in tool_calls:
                        tool_name = tool_call.get('function', {}).get('name')
                        arguments = tool_call.get('function', {}).get('arguments', {})

                        if isinstance(arguments, str):
                            try:
                                arguments = json.loads(arguments)
                            except json.JSONDecodeError:
                                print(f"警告：无法解析工具参数: {arguments}")
                                arguments = {}

                        print(f"\n调用工具: {tool_name}({arguments})")
                        tool_result = execute_tool(tool_name, arguments)
                        print(f"工具返回: {tool_result}")

                        chat_history.append({
                            "role": "tool",
                            "content": tool_result,
                            "name": tool_name
                        })

                        print("助手: ", end='', flush=True)
                        final_response = call_llm_non_stream(chat_history)

                        if final_response is not None:
                            final_content = final_response.get("content", "")
                            print(final_content)
                            if final_content:
                                chat_history.append({"role": "assistant", "content": final_content})

            print()
    except KeyboardInterrupt:
        print("\n退出聊天客户端")
        sys.exit(0)

if __name__ == "__main__":
    main()