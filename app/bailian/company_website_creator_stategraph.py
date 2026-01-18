#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实战：利用Python REPL + LangChain 1.2.4 最新 Agent 架构开发企业官网
✅ 使用 StateGraph 新架构 | ✅ 无需 langchain_classic | ✅ 自动生成+执行代码
"""
# ===================== 全部正确的导入（最新 LangChain 1.2.4 方案） =====================
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载项目根目录的 .env 文件
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

from langchain_openai import ChatOpenAI
from langchain_experimental.tools.python.tool import PythonREPLTool
from pydantic import SecretStr


# ===================== 1. 初始化大模型 (完全保留你的配置，一行未改) =====================
def init_llm():
    """初始化通义千问大模型"""
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("环境变量 DASHSCOPE_API_KEY 未设置，请在 .env 文件中配置")
    
    return ChatOpenAI(
        model="qwen-plus",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=SecretStr(api_key),
        temperature=0,
        max_tokens=2048
    )


# ===================== 2. 创建Python代码执行工具 (完全保留，一行未改) =====================
def create_repl_tool():
    """创建Python REPL工具，支持执行任意Python代码/文件读写"""
    return PythonREPLTool()


# ===================== 3. 创建智能体 (使用最新 LangChain 1.2.4 StateGraph 架构) =====================
def create_new_agent(llm, tools):
    """创建基于 StateGraph 的新架构智能体"""
    from langchain import agents
    
    # 使用最新的 create_agent API (基于 StateGraph)
    agent_graph = agents.create_agent(
        model=llm,
        tools=tools,
        system_prompt="你是一个有用的助手，你可以使用Python代码来执行任务。请帮助用户完成以下任务：\n\n"
                      "请按照以下步骤进行：\n"
                      "1. 分析任务需求\n"
                      "2. 编写Python代码来完成任务\n"
                      "3. 执行代码\n"
                      "4. 返回执行结果和最终答案\n\n"
                      "注意：\n"
                      "- 直接返回Python代码，不要添加 ```python 或 ```py 等标记\n"
                      "- 代码应该完整、可执行，并且能够正确完成任务\n"
                      "- 确保代码中包含适当的错误处理\n"
                      "- 写入文件时必须指定utf-8编码，防止中文乱码\n"
                      "- 生成HTML/CSS代码时，使用标准的CSS语法，CSS选择器使用单大括号 {}，不要使用双大括号 {{}}"
    )
    return agent_graph


# ===================== 主函数 (使用新架构 API) =====================
def main():
    """主函数：一键执行【大模型生成代码 → Agent自动执行 → 验证文件】"""
    print("=== 利用Python REPL开发企业官网 (LangChain 1.2.4 新架构版) ===")
    
    # 初始化组件
    llm = init_llm()
    repl_tool = create_repl_tool()
    print("✓ 大模型初始化完成")
    print("✓ Python REPL工具创建完成")
    
    # 绑定工具+创建智能体（使用新架构）
    tools = [repl_tool]
    agent_graph = create_new_agent(llm, tools)
    print("✓ 智能体创建完成 (使用最新 StateGraph 架构)")
    
    # 你的原需求，完全不变
    input_text = "向/Users/wangqiao/Downloads/github_project/imooc_agent/.temp目录下写入一个新文件，名称为：index.html，并写一个企业的官网，包含标题、导航栏、关于我们、服务、联系我们等部分"

    # 🔥 核心：使用新架构的 stream 方法执行
    print("\n执行大模型生成Python代码并自动执行...")
    try:
        # 准备输入数据（新架构使用不同的输入格式）
        inputs = {
            "messages": [
                {"role": "user", "content": input_text}
            ]
        }
        
        # 执行智能体
        print("开始执行智能体...")
        for chunk in agent_graph.stream(inputs, stream_mode="updates"):
            if chunk:
                print(chunk)
        
        # 验证文件
        file_path = "/Users/wangqiao/Downloads/github_project/imooc_agent/.temp/index.html"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if os.path.exists(file_path):
            print(f"\n✓ 文件创建成功：{file_path}")
            print(f"文件大小：{os.path.getsize(file_path)} 字节")
        else:
            print(f"\n✗ 文件创建失败：{file_path}")
    except Exception as e:
        print(f"执行出错：{e}")


if __name__ == "__main__":
    main()