#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实战：利用Python REPL + LangChain 1.2.4 Agent 开发企业官网
✅ 彻底解决导入报错 | ✅ 无需降级 | ✅ 改动最小 | ✅ 自动生成+执行代码
"""
# ===================== 全部正确的导入（核心修复，必看） =====================
import os
from langchain_openai import ChatOpenAI
from langchain_experimental.tools.python.tool import PythonREPLTool
from pydantic import SecretStr
from langchain_core.prompts import PromptTemplate

# ✅✅✅ LangChain 1.2.4 正确导入 - 解决所有报错 ✅✅✅
from langchain_classic.agents import AgentExecutor
from langchain_classic.agents import create_tool_calling_agent


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
        max_tokens=2048,
    )


# ===================== 2. 创建Python代码执行工具 (完全保留，一行未改) =====================
def create_repl_tool():
    """创建Python REPL工具，支持执行任意Python代码/文件读写"""
    return PythonREPLTool()


# ===================== 3. 创建提示模板 (完全保留你的需求约束，一行未改) =====================
def create_prompt_template():
    """创建适配工具调用Agent的提示词，精准约束代码生成规则"""
    return PromptTemplate.from_template(
        template="""你是一个有用的助手，你可以使用Python代码来执行任务。请帮助用户完成以下任务：

任务：{input}

请按照以下步骤进行：
1. 分析任务需求
2. 编写Python代码来完成任务
3. 执行代码
4. 返回执行结果和最终答案

注意：
- 直接返回Python代码，不要添加 ```python 或 ```py 等标记
- 代码应该完整、可执行，并且能够正确完成任务
- 确保代码中包含适当的错误处理
- 写入文件时必须指定utf-8编码，防止中文乱码

{agent_scratchpad}
"""
    )


# ===================== 4. 创建智能体 (仅1行适配修改，其余不变) =====================
def create_code_exec_agent(llm, tools, prompt):
    """创建代码执行专属智能体"""
    # ✅ 仅这里有1个微小适配：1.2.4的create_tool_calling_agent需要显式传tools
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent, tools=tools, verbose=True, handle_parsing_errors=True
    )
    return agent_executor


# ===================== 主函数 (完全保留你的所有逻辑，一行未改) =====================
def main():
    """主函数：一键执行【大模型生成代码 → Agent自动执行 → 验证文件】"""
    print("=== 利用Python REPL开发企业官网 (LangChain 1.2.4 修复版) ===")

    # 初始化组件
    llm = init_llm()
    repl_tool = create_repl_tool()
    prompt_template = create_prompt_template()
    print("✓ 大模型初始化完成")
    print("✓ Python REPL工具创建完成")
    print("✓ 提示模板创建完成")

    # 绑定工具+创建智能体
    tools = [repl_tool]
    agent_executor = create_code_exec_agent(llm, tools, prompt_template)

    # 你的原需求，完全不变
    input_text = "向/Users/wangqiao/Downloads/github_project/imooc_agent/.temp目录下写入一个新文件，名称为：index.html，并写一个企业的官网，包含标题、导航栏、关于我们、服务、联系我们等部分"

    # 🔥 核心：全自动执行，无需手动提取python_code
    print("\n执行大模型生成Python代码并自动执行...")
    try:
        agent_executor.invoke({"input": input_text})

        # 验证文件
        file_path = (
            "/Users/wangqiao/Downloads/github_project/imooc_agent/.temp/index.html"
        )
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
