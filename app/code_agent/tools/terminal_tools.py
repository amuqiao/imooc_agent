#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
终端工具获取模块，用于获取通过MCP协议连接的终端控制工具
"""

from app.code_agent.utils.mcp import create_mcp_stdio_client


async def get_stdio_terminal_tools():
    """
    获取通过MCP协议连接的终端控制工具

    Returns:
        list: 终端控制工具列表
    """
    try:
        # 使用动态路径，确保在不同操作系统上都能正确找到文件
        import os
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        terminal_tools_path = os.path.join(script_dir, "app", "mcp", "stdio", "terminal_tools.py")

        params = {
            "command": "python",
            "args": [
                terminal_tools_path,
            ],
        }

        client, tools = await create_mcp_stdio_client("terminal", params)

        return tools
    except Exception as e:
        print(f"获取终端工具失败: {str(e)}")
        return []
