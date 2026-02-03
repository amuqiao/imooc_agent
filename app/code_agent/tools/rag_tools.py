#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RAG 工具获取函数
"""

import os
from app.code_agent.utils.mcp import create_mcp_stdio_client


async def get_stdio_rag_tools():
    """
    获取基于stdio的RAG工具列表

    Returns:
        list: 可用的RAG工具列表
    """
    try:
        # 使用动态路径，确保在不同操作系统上都能正确找到文件
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        rag_tools_path = os.path.join(script_dir, "app", "code_agent", "mcp", "rag.py")

        # 配置MCP客户端参数
        params = {
            "command": "python",
            "args": [
                rag_tools_path
            ]
        }

        # 创建MCP客户端并获取工具列表
        client, tools = await create_mcp_stdio_client("rag", params)

        return tools
    except Exception as e:
        print(f"获取RAG工具失败: {str(e)}")
        return []
