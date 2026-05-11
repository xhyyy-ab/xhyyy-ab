import sys
sys.path.insert(0, 'd:/trae_projects/practice02')

from chat_client import curl

# 测试获取青城山天气预报
print("=== 测试修复后的 curl 函数（ASCII图表 + 详细温度）===")
result = curl("wttr.in/青城山")
print(result)