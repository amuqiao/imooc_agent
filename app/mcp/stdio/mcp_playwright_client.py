#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Playwright 客户端示例 - 使用stdio传输方式连接playwright-mcp-server

功能：直接使用Playwright工具操作真实浏览器完成以下任务：
1. 打开DuckDuckGo搜索结果页面
2. 获取"深圳今天天气"的搜索结果
3. 关闭浏览器
"""

import asyncio
import sys

# 设置Windows控制台编码为UTF-8
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools


async def main():
    """主函数：直接使用Playwright工具操作浏览器查询深圳天气"""
    print("=== MCP Playwright 客户端 - 浏览器自动化查询天气 ===\n")
    
    # 配置playwright MCP服务器参数（使用stdio方式）
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@executeautomation/playwright-mcp-server"],
    )
    
    print("正在连接到Playwright MCP服务器（stdio模式）...")
    
    # 初始化变量
    playwright_close_tool = None
    
    try:
        # 连接到MCP服务器
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("[OK] MCP服务器连接成功！")
                
                # 加载MCP工具
                tools = await load_mcp_tools(session)
                print(f"[OK] 加载了{len(tools)}个工具")
                
                # 创建工具字典，方便调用
                tools_dict = {tool.name: tool for tool in tools}
                
                # 获取所需工具
                navigate_tool = tools_dict.get('playwright_navigate')
                get_text_tool = tools_dict.get('playwright_get_visible_text')
                playwright_close_tool = tools_dict.get('playwright_close')
                print("\n" + "=" * 60)
                print("开始执行浏览器操作...")
                print("=" * 60 + "\n")
                
                # 1. 直接导航到DuckDuckGo搜索结果页面
                print("1. 直接导航到DuckDuckGo搜索结果页面...")
                if navigate_tool:
                    # 直接使用包含搜索关键词的URL
                    search_url = "https://duckduckgo.com/?q=深圳今天天气"
                    await navigate_tool.arun({"url": search_url, "timeout": 60000})
                    print("[OK] 已成功导航到DuckDuckGo搜索结果页面")
                    # 等待页面加载完成
                    await asyncio.sleep(3)
                else:
                    print("[ERROR] 未找到导航工具")
                    return
                
                # 2. 等待搜索结果加载
                print("2. 等待搜索结果加载完成...")
                await asyncio.sleep(2)  # 再等待2秒确保页面完全加载
                
                # 3. 获取搜索结果
                print("3. 获取搜索结果...")
                if get_text_tool:
                    try:
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
                    except Exception as e:
                        print(f"[ERROR] 获取搜索结果失败：{e}")
                        import traceback
                        traceback.print_exc()
                else:
                    print("[ERROR] 未找到获取文本工具")
                    return
                
                print("\n" + "=" * 60)
                print("任务执行完成！")
                print("=" * 60)
                
    except Exception as e:
        print(f"\n[ERROR] 执行过程中发生错误：{e}")
        import traceback
        traceback.print_exc()
    finally:
        # 确保浏览器关闭
        if playwright_close_tool:
            print("\n正在关闭浏览器...")
            try:
                await playwright_close_tool.arun({})
                print("[OK] 浏览器已成功关闭")
            except Exception as close_error:
                print(f"[ERROR] 关闭浏览器时发生错误：{close_error}")


if __name__ == "__main__":
    asyncio.run(main())