# AI 智能体开发教学项目

基于Python的AI智能体开发教学项目，帮助学习者从基础到进阶掌握AI智能体的开发技术。

## 项目结构

```
trae_projects/
├── .agents/                    # 技能系统目录
│   └── skills/                 # 技能存储目录
│       └── notice/             # 通知技能
│           └── SKILL.md
├── demo/                       # 演示文件目录
│   ├── 1.txt
│   ├── 2.txt
│   └── result.txt
├── practice01/                 # 练习1：基础LLM客户端
│   ├── chat_client.py          # 支持流式输出的聊天客户端
│   ├── llm_client.py           # 简单的LLM API调用和性能统计
│   ├── 实验报告01.md
│   └── 实验报告01.pdf
├── practice02/                 # 练习2：交互式聊天客户端
│   ├── chat_client.py          # 支持流式输出和历史记录的聊天系统
│   ├── project_structure.html  # 项目结构可视化HTML
│   ├── project_structure.svg   # 项目结构可视化SVG
│   ├── tool_chat_client.py     # 支持工具调用和网络访问的客户端
│   ├── 实验报告02.md
│   └── 实验报告02.pdf
├── practice03/                 # 练习3：对话历史压缩
│   ├── tool_chat_client.py     # 支持工具调用和对话历史压缩的客户端
│   ├── tool_chat_client_v2.py  # 支持关键信息提取和聊天历史搜索的客户端
│   ├── 实验报告03.md
│   └── 实验报告03.pdf
├── practice04/                 # 练习4：AnythingLLM集成
│   ├── chat_client.py          # 支持AnythingLLM查询的聊天系统
│   ├── test_anythingllm.py     # AnythingLLM集成测试
│   ├── 实验报告04.md
│   └── 实验报告04.pdf
├── practice05/                 # 练习5：技能系统
│   ├── chat_client.py          # 支持技能列表读取和技能内容加载的聊天客户端
│   ├── 实验报告05.md
│   └── 实验报告05.pdf
├── practice06/                 # 练习6：链式工具调用
│   ├── chat_client.py          # 支持链式工具调用的客户端
│   ├── summary.txt             # 总结文件
│   ├── 实验报告06.md
│   └── 实验报告06.pdf
├── practice07/                 # 练习7：全栈项目 - 皮肤病智能自查小程序
│   ├── backend/                # 后端服务
│   ├── miniprogram/            # 微信小程序前端
│   ├── init-spec/              # 初始化规范文档
│   ├── PROJECT_SUMMARY.md
│   ├── README.md
│   ├── TEST_REPORT.md
│   ├── api.md
│   ├── requirement.md
│   ├── spec.md
│   ├── test.md
│   └── verify.js
├── reading/                    # 阅读学习目录
│   ├── .agents/
│   │   └── skills/
│   │       └── init-article/
│   │           ├── assets/
│   │           ├── SKILL.md
│   │           ├── check.md
│   │           ├── structure.md
│   │           ├── topic.md
│   │           └── voice.md
│   └── 读书心得.md
├── env.example                 # 环境变量配置模板
├── .gitignore                  # Git忽略文件配置
├── pandoc_cn_style.tex         # Pandoc中文样式文件
└── README.md                   # 项目说明文档
```

## 环境配置

### 1. 创建虚拟环境

```bash
python -m venv venv
```

### 2. 激活虚拟环境

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

### 3. 配置环境变量

复制环境变量模板并填写配置：

```bash
cp env.example .env
```

编辑 `.env` 文件，配置你的LLM API信息：

```env
# OpenAI Compatible LLM Configuration
BASE_URL=http://127.0.0.1:1234/v1
MODEL=qwen/qwen3.5-2b
API_KEY=sk-local-llm
PROMPT=请用一句话介绍什么是LLM
MAX_TOKENS=500
TEMPERATURE=0.7

# AnythingLLM API配置（可选）
ANYTHINGLLM_API_KEY=your_api_key_here
ANYTHINGLLM_WORKSPACE_SLUG=assistant-chats
```

## 练习内容

### Practice 01: 基础LLM客户端

学习目标：
- 掌握HTTP客户端的基本使用
- 理解OpenAI兼容API的请求格式
- 学会统计API调用的性能指标

运行方式：

1. 基础LLM客户端（性能统计）：
```bash
python practice01/llm_client.py
```

2. 聊天客户端（流式输出）：
```bash
python practice01/chat_client.py
```

功能特点：

**基础LLM客户端 (llm_client.py)**
- 使用Python标准HTTP库访问LLM API
- 支持HTTP和HTTPS协议
- 统计token消耗、执行时间和处理速度
- 详细的性能指标输出

**聊天客户端 (chat_client.py)**
- 终端界面交互式对话
- 实时流式输出响应内容
- 自动维护对话历史记录
- 支持quit/exit命令退出

### Practice 02: 交互式聊天客户端

学习目标：
- 实现流式输出功能
- 管理对话历史记录
- 处理用户中断和异常情况
- 构建交互式终端界面
- 实现工具调用功能
- 开发网络访问能力

运行方式：

1. 基础聊天客户端：
```bash
python practice02/chat_client.py
```

2. 工具聊天客户端（支持网络访问）：
```bash
python practice02/tool_chat_client.py
```

功能特点：

**基础聊天客户端 (chat_client.py)**
- 终端界面交互式对话
- 实时流式输出响应内容
- 自动维护对话历史记录
- 支持Ctrl+C中断当前响应
- 支持quit/exit命令退出
- 显示响应时间统计

**工具聊天客户端 (tool_chat_client.py)**
- 集成所有文件操作工具（list_directory、rename_file、delete_file、create_file、read_file）
- 新增网络访问功能（curl工具）
- 支持通过HTTP/HTTPS请求访问网页并返回内容
- 支持使用 wttr.in 获取天气预报（格式：https://wttr.in/城市名）
- 自动处理HTTP和HTTPS协议
- 示例用法：输入"查看明天北京的天气"或直接使用"https://wttr.in/Beijing"

### Practice 03: 对话历史压缩

学习目标：
- 实现对话历史长度检测
- 掌握LLM对话总结技术
- 学习对话上下文管理
- 理解token使用优化策略

运行方式：

1. 工具聊天客户端（带对话历史压缩和工具调用）：
```bash
python practice03/tool_chat_client.py
```

2. 高级工具聊天客户端（带关键信息提取和历史搜索）：
```bash
python practice03/tool_chat_client_v2.py
```

功能特点：

**工具聊天客户端 (tool_chat_client.py)**
- 基于practice02的tool_chat_client.py功能
- 集成所有文件操作工具和网络访问功能
- 新增对话历史自动压缩功能
- 当对话超过5轮或3000字符时触发压缩
- 使用LLM自动总结前70%的对话内容
- 保留最后30%的原始对话内容
- 显示压缩状态和统计信息
- 优化token使用，提高对话效率

**高级工具聊天客户端 (tool_chat_client_v2.py)**
- 基于tool_chat_client.py的所有功能
- 集成所有文件操作工具和网络访问功能
- 每5轮对话自动提取关键信息（5W规则）
- 按照5W规则（Who、What、When、Where、Why）提取关键信息
- 将关键信息保存到本地文件 `D:\chat-log\log.txt`（自动创建目录和文件）
- 支持聊天历史搜索功能
- 输入 `/search` 或表达"查找聊天历史"的意思时触发搜索
- 结合聊天记录和用户请求进行完整的LLM查询
- 新增 `search_chat_history` 工具，支持Function Call触发历史搜索

**核心功能实现**：
- `calculate_context_length()`: 计算对话上下文总长度
- `count_conversation_rounds()`: 计算对话轮数
- `summarize_conversation()`: 调用LLM总结对话历史
- `check_and_summarize()`: 检测并执行对话压缩逻辑
- `extract_key_information()`: 调用LLM按照5W规则提取关键信息
- `save_key_information()`: 保存关键信息到本地JSON文件
- `check_and_extract_key_info()`: 检测并执行关键信息提取
- `search_chat_history()`: 搜索聊天历史记录并结合用户问题回答
- `should_search_chat_history()`: 检测搜索触发条件
- 自动创建目录和文件：确保日志文件路径存在

### Practice 04: AnythingLLM集成

学习目标：
- 学习使用subprocess模块调用外部命令（curl）
- 掌握API认证和请求构建
- 实现外部工具集成到聊天系统
- 了解AnythingLLM的API使用方法

运行方式：

1. 聊天客户端（带AnythingLLM集成）：
```bash
python practice04/chat_client.py
```

2. 测试AnythingLLM集成功能：
```bash
python practice04/test_anythingllm.py
```

功能特点：

**聊天客户端 (chat_client.py)**
- 基于practice03的tool_chat_client_v2.py功能
- 集成所有文件操作工具、网络访问功能和聊天历史搜索
- 新增`anythingllm_query`工具，支持查询AnythingLLM文档仓库
- 当用户提到"文档仓库"、"文件仓库"、"仓库"等关键词时自动触发查询
- 使用subprocess模块调用curl命令访问AnythingLLM API
- 支持API密钥认证
- 详细的错误处理和提示
- 对话历史压缩功能（超过5轮或3000字符时自动压缩）
- 每5轮对话自动提取关键信息（5W规则）

**核心功能实现**：
- `anythingllm_query()`: 使用subprocess调用curl命令访问AnythingLLM API
  - 从环境变量读取ANYTHINGLLM_API_KEY和ANYTHINGLLM_WORKSPACE_SLUG
  - 访问 http://localhost:3001/api/v1/workspace/assistant-chats/chat
  - 使用message字段发送查询内容
  - 使用API密钥进行Bearer认证
  - 支持中文编码处理
  - 处理超时和错误情况
- 新增的工具定义：anythingllm_query
- 更新系统提示词：当用户提到"文档仓库"、"文件仓库"、"仓库"时触发查询

**环境配置**：
确保`.env`文件中已配置AnythingLLM相关变量：

```env
# AnythingLLM API配置
ANYTHINGLLM_API_KEY=your_api_key_here
ANYTHINGLLM_WORKSPACE_SLUG=assistant-chats
```

**使用方法**：
1. 确保AnythingLLM服务正在运行（默认地址：http://localhost:3001）
2. 确保.env文件中配置了ANYTHINGLLM_API_KEY和ANYTHINGLLM_WORKSPACE_SLUG
3. 运行聊天客户端：`python practice04/chat_client.py`
4. 当提到"文档仓库"、"文件仓库"、"仓库"等关键词时，系统会自动调用anythingllm_query工具
5. 查看查询结果并与AI继续对话

**API接口信息**：
- API地址：http://localhost:3001/api/v1/workspace/assistant-chats/chat
- 认证方式：Bearer Token（从ANYTHINGLLM_API_KEY读取）
- 请求方法：POST
- 请求体：{"message": "查询内容"}
- 响应格式：JSON（包含textResponse字段）

### Practice 05: 技能系统

学习目标：
- 开发读取技能列表的function `list_available_skills`
- 开发加载技能正文的function `load_skill_content`
- 理解YAML front matter解析方法
- 掌握技能系统的设计模式
- 学习通过system prompt向LLM传递技能信息

运行方式：

```bash
python practice05/chat_client.py
```

功能特点：

**技能列表读取 (list_available_skills)**
- 自动读取 `.agents/skills` 目录下的一级子目录
- 解析每个子目录中的 `SKILL.md` 文件
- 提取YAML front matter中的name和description字段
- 返回JSON格式的技能列表

**技能内容加载 (load_skill_content)**
- 根据技能名称加载对应的SKILL.md文件
- 提取YAML front matter之后的所有内容
- 返回纯正文内容供LLM执行

**技能系统集成**
- 在系统启动时自动读取所有可用技能
- 通过system prompt以JSON格式向LLM提供技能列表
- 当LLM判断需要使用技能时，自动调用`load_skill_content`工具加载技能内容
- 支持动态更新技能信息

**技能格式规范**：
技能文件使用YAML front matter格式：
```markdown
---
name: 技能名称
description: 技能描述
---

这里是技能的具体内容，
LLM将根据此内容执行相应操作。
```

**核心功能实现**：
- `list_available_skills()`: 扫描skills目录，解析SKILL.md的YAML front matter
- `load_skill_content()`: 根据技能名加载技能正文内容（YAML front matter之后的部分）
- `get_skills_system_prompt()`: 生成包含技能列表的system prompt
- `load_skill_content`工具：支持LLM动态加载技能详细内容
- 每次用户输入时，自动将技能列表通过system prompt发送给LLM

**环境配置**：
技能目录结构：
```
.agents/
└── skills/
    └── {skill_name}/
        └── SKILL.md
```

每个SKILL.md文件包含：
- YAML front matter：技能名称和描述
- 正文内容：技能的详细说明和执行规范

**测试说明**：
已创建notice技能用于测试：
- 路径：`.agents/skills/notice/SKILL.md`
- 功能：撰写通知时自动添加部门前缀
- 规范：通知不能以"通知"开头，必须冠以"XX部通知"前缀

测试用例：
1. 用户未指定部门 → 输出"XX部通知"开头
2. 用户指定"销售部" → 输出"销售部通知"开头

### Practice 06: 链式工具调用

学习目标：
- 掌握链式工具调用的实现方法
- 学习工具调用上下文管理
- 理解多步骤任务的自动执行机制

运行方式：

```bash
python practice06/chat_client.py
```

功能特点：

**链式工具调用**
- 支持多步骤任务的自动执行
- 前一个工具的输出可作为后一个工具的输入
- 自动维护工具调用上下文和变量
- 支持最大迭代次数限制（默认10次）
- 自动解析LLM返回的JSON格式决策

**核心功能实现**：
- `ChainedCallContext`: 链式调用上下文管理器
  - 管理执行步骤历史
  - 维护变量存储
  - 控制迭代次数
- `execute_chained_tool_call()`: 执行链式工具调用主函数
- `build_analysis_prompt()`: 构建分析提示词
- `parse_llm_response()`: 解析LLM响应（支持tool_calls和JSON格式）

**可用工具**：
- `list_directory(dir_path)`: 列出目录文件
- `read_file(dir_path, file_name)`: 读取文件内容
- `create_file(dir_path, file_name, content)`: 创建/写入文件
- `curl(url)`: 获取网页内容

**输出格式**：
LLM必须输出JSON格式：
- 完成任务：`{"done":true,"answer":"完成"}`
- 调用工具：`{"done":false,"tool_call":{"name":"read_file","arguments":{"dir_path":"demo","file_name":"1.txt"}}}`

### Practice 07: 全栈项目 - 皮肤病智能自查小程序

学习目标：
- 学习完整的全栈项目开发流程
- 掌握Node.js后端开发
- 理解微信小程序开发
- 学习RESTful API设计和实现

**项目概述**：
一款面向普通用户的皮肤病智能自查与科普工具微信小程序。

**核心功能**：
- ✅ 微信一键登录
- ✅ AI皮肤病识别（支持1-3张照片）
- ✅ 识别结果展示（置信度分级）
- ✅ 医疗免责声明强制交互
- ✅ 科普文章推荐与浏览
- ✅ 文章收藏功能
- ✅ 识别历史记录
- ✅ 个人中心

**技术特性**：
- RESTful API设计
- JWT认证机制
- MongoDB数据存储
- 响应式UI设计
- 完整的错误处理
- 安全防护（Helmet、Rate Limit）

**详细文档**：
- 需求文档：`practice07/requirement.md`
- 规格文档：`practice07/spec.md`
- API文档：`practice07/api.md`
- 测试文档：`practice07/test.md`
- 测试报告：`practice07/TEST_REPORT.md`
- 项目总结：`practice07/PROJECT_SUMMARY.md`

**运行方式**：
```bash
# 进入后端目录
cd practice07/backend

# 安装依赖
npm install

# 复制环境变量配置
cp .env.example .env

# 编辑.env文件配置参数
# 启动开发服务器
npm run dev
```

## 技术栈

### 核心技术
- **Python 3.12+**
- **标准库**：http.client, json, os, time, sys, ssl, subprocess
- **API协议**：OpenAI兼容协议

### Practice 07 技术栈
- **后端**：Node.js 18+, Express.js, MongoDB, JWT
- **前端**：微信小程序
- **测试**：Jest

## 开发指南

### 代码规范

- 使用Python标准库，避免第三方依赖
- 代码注释使用中文
- 函数和变量命名清晰易懂
- 包含适当的错误处理

### 扩展建议

1. **Practice 01 扩展**：
   - 添加重试机制
   - 支持批量请求
   - 添加缓存功能

2. **Practice 02 扩展**：
   - 支持多轮对话的上下文管理
   - 添加对话历史保存和加载
   - 实现命令系统（如清屏、查看历史等）
   - 添加Markdown格式化输出

3. **Practice 03 扩展**：
   - 支持自定义压缩阈值和比例
   - 添加对话历史持久化存储
   - 实现多级压缩策略（轻度、中度、重度）
   - 添加压缩效果统计和可视化
   - 支持手动触发压缩命令

4. **Practice 06 扩展**：
   - 添加更多工具支持
   - 实现工具调用的循环依赖检测
   - 添加任务进度追踪
   - 支持并行工具调用

## 学习路径

1. **入门阶段**：完成Practice 01，理解LLM API的基本调用方式
2. **进阶阶段**：完成Practice 02，掌握流式处理和状态管理
3. **优化阶段**：完成Practice 03，学习对话历史管理和token优化
4. **实战阶段**：完成Practice 04-06，掌握工具调用和技能系统
5. **全栈阶段**：完成Practice 07，学习完整的项目开发流程

## 常见问题

### Q: 如何连接到不同的LLM服务？

A: 修改`.env`文件中的`BASE_URL`和`MODEL`参数即可连接到不同的LLM服务。

### Q: 流式输出不工作怎么办？

A: 确保你的LLM服务支持流式输出（`stream: true`参数）。

### Q: 如何增加对话历史的长度限制？

A: 在`chat_client.py`中修改对话历史的处理逻辑，添加长度限制。

### Q: 对话历史压缩是如何工作的？

A: 当对话超过5轮或3000字符时，系统会自动调用LLM总结前70%的对话内容，保留最后30%的原始内容，从而优化token使用。

### Q: 如何调整对话压缩的阈值？

A: 在`practice03/tool_chat_client.py`的`check_and_summarize()`函数中修改`max_rounds`（默认5轮）和`max_length`（默认3000字符）参数。

### Q: 压缩后的对话会影响上下文理解吗？

A: 压缩会保留关键信息的总结，但可能会丢失一些细节。系统保留了最近30%的原始对话，确保当前上下文的完整性。

### Q: 如何添加新技能？

A: 在`.agents/skills/`目录下创建新的技能目录，添加`SKILL.md`文件，包含YAML front matter和技能内容。

### Q: 链式工具调用如何工作？

A: LLM分析用户请求，输出JSON格式的决策，系统根据决策调用工具，将工具返回结果加入上下文，继续分析直到任务完成或达到最大迭代次数。

## 贡献指南

欢迎提交Issue和Pull Request来改进这个教学项目。

## 许可证

本项目仅用于教学目的。
