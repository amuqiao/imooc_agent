#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Playwright 客户端 - v2 版本
使用 LangGraph 和 MCP 连接 Playwright 服务器，查询天气信息
"""

import asyncio
import os
import sys

# 设置Windows控制台编码为UTF-8
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# 修复导入问题，直接初始化LLM而不是从common模块导入
from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from langchain_core.messages import HumanMessage, AIMessage
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent


# ===================== 初始化LLM =====================
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


async def main():
    """主函数：使用MCP Playwright客户端查询天气"""
    print("=== MCP Playwright 客户端 - v2 版本 ===\n")
    
    try:
        # 1. 初始化LLM
        llm = init_llm()
        print("[OK] LLM初始化完成")
        
        # 2. 定义mcp参数
        server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@executeautomation/playwright-mcp-server"],
        )
        
        print("正在连接到Playwright MCP服务器...")
        
        # 3. 实例化stdio_client
        async with stdio_client(server_params) as (read, write):
            # 4. 创建session
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("[OK] MCP服务器连接成功！")
                
                # 5. 读取mcp tools配置
                tools = await load_mcp_tools(session)  # 自动加载MCP服务器提供的工具
                print(f"[OK] 加载了{len(tools)}个工具")
                
                # 6. 定义agent
                agent = create_react_agent(llm, tools)  # 创建React Agent
                print("[OK] Agent创建成功！")
                
                # 7. 调用agent
                print("\n[INFO] 开始查询南京今天的天气...")
                response = await agent.ainvoke(
                    input={"messages": [("user", "使用DuckDuckGo查询南京今天的天气")]}
                )
                
                # 8. 打印调用过程和结果
                print("\n" + "=" * 60)
                print("执行结果：")
                print("=" * 60)
                
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
                
                print("\n" + "=" * 60)
                print("查询完成！")
                print("=" * 60)
                
    except Exception as e:
        print(f"\n[ERROR] 执行出错：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())