import os

def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip().strip('"')
    os.environ.update(env_vars)
    return env_vars

env_vars = load_env()
print("环境变量加载结果：")
print(f"BASE_URL: {env_vars.get('BASE_URL', '未找到')}")
print(f"MODEL: {env_vars.get('MODEL', '未找到')}")
print(f"API_KEY: {env_vars.get('API_KEY', '未找到')}")
print(f"PROMPT: {env_vars.get('PROMPT', '未找到')}")
print(f"MAX_TOKENS: {env_vars.get('MAX_TOKENS', '未找到')}")
