import os
import json
import time
import datetime
from http.client import HTTPConnection
from urllib.parse import urlparse, quote

# 从 file_tools 导入你的文件工具
from file_tools import list_files, rename_file, delete_file, create_file, read_file

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

def stream_llm_response(base_url, model, api_key, messages, max_tokens=500):
    parsed_url = urlparse(base_url)
    host = parsed_url.netloc
    path = parsed_url.path or '/'
    if not path.endswith('/'):
        path += '/'
    path += 'chat/completions'

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "stream": True
    }

    conn = HTTPConnection(host)
    try:
        conn.request("POST", path, json.dumps(data), headers)
        response = conn.getresponse()
        full_content = ""
        start_time = time.time()

        while True:
            line = response.readline().decode('utf-8')
            if not line:
                break
            if line.startswith('data: '):
                data_str = line[6:].strip()
                if data_str == '[DONE]':
                    break
                try:
                    chunk = json.loads(data_str)
                    content = chunk['choices'][0]['delta'].get('content', '')
                    if content:
                        print(content, end='', flush=True)
                        full_content += content
                except:
                    continue
        return full_content, time.time() - start_time
    finally:
        conn.close()

def curl_request(url, method='GET', headers=None, data=None):
    url = url.replace("https://wttr.in", "http://wttr.in")
    parsed = urlparse(url)
    host = parsed.netloc
    path = parsed.path or '/'

    if parsed.query:
        path += "?" + parsed.query

    path = quote(path, safe='/?&')

    conn = HTTPConnection(host)
    try:
        conn.request(method, path, headers=headers or {})
        res = conn.getresponse()
        content = res.read().decode('utf-8')
        return json.dumps({
            "status": res.status,
            "reason": res.reason,
            "content": content
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
    finally:
        conn.close()

def execute_tool(tool_call):
    tool_name = tool_call.get("name")
    args = tool_call.get("arguments", {})

    tool_map = {
        "list_files": list_files,
        "rename_file": rename_file,
        "delete_file": delete_file,
        "create_file": create_file,
        "read_file": read_file,
        "curl": curl_request
    }

    if tool_name in tool_map:
        result = tool_map[tool_name](**args)
        return result
    else:
        return f"未知工具: {tool_name}"

# ====================== ✅ 修复：获取明天天气 ======================
def parse_wttr_html(html):
    try:
        data = json.loads(html)
        if "weather" in data and len(data["weather"]) >= 2:
            # 索引 1 = 明天
            tomorrow = data["weather"][1]
            date_str = data["weather"][1]["date"]
            return {
                "date": date_str,
                "min_temp_c": tomorrow["mintempC"],
                "max_temp_c": tomorrow["maxtempC"],
                "description": tomorrow["weatherDesc"][0]["value"]
            }
    except:
        pass
    return None

def main_loop(conversation_history, base_url, model, api_key, max_tokens):
    while True:
        user_input = input("\n你: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ['quit', 'exit']:
            print("再见！")
            break

        conversation_history.append({"role": "user", "content": user_input})

        print("AI: ", end="", flush=True)
        ai_response, t = stream_llm_response(base_url, model, api_key, conversation_history, max_tokens)

        if not ai_response:
            continue

        tool_call = None
        if "toolcall" in ai_response:
            start = ai_response.find("{")
            if start != -1:
                bracket_count = 1
                end = start
                for i in range(start + 1, len(ai_response)):
                    if ai_response[i] == "{":
                        bracket_count += 1
                    elif ai_response[i] == "}":
                        bracket_count -= 1
                        if bracket_count == 0:
                            end = i + 1
                            break
                try:
                    tool_call = json.loads(ai_response[start:end])
                except:
                    pass

        if tool_call and "toolcall" in tool_call:
            tc = tool_call["toolcall"]
            print("\n[执行工具调用]")
            res = execute_tool(tc)
            print(f"[工具结果] {res}")

            if tc["name"] == "curl":
                try:
                    j = json.loads(res)
                    html = j["content"]
                    weather = parse_wttr_html(html)
                    if weather:
                        # ✅ 显示正确日期 + 正确气温
                        final = (
                            f"\n=====================================\n"
                            f"✅ 青城山明天天气预报（实时数据）\n"
                            f"📅 日期：{weather['date']}\n"
                            f"🌡 最高温度：{weather['max_temp_c']}°C\n"
                            f"❄️ 最低温度：{weather['min_temp_c']}°C\n"
                            f"☁ 天气状况：{weather['description']}\n"
                            f"=====================================\n"
                        )
                        print(final)
                        conversation_history.append({"role": "assistant", "content": ai_response})
                        conversation_history.append({"role": "user", "content": f"工具结果：{res}"})
                        conversation_history.append({"role": "assistant", "content": final})
                        continue
                except:
                    pass

            conversation_history.append({"role": "assistant", "content": ai_response})
            conversation_history.append({"role": "user", "content": f"工具执行结果：{res}"})

            print("AI: ", end="", flush=True)
            final, _ = stream_llm_response(base_url, model, api_key, conversation_history, max_tokens)
            if final:
                print(final)
                conversation_history.append({"role": "assistant", "content": final})
        else:
            conversation_history.append({"role": "assistant", "content": ai_response})
        print(f"\n[耗时 {t:.2f}s]")

if __name__ == "__main__":
    env = load_env()
    base_url = env.get("BASE_URL", "http://127.0.0.1:1234/v1")
    model = env.get("MODEL", "qwen3.5")
    api_key = env.get("API_KEY", "sk-local")
    max_tokens = int(env.get("MAX_TOKENS", 500))

    # ====================== ✅ 关键修复：访问明天天气 ======================
    system_prompt = """
你必须严格输出JSON，不要加任何文字：
{
  "toolcall": {
    "name": "curl",
    "arguments": {
      "url": "http://wttr.in/青城山?format=j1&2"
    }
  }
}
"""

    main_loop([{"role": "system", "content": system_prompt}], base_url, model, api_key, max_tokens)