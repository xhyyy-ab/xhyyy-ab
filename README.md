# AI 智能体开发教学项目

基于Python的AI智能体开发教学项目，帮助学习者从基础到进阶掌握AI智能体的开发技术。

## 项目结构

```
trae_projects/
├── practice01/          # 练习1：基础LLM客户端
│   └── llm_client.py   # 简单的LLM API调用和性能统计
├── practice02/          # 练习2：交互式聊天客户端
│   ├── chat_client.py         # 支持流式输出和历史记录的聊天系统
│   ├── tool_client.py         # 支持工具调用的客户端
│   └── tool_chat_client.py    # 支持工具调用和网络访问的客户端
├── practice03/          # 练习3：对话历史压缩
│   ├── chat_client.py         # 支持对话历史自动压缩的聊天系统
│   └── test_chat_client.py    # 对话历史压缩功能测试
├── env.example         # 环境变量配置模板
├── .gitignore          # Git忽略文件配置
└── README.md           # 项目说明文档
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
```

## 练习内容

### Practice 01: 基础LLM客户端

学习目标：
- 掌握HTTP客户端的基本使用
- 理解OpenAI兼容API的请求格式
- 学会统计API调用的性能指标

运行方式：
```bash
python practice01/llm_client.py
```

功能特点：
- 使用Python标准HTTP库访问LLM API
- 支持HTTP和HTTPS协议
- 统计token消耗、执行时间和处理速度
- 详细的性能指标输出

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

2. 工具调用客户端：
```bash
python practice02/tool_client.py
```

3. 工具聊天客户端（支持网络访问）：
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

**工具调用客户端 (tool_client.py)**
- 支持文件操作工具：列出文件、重命名文件、删除文件、创建文件、读取文件
- 工具调用的JSON格式解析和执行
- 工具执行结果的处理和展示

**工具聊天客户端 (tool_chat_client.py)**
- 集成所有文件操作工具
- 新增网络访问功能（curl工具）
- 支持通过HTTP请求访问网页并返回内容
- 支持GET、POST等HTTP方法
- 支持自定义请求头和请求数据

### Practice 03: 对话历史压缩

学习目标：
- 实现对话历史长度检测
- 掌握LLM对话总结技术
- 学习对话上下文管理
- 理解token使用优化策略

运行方式：

1. 基础聊天客户端（带对话历史压缩）：
```bash
python practice03/chat_client.py
```

2. 高级聊天客户端（带关键信息提取和历史搜索）：
```bash
python practice03/chat_client_v2.py
```

3. 测试对话历史压缩功能：
```bash
python practice03/test_chat_client.py
```

4. 测试高级功能：
```bash
python practice03/test_chat_client_v2.py
```

功能特点：

**对话历史压缩客户端 (chat_client.py)**
- 基于practice02的聊天客户端功能
- 自动检测对话历史长度
- 当对话超过5轮或3000字符时触发压缩
- 使用LLM自动总结前70%的对话内容
- 保留最后30%的原始对话内容
- 显示压缩状态和统计信息
- 优化token使用，提高对话效率

**核心功能实现**：
- `calculate_context_length()`: 计算对话上下文总长度
- `summarize_conversation()`: 调用LLM总结对话历史
- `check_and_summarize()`: 检测并执行对话压缩逻辑
- 智能分割：前70%压缩，后30%保留原文
- 错误处理：LLM服务异常时的容错机制

**高级聊天客户端 (chat_client_v2.py)**
- 基于基础聊天客户端的所有功能
- 每5轮对话自动提取关键信息
- 按照5W规则（Who、What、When、Where、Why）提取关键信息
- 将关键信息保存到本地文件 `D:\chat-log\log.txt`
- 支持聊天历史搜索功能
- 输入 `/search` 或表达"查找聊天历史"的意思时触发搜索
- 结合聊天记录和用户请求进行完整的LLM查询

**核心功能实现**：
- `extract_key_information()`: 调用LLM提取关键信息
- `save_key_information()`: 保存关键信息到本地文件
- `check_and_extract_key_info()`: 检测并执行关键信息提取
- `search_chat_history()`: 搜索聊天历史记录
- `should_search_chat_history()`: 检测搜索触发条件
- 自动创建目录和文件：确保日志文件路径存在

## 技术栈

- **Python 3.12+**
- **标准库**：http.client, json, os, time, sys
- **API协议**：OpenAI兼容协议

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

## 学习路径

1. **入门阶段**：完成Practice 01，理解LLM API的基本调用方式
2. **进阶阶段**：完成Practice 02，掌握流式处理和状态管理
3. **优化阶段**：完成Practice 03，学习对话历史管理和token优化
4. **实战阶段**：基于现有代码开发自己的AI智能体应用

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

A: 在`practice03/chat_client.py`的`check_and_summarize()`函数中修改`max_rounds`（默认5轮）和`max_length`（默认3000字符）参数。

### Q: 压缩后的对话会影响上下文理解吗？

A: 压缩会保留关键信息的总结，但可能会丢失一些细节。系统保留了最近30%的原始对话，确保当前上下文的完整性。

## 贡献指南

欢迎提交Issue和Pull Request来改进这个教学项目。

## 许可证

本项目仅用于教学目的。

## 联系方式

如有问题或建议，欢迎通过Issue进行交流。