#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP客户端示例 - 使用stdio传输方式

测试math_mcp_server.py的stdio模式
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载项目根目录的 .env 文件
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
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
    
    # 获取当前文件的目录
    current_dir = Path(__file__).parent
    
    # 使用stdio模式连接MCP服务器
    server_params = StdioServerParameters(
        command="python",
        args=[str(current_dir / "math_mcp_server.py"), "--transport", "stdio"],
    )
    
    print("连接到MCP服务器（stdio模式）...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("MCP服务器连接成功！")
            
            # 加载MCP工具
            tools = await load_mcp_tools(session)
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


if __name__ == "__main__":
    asyncio.run(main())
