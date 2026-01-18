#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP客户端示例 - 使用sse传输方式

测试math_mcp_server.py的sse模式
"""

import asyncio
import os
import subprocess
import time
from pathlib import Path
from dotenv import load_dotenv

# 加载项目根目录的 .env 文件
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from pydantic import SecretStr


def init_llm():
    """初始化通义千问大模型"""
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("环境变量 DASHSCOPE_API_KEY 未设置，请在 .env 文件中配置")
    
    return ChatOpenAI(
        model="qwen-plus",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=SecretStr(api_key),
        streaming=True,
    )


async def start_server():
    """启动MCP服务器（sse模式）"""
    # 获取当前文件的目录
    current_dir = Path(__file__).parent

    # 启动服务器进程，移除不支持的--port参数
    server_process = subprocess.Popen(
        ["python", str(current_dir / "math_mcp_server.py"), "--transport", "sse"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # 等待服务器启动
    time.sleep(2)

    return server_process


async def main():
    """主函数"""
    # 启动MCP服务器
    server_process = await start_server()

    try:
        # 初始化LLM
        llm = init_llm()

        print("连接到MCP服务器（sse模式）...")

        # 使用MultiServerMCPClient连接MCP服务器
        client = MultiServerMCPClient(
            {
                "math": {
                    "url": "http://127.0.0.1:8000/sse",
                    "transport": "sse",
                }
            }
        )

        # 加载MCP工具
        tools = await client.get_tools()
        print(f"加载了{len(tools)}个工具：{[tool.name for tool in tools]}")

        # 创建React Agent
        agent = create_react_agent(llm, tools)
        print("Agent创建成功！")

        # 调用Agent
        user_input = "what's (3 + 5) x 12?"
        print(f"\n用户输入：{user_input}")

        response = await agent.ainvoke(input={"messages": [("user", user_input)]})

        print(f"\nAgent响应：")
        for msg in response["messages"]:
            if hasattr(msg, "content") and msg.content:
                print(f"  {msg.content}")

    finally:
        # 终止服务器进程
        server_process.terminate()
        server_process.wait()
        print("\nMCP服务器已关闭")


if __name__ == "__main__":
    asyncio.run(main())
