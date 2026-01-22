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
        # 配置MCP客户端参数
        params = {
            "command": "python",
            "args": [
                "E:\\github_project\\imooc_agent\\app\\mcp\\stdio\\powershell_tools.py"
            ]
        }

        # 创建MCP客户端并获取工具列表
        client, tools = await create_mcp_stdio_client("powershell_tools", params)

        return tools
    except Exception as e:
        print(f"获取PowerShell工具失败: {str(e)}")
        return []
