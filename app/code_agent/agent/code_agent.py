#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
代码智能体主程序
实现多轮对话的代码智能体，集成文件操作和shell工具
"""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from pydantic import SecretStr

# 导入 RAG 相关函数
from app.code_agent.rag.rag import create_client, retrieve_index

# 导入自定义工具
from app.code_agent.tools.file_saver import (  # 仅导入需要的文件工具
    append_file,
    get_file_content,
    save_file,
)
from app.code_agent.tools.file_tools import (
    get_stdio_file_tools,  # 导入文件工具获取函数
)
from app.code_agent.tools.powershell_tools import (
    get_stdio_powershell_tools,  # 导入PowerShell工具获取函数
)
from app.code_agent.tools.terminal_tools import (
    get_stdio_terminal_tools,  # 导入终端工具获取函数
)
from app.code_agent.tools.rag_tools import (
    get_stdio_rag_tools,  # 导入RAG工具获取函数
)

# 注释掉shell_tools，暂时不使用
# from app.code_agent.tools.shell_tools import (
#     get_stdio_shell_tools,  # 导入shell工具获取函数
# )

# 加载环境变量
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


def init_llm():
    """
    初始化大模型
    参考agent_multi_turn_conversation.py中的init_llm函数实现
    """
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


async def run_agent():
    """
    运行代码智能体，实现多轮对话交互
    """
    try:
        # 1. 初始化语言模型
        try:
            llm_qwen = init_llm()
            print("成功初始化语言模型")
        except Exception as e:
            print(f"错误：初始化语言模型失败 - {str(e)}")
            return

        # 2. 初始化工具列表
        # 2.1 基础文件工具
        file_tools = [save_file, append_file, get_file_content]

        # 2.2 获取MCP文件工具（通过MCP协议连接到外部文件工具服务）
        try:
            mcp_file_tools = await get_stdio_file_tools()
            print(f"成功加载 {len(mcp_file_tools)} 个MCP文件工具")
        except Exception as e:
            print(f"警告：加载MCP文件工具失败 - {str(e)}")
            mcp_file_tools = []

        # 2.3 获取PowerShell工具（通过MCP协议连接到外部PowerShell工具服务）
        try:
            powershell_tools = await get_stdio_powershell_tools()
            print(f"成功加载 {len(powershell_tools)} 个PowerShell工具")
        except Exception as e:
            print(f"警告：加载PowerShell工具失败 - {str(e)}")
            powershell_tools = []

        # 2.4 获取终端工具（通过MCP协议连接到外部终端工具服务）
        try:
            terminal_tools = await get_stdio_terminal_tools()
            print(f"成功加载 {len(terminal_tools)} 个终端工具")
        except Exception as e:
            print(f"警告：加载终端工具失败 - {str(e)}")
            terminal_tools = []

        # 2.5 获取RAG工具（通过MCP协议连接到外部RAG工具服务）
        try:
            rag_tools = await get_stdio_rag_tools()
            print(f"成功加载 {len(rag_tools)} 个RAG工具")
        except Exception as e:
            print(f"警告：加载RAG工具失败 - {str(e)}")
            rag_tools = []

        # 注释掉shell_tools，暂时不使用
        # 2.5 获取shell工具（通过MCP协议连接到外部shell工具服务）
        # try:
        #     shell_tools = await get_stdio_shell_tools()
        #     print(f"成功加载 {len(shell_tools)} 个shell工具")
        # except Exception as e:
        #     print(f"警告：加载shell工具失败 - {str(e)}")
        #     shell_tools = []

        # 2.6 合并所有工具
        all_tools = file_tools + mcp_file_tools + powershell_tools + terminal_tools + rag_tools

        if not all_tools:
            print("错误：未加载到任何工具")
            return

        # 3. 初始化记忆存储 (使用FileSaver作为checkpointer)
        # 注意：这里需要根据实际情况替换为正确的记忆初始化代码
        memory = None  # 示例：memory = FileSaver()

        # 4. 创建自定义提示词，明确告诉智能体在使用任何工具之前都必须先使用 RAG 工具获取相关知识
        react_prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个代码智能体，负责处理用户的各种请求。\n\n**强制性要求：在使用任何工具之前，你必须先使用 RAG 工具获取相关的知识**。这是绝对必须执行的步骤，没有例外。无论你认为自己是否已经知道答案，都必须先使用 RAG 工具获取最新的相关知识。\n\n**严格使用步骤：**\n1. 首先，分析用户的请求，确定需要获取哪些相关知识\n2. 然后，使用 RAG 工具（工具名称：query_rag_from_bailian）获取相关知识，将用户的请求作为查询参数传递给 RAG 工具\n3. 接着，根据获取到的知识和用户的请求，决定下一步操作\n4. 最后，使用适当的工具完成用户的请求\n\n**重要注意事项：**\n- 必须先使用 RAG 工具，然后才能使用其他工具\n- 获取到的知识将作为你决策和执行的基础\n- 如果 RAG 工具没有返回相关信息，你可以根据自己的知识来处理任务\n- 你必须在思考过程中明确说明你使用了 RAG 工具获取知识，以及获取到了哪些知识\n- 无论用户的请求是什么，你都必须先使用 RAG 工具获取相关知识，然后才能使用其他工具"),
            ("user", "{messages}")
        ])

        # 5. 创建React智能体
        agent = create_react_agent(
            model=llm_qwen, tools=all_tools, checkpointer=memory, debug=False, prompt=react_prompt
        )

        print("代码智能体已初始化完成，输入'exit'退出")
        print("=" * 50)

        # 5. 多轮对话循环
        thread_id = "2"  # 示例线程ID，可根据实际情况生成
        while True:
            # 获取用户输入
            user_input = input("用户： ")

            # 检查退出条件
            if user_input.lower() == "exit":
                print("智能体会话已结束")
                break

            try:
                # 1. 从阿里云百炼知识库中读取知识
                rag_knowledge = ""
                try:
                    # 创建百炼客户端
                    bailian_client = create_client()

                    # 从环境变量获取配置
                    workspace_id = os.getenv('workspace_id')
                    index_id = os.getenv('knowledge_base_id')

                    # 验证配置
                    if workspace_id and index_id:
                        # 查询知识库
                        rag = retrieve_index(bailian_client, workspace_id, index_id, user_input)

                        # 处理查询结果
                        if rag.body and hasattr(rag.body, 'data') and rag.body.data:
                            if hasattr(rag.body.data, 'nodes') and rag.body.data.nodes:
                                # 拼接查询结果
                                result = ""
                                index = 1
                                for data in rag.body.data.nodes:
                                    result += f"第{index}段知识：\n    {data.text}\n    --\n    "
                                    index += 1
                                rag_knowledge = result
                                # 打印 RAG 工具的结果
                                print("\n=== RAG 知识库查询结果 ===")
                                print(rag_knowledge)
                                print("=========================\n")
                except Exception as e:
                    print(f"RAG 查询失败: {str(e)}")

                # 2. 准备配置
                config = RunnableConfig(configurable={"thread_id": thread_id})

                # 3. 构建带有 RAG 知识的输入
                if rag_knowledge:
                    # 如果有 RAG 知识，将其拼接到提示词中
                    rag_enhanced_input = f"用户问题：{user_input}\n\n相关知识：\n{rag_knowledge}"
                else:
                    # 如果没有 RAG 知识，使用原始输入
                    rag_enhanced_input = user_input

                # 4. 调用智能体处理用户请求
                response = await agent.ainvoke(
                    input={"messages": rag_enhanced_input}, config=config
                )

                # 输出智能体响应
                if response and "messages" in response and response["messages"]:
                    print(f"助理： {response['messages'][-1].content}")
                else:
                    print("助理： 未获取到有效响应")

            except Exception as e:
                print(f"错误：处理用户请求时发生异常 - {str(e)}")

            print("=" * 50)

    except Exception as e:
        print(f"严重错误：智能体运行失败 - {str(e)}")


if __name__ == "__main__":
    """
    程序入口
    """
    asyncio.run(run_agent())
