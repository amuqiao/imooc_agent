#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP客户端示例 - 使用streamable_http传输方式

测试math_mcp_server.py的streamable_http模式（推荐使用）
"""

import asyncio
import os
import subprocess
import time
from pathlib import Path

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


async def main():
    """主函数"""
    # 初始化LLM
    llm = init_llm()
    
    print("连接到MCP服务器（streamable_http模式）...")
    
    # 使用MultiServerMCPClient连接已经运行的MCP服务器
    client = MultiServerMCPClient(
        {
            "math": {
                "url": "http://127.0.0.1:8000/mcp",
                "transport": "streamable_http",
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
    
    print("\n测试完成！")


if __name__ == "__main__":
    asyncio.run(main())
