from file_tools import list_files, rename_file, delete_file, create_file, read_file
import os

# 测试目录
TEST_DIR = "."

print("测试文件操作工具...")
print("=" * 60)

# 测试 list_files
print("1. 测试 list_files 工具:")
result = list_files(TEST_DIR)
if isinstance(result, str) and result.startswith("错误"):
    print(f"  错误: {result}")
else:
    print(f"  成功: 找到 {len(result)} 个文件/目录")
    for item in result:
        print(f"    - {item['name']} ({item['type']}, {item['size']} 字节)")
print()

# 测试 create_file
print("2. 测试 create_file 工具:")
test_file = "test_tool.txt"
test_content = "这是一个测试文件，用于验证工具调用功能。"
result = create_file(TEST_DIR, test_file, test_content)
print(f"  {result}")
print()

# 测试 read_file
print("3. 测试 read_file 工具:")
result = read_file(TEST_DIR, test_file)
if isinstance(result, str) and result.startswith("错误"):
    print(f"  错误: {result}")
else:
    print(f"  成功: 读取文件内容")
    print(f"    内容: {result}")
print()

# 测试 rename_file
print("4. 测试 rename_file 工具:")
new_test_file = "test_tool_renamed.txt"
result = rename_file(TEST_DIR, test_file, new_test_file)
print(f"  {result}")
print()

# 测试 delete_file
print("5. 测试 delete_file 工具:")
result = delete_file(TEST_DIR, new_test_file)
print(f"  {result}")
print()

print("=" * 60)
print("测试完成！")
