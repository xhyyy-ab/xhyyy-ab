# AI 智能体开发教学项目

基于Python的AI智能体开发教学项目，帮助学习者从基础到进阶掌握AI智能体的开发技术。

## 项目结构

```
trae_projects/
├── practice01/          # 练习1：基础LLM客户端
│   └── llm_client.py   # 简单的LLM API调用和性能统计
├── practice02/          # 练习2：交互式聊天客户端
│   └── chat_client.py  # 支持流式输出和历史记录的聊天系统
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

运行方式：
```bash
python practice02/chat_client.py
```

功能特点：
- 终端界面交互式对话
- 实时流式输出响应内容
- 自动维护对话历史记录
- 支持Ctrl+C中断当前响应
- 支持quit/exit命令退出
- 显示响应时间统计

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

## 学习路径

1. **入门阶段**：完成Practice 01，理解LLM API的基本调用方式
2. **进阶阶段**：完成Practice 02，掌握流式处理和状态管理
3. **实战阶段**：基于现有代码开发自己的AI智能体应用

## 常见问题

### Q: 如何连接到不同的LLM服务？

A: 修改`.env`文件中的`BASE_URL`和`MODEL`参数即可连接到不同的LLM服务。

### Q: 流式输出不工作怎么办？

A: 确保你的LLM服务支持流式输出（`stream: true`参数）。

### Q: 如何增加对话历史的长度限制？

A: 在`chat_client.py`中修改对话历史的处理逻辑，添加长度限制。

## 贡献指南

欢迎提交Issue和Pull Request来改进这个教学项目。

## 许可证

本项目仅用于教学目的。

## 联系方式

如有问题或建议，欢迎通过Issue进行交流。