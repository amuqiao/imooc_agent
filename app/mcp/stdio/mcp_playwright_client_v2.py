#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Playwright 客户端 - v2 版本
使用 LangGraph 和 MCP 连接 Playwright 服务器，查询天气信息
"""

import asyncio
import os
import sys
from pathlib import Path

# 加载环境变量
from dotenv import load_dotenv
# 加载项目根目录的 .env 文件
env_path = Path(__file__).parent.parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

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
    # 使用默认API密钥作为备选，避免环境变量未设置时直接失败
    api_key = os.getenv("DASHSCOPE_API_KEY", "sk-7033a12030f74a92930d89739e123c8e")
    
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
    
    # 初始化变量
    playwright_close_tool = None
    
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
                
                # 创建工具字典，方便直接调用
                tools_dict = {tool.name: tool for tool in tools}
                
                # 获取所需工具
                playwright_close_tool = tools_dict.get('playwright_close')
                
                print("\n" + "=" * 60)
                print("开始执行浏览器操作...")
                print("=" * 60 + "\n")
                
                try:
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
                except Exception as tool_error:
                    print(f"\n[WARNING] 工具调用出错：{str(tool_error)[:200]}")
                    print("[INFO] 尝试直接使用Playwright工具进行查询...")
                    
                    # 参考v1版本，直接使用Playwright工具
                    navigate_tool = tools_dict.get('playwright_navigate')
                    fill_tool = tools_dict.get('playwright_fill')
                    press_key_tool = tools_dict.get('playwright_press_key')
                    get_text_tool = tools_dict.get('playwright_get_visible_text')
                    
                    if navigate_tool and fill_tool and press_key_tool and get_text_tool:
                        # 直接使用工具执行查询，参考v1版本的操作流程
                        print("1. 导航到DuckDuckGo主页...")
                        await navigate_tool.arun({"url": "https://duckduckgo.com", "timeout": 60000})
                        print("[OK] 已成功导航到DuckDuckGo主页")
                        await asyncio.sleep(1)
                        
                        print("2. 在搜索框中输入'南京今天天气'...")
                        await fill_tool.arun({"selector": "#searchbox_input", "value": "南京今天天气", "timeout": 30000})
                        print("[OK] 搜索内容输入完成")
                        await asyncio.sleep(1)
                        
                        print("3. 按下回车键执行搜索...")
                        await press_key_tool.arun({"key": "Enter", "timeout": 30000})
                        print("[OK] 搜索已执行")
                        await asyncio.sleep(3)  # 等待搜索结果加载
                        
                        print("4. 获取搜索结果...")
                        result = await get_text_tool.arun({"timeout": 60000})
                        print("[OK] 搜索结果获取成功")
                        
                        # 处理并显示结果
                        print("\n" + "=" * 60)
                        print("搜索结果摘要：")
                        print("=" * 60)
                        
                        # 处理结果文本
                        result_text = ""
                        if isinstance(result, str):
                            result_text = result
                        elif isinstance(result, list):
                            # 处理列表类型的结果
                            for item in result:
                                if isinstance(item, dict) and 'text' in item:
                                    result_text += item['text'] + '\n'
                                elif isinstance(item, str):
                                    result_text += item + '\n'
                        else:
                            result_text = str(result)
                        
                        # 显示结果
                        if result_text:
                            # 只显示前2000个字符
                            print(f"\n{result_text[:2000]}...")
                        else:
                            print("\n未获取到有效结果")
                        
                        print("\n" + "=" * 60)
                        print("查询完成！")
                        print("=" * 60)
                    else:
                        print("[ERROR] 缺少必要的Playwright工具")
                        return
                
    except Exception as e:
        print(f"\n[ERROR] 执行出错：{e}")
        import traceback
        traceback.print_exc()
    finally:
        # 确保浏览器关闭，参考v1版本的资源管理
        if playwright_close_tool:
            print("\n正在关闭浏览器...")
            try:
                await playwright_close_tool.arun({})
                print("[OK] 浏览器已成功关闭")
            except Exception as close_error:
                # 忽略重复关闭错误，因为Agent可能已经关闭了浏览器
                if str(close_error).strip():
                    print(f"[ERROR] 关闭浏览器时发生错误：{close_error}")
                else:
                    print("[INFO] 浏览器可能已被Agent关闭，忽略关闭操作")


if __name__ == "__main__":
    asyncio.run(main())