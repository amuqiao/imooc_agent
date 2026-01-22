#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MCP (Multi-Component Protocol) 工具公共方法
提供 MCP 客 户端创建和管理功能
"""

from typing import Any, Dict, Tuple

from langchain_mcp_adapters.client import MultiServerMCPClient


async def create_mcp_stdio_client(
    name: str, params: Dict[str, Any] = None
) -> Tuple[MultiServerMCPClient, list]:
    """
    创建基于标准输入输出的 MCP 客户端

    Args:
        name: 客户端名称
        params: 额外配置参数

    Returns:
        Tuple[MultiServerMCPClient, list]: MCP 客户端实例和可用工具列表

    Example:
        client, tools = await create_mcp_stdio_client("test_client")
    """
    # 初始化默认参数
    params = params or {}

    # 构建配置，移除name参数，因为_create_stdio_session不接受它
    config = {"transport": "stdio", **params}

    # 创建客户端实例
    client = MultiServerMCPClient({name: config})

    # 获取工具列表
    tools = await client.get_tools()

    return client, tools
