#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PowerShell工具获取模块
负责获取基于stdio的PowerShell工具列表
"""

from app.code_agent.utils.mcp import create_mcp_stdio_client


async def get_stdio_powershell_tools():
    """
    获取基于stdio的PowerShell工具列表

    Returns:
        list: 可用的PowerShell工具列表
    """
    try:
        # 使用动态路径，确保在不同操作系统上都能正确找到文件
        import os
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        powershell_tools_path = os.path.join(script_dir, "app", "mcp", "stdio", "powershell_tools.py")

        # 配置MCP客户端参数
        params = {
            "command": "python",
            "args": [
                powershell_tools_path
            ]
        }

        # 创建MCP客户端并获取工具列表
        client, tools = await create_mcp_stdio_client("powershell_tools", params)

        return tools
    except Exception as e:
        print(f"获取PowerShell工具失败: {str(e)}")
        return []
