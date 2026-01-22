#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试PowerShell工具功能
"""

import asyncio
from app.code_agent.tools.powershell_tools import get_stdio_powershell_tools


async def test_powershell_tools():
    """
    测试PowerShell工具获取功能
    """
    print("开始测试PowerShell工具...")
    
    try:
        # 测试获取PowerShell工具列表
        tools = await get_stdio_powershell_tools()
        print(f"获取到 {len(tools)} 个PowerShell工具")
        
        for tool in tools:
            print(f"- {tool.name}: {tool.description}")
        
        return True
    except Exception as e:
        print(f"测试失败: {str(e)}")
        return False


if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_powershell_tools())