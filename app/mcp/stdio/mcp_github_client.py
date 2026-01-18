#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP GitHub 客户端 - v2 版本
使用 LangGraph 和 MCP 连接 GitHub 服务器，查询 GitHub 仓库信息
"""

import asyncio
import sys
from pydantic_settings import BaseSettings

# 设置Windows控制台编码为UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except:
        pass

# 修复导入问题，直接初始化LLM
from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from langchain_core.messages import HumanMessage, AIMessage
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent


# ===================== 配置管理 =====================
class Settings(BaseSettings):
    """应用配置管理"""
    dashscope_api_key: SecretStr
    github_personal_access_token: str
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }


# ===================== 初始化LLM =====================
def init_llm(settings: Settings):
    """初始化通义千问大模型"""
    return ChatOpenAI(
        model="qwen-plus",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=settings.dashscope_api_key,
        temperature=0,
        max_tokens=2048,
    )


def print_result(response):
    """打印调用结果"""
    messages = response["messages"]
    for message in messages:
        if isinstance(message, HumanMessage):
            print(f"用户: {message.content}")
        elif isinstance(message, AIMessage):
            if message.content:
                print(f"助理: {message.content}")
            else:
                for tool_call in message.tool_calls:
                    print(f"调用工具: {tool_call['name']} {tool_call['args']}")


async def main():
    """主函数：使用MCP GitHub客户端查询仓库信息"""
    print("=== MCP GitHub 客户端 - v2 版本 ===\n")

    try:
        # 1. 加载配置
        settings = Settings()
        print("[OK] 配置加载完成")
        
        # 2. 初始化LLM
        llm = init_llm(settings)
        print("[OK] LLM初始化完成")

        # 3. 定义mcp参数
        server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-github"],
            env={"GITHUB_PERSONAL_ACCESS_TOKEN": settings.github_personal_access_token},
        )

        print("正在连接到GitHub MCP服务器...")

        # 4. 实例化stdio_client
        async with stdio_client(server_params) as (read, write):
            # 5. 创建session
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("[OK] MCP服务器连接成功！")

                # 6. 读取mcp tools配置
                tools = await load_mcp_tools(session)  # 自动加载MCP服务器提供的工具
                print(f"[OK] 加载了{len(tools)}个工具")

                # 7. 调用agent
                print("\n[INFO] 开始查询GitHub仓库...")
                response = await create_react_agent(
                    model=llm, tools=tools, debug=True
                ).ainvoke(input={"messages": [("user", "查询我有哪些代码仓库？我的用户名是amuqiao")]})

                # 8. 打印调用过程和结果
                print("\n" + "=" * 60)
                print("执行结果：")
                print("=" * 60)
                print_result(response)

                print("\n" + "=" * 60)
                print("查询完成！")
                print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] 执行出错：{e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())