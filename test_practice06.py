import os
import json
import sys

print("=== 测试 practice06 技能功能 ===")

sys.path.append(os.path.join(os.path.dirname(__file__), 'practice06'))

try:
    from tool_client import (
        load_env, list_available_skills, load_skill_content
    )
    print("✓ 成功导入工具函数")
except Exception as e:
    print(f"✗ 导入工具函数失败: {e}")
    sys.exit(1)

try:
    load_env()
    print("✓ 成功加载环境变量")
except Exception as e:
    print(f"✗ 加载环境变量失败: {e}")
    sys.exit(1)

print("\n=== 测试 list_available_skills ===")
result = list_available_skills()
print(f"返回结果: {result}")
data = json.loads(result)
if data.get('status') == 'success':
    skills = data.get('data', [])
    print(f"✓ list_available_skills 成功，找到 {len(skills)} 个技能")
    for skill in skills:
        print(f"  - {skill.get('name')}: {skill.get('description')}")
else:
    print(f"✗ list_available_skills 失败: {data.get('message')}")

print("\n=== 测试 load_skill_content ===")
result = load_skill_content("notice")
print(f"返回结果: {result}")
data = json.loads(result)
if data.get('status') == 'success':
    content = data.get('data', '')
    print(f"✓ load_skill_content 成功")
    print(f"技能正文内容:\n{content}")
else:
    print(f"✗ load_skill_content 失败: {data.get('message')}")

print("\n=== 测试模拟调用 ===")

skills_result = list_available_skills()
skills_data = json.loads(skills_result)
skills = skills_data.get('data', [])

has_notice_skill = any(s.get('name') == 'notice' for s in skills)
print(f"可用技能列表中是否包含notice: {has_notice_skill}")

if has_notice_skill:
    skill_content_result = load_skill_content("notice")
    skill_content_data = json.loads(skill_content_result)
    if skill_content_data.get('status') == 'success':
        print("✓ 可以成功加载notice技能内容")

        test_prompt_1 = """用户请求：帮我撰写一个关于五一节放假的通知，没有告诉我部门信息

请严格按照以下技能说明执行：

通知撰写规范：
通知不能以"通知"二字开头。
标题必须以部门前缀开头，格式为"XX部通知"。
如果用户没有明确告知所在部门，一律使用"XX部"代替。
通知内容应简洁正式，包含必要的时间、地点、事由等信息。

请撰写这个通知，只输出通知内容即可。"""

        test_prompt_2 = """用户请求：我是销售部的，帮我撰写一个关于五一节放假的通知

请严格按照以下技能说明执行：

通知撰写规范：
通知不能以"通知"二字开头。
标题必须以部门前缀开头，格式为"XX部通知"。
如果用户没有明确告知所在部门，一律使用"XX部"代替。
通知内容应简洁正式，包含必要的时间、地点、事由等信息。

请撰写这个通知，只输出通知内容即可。"""

        print("\n--- 测试用例1：用户未指定部门 ---")
        print(f"测试提示: {test_prompt_1[:50]}...")
        print("预期结果：通知标题应该以'XX部通知'开头")

        print("\n--- 测试用例2：用户指定销售部 ---")
        print(f"测试提示: {test_prompt_2[:50]}...")
        print("预期结果：通知标题应该以'销售部通知'开头")

print("\n=== 测试完成 ===")