#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP服务器示例 - 数学工具

支持三种传输方式：
1. stdio - 标准输入输出模式
2. sse - 服务器发送事件模式（已废弃，推荐使用streamable_http）
3. streamable_http - 流式HTTP模式（推荐使用）
"""

from mcp.server.fastmcp import FastMCP

# 创建MCP服务器实例
mcp = FastMCP("Math Tools")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b


@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    return a - b


@mcp.tool()
def divide(a: int, b: int) -> float:
    """Divide two numbers"""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


if __name__ == "__main__":
    import sys
    import argparse

    # 解析命令行参数，指定传输方式
    parser = argparse.ArgumentParser(description="MCP Math Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport method to use",
    )
    parser.add_argument(
        "--mount-path", type=str, default=None, help="Mount path for sse transport"
    )

    args = parser.parse_args()

    print(f"Starting MCP Math Server with {args.transport} transport")

    # 运行MCP服务器
    mcp.run(transport=args.transport, mount_path=args.mount_path)
