import os
import json
import sys

# 测试工具函数
print("=== 测试 practice05 工具功能 ===")

# 添加 practice05 目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'practice05'))

# 导入工具函数
try:
    from tool_client import (
        load_env, list_files, rename_file, delete_file, create_file, read_file,
        fetch_webpage, search_chat_history, anythingllm_query
    )
    print("✓ 成功导入工具函数")
except Exception as e:
    print(f"✗ 导入工具函数失败: {e}")
    sys.exit(1)

# 加载环境变量
try:
    load_env()
    print("✓ 成功加载环境变量")
except Exception as e:
    print(f"✗ 加载环境变量失败: {e}")
    sys.exit(1)

# 测试文件操作工具
print("\n=== 测试文件操作工具 ===")

# 测试列出目录
try:
    result = list_files('.')
    data = json.loads(result)
    if data.get('status') == 'success':
        files = data.get('data', [])
        print(f"✓ 列出目录成功，找到 {len(files)} 个文件/目录")
    else:
        print(f"✗ 列出目录失败: {data.get('message')}")
except Exception as e:
    print(f"✗ 测试列出目录失败: {e}")

# 测试创建文件
try:
    test_content = "这是一个测试文件"
    result = create_file('.', 'test_practice05.txt', test_content)
    data = json.loads(result)
    if data.get('status') == 'success':
        print("✓ 创建文件成功")
    else:
        print(f"✗ 创建文件失败: {data.get('message')}")
except Exception as e:
    print(f"✗ 测试创建文件失败: {e}")

# 测试读取文件
try:
    result = read_file('.', 'test_practice05.txt')
    data = json.loads(result)
    if data.get('status') == 'success':
        content = data.get('data')
        if content == test_content:
            print("✓ 读取文件成功")
        else:
            print("✗ 读取文件内容不匹配")
    else:
        print(f"✗ 读取文件失败: {data.get('message')}")
except Exception as e:
    print(f"✗ 测试读取文件失败: {e}")

# 测试重命名文件
try:
    result = rename_file('.', 'test_practice05.txt', 'test_practice05_renamed.txt')
    data = json.loads(result)
    if data.get('status') == 'success':
        print("✓ 重命名文件成功")
    else:
        print(f"✗ 重命名文件失败: {data.get('message')}")
except Exception as e:
    print(f"✗ 测试重命名文件失败: {e}")

# 测试删除文件
try:
    result = delete_file('.', 'test_practice05_renamed.txt')
    data = json.loads(result)
    if data.get('status') == 'success':
        print("✓ 删除文件成功")
    else:
        print(f"✗ 删除文件失败: {data.get('message')}")
except Exception as e:
    print(f"✗ 测试删除文件失败: {e}")

# 测试网络访问工具
print("\n=== 测试网络访问工具 ===")
try:
    result = fetch_webpage('https://www.example.com')
    data = json.loads(result)
    if data.get('status') == 'success':
        content = data.get('data', '')
        if 'Example Domain' in content:
            print("✓ 访问网页成功")
        else:
            print("✗ 访问网页内容不匹配")
    else:
        print(f"✗ 访问网页失败: {data.get('message')}")
except Exception as e:
    print(f"✗ 测试网络访问失败: {e}")

# 测试聊天历史搜索工具
print("\n=== 测试聊天历史搜索工具 ===")
try:
    # 确保聊天日志目录存在
    log_dir = "d:\\chat-log"
    os.makedirs(log_dir, exist_ok=True)
    # 创建测试日志文件
    log_path = os.path.join(log_dir, "log.txt")
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write("测试聊天历史\n用户: 你好\n助手: 你好，有什么可以帮助你的？")
    # 测试搜索
    result = search_chat_history('你好')
    data = json.loads(result)
    if data.get('status') == 'success':
        print("✓ 搜索聊天历史成功")
    else:
        print(f"✗ 搜索聊天历史失败: {data.get('message')}")
except Exception as e:
    print(f"✗ 测试聊天历史搜索失败: {e}")

# 测试AnythingLLM文档仓库访问工具
print("\n=== 测试AnythingLLM文档仓库访问工具 ===")
try:
    result = anythingllm_query('测试AnythingLLM')
    data = json.loads(result)
    if data.get('status') == 'success':
        print("✓ AnythingLLM查询成功")
    else:
        print(f"⚠️  AnythingLLM查询失败（可能是服务未运行或配置问题）: {data.get('message')}")
except Exception as e:
    print(f"⚠️  测试AnythingLLM失败（可能是服务未运行）: {e}")

print("\n=== 测试完成 ===")
print("所有工具功能已测试完毕。")
print("请运行 `python practice05/tool_client.py` 启动交互式客户端。")
