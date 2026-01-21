#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shell命令执行工具集（FastMCP封装）
支持多种命令执行方式：
1. 一次性执行并返回全部输出
2. 实时流式输出
3. 安全的命令执行（避免shell注入）
4. 支持shell特性的命令执行
"""
import subprocess
from typing import Dict, Any, Optional, Annotated
from pydantic import Field

from mcp.server.fastmcp import FastMCP

# 创建FastMCP实例
mcp = FastMCP()


@mcp.tool(name="run_command_once", description="一次性执行命令并返回全部输出")
def run_command_once(
    command: Annotated[str, Field(description="要执行的命令", json_schema_extra={"example": "echo 'Hello World'"})],
    shell: Annotated[bool, Field(description="是否使用shell执行，支持管道等shell特性", default=True)] = True,
    timeout: Annotated[Optional[int], Field(description="命令执行超时时间（秒）", default=None)] = None
) -> str:
    """
    一次性执行命令并返回全部输出
    """
    process = subprocess.Popen(
        command, 
        shell=shell, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT, 
        text=True,
        encoding='utf-8'
    )
    output, _ = process.communicate(timeout=timeout)
    return output.rstrip("\n")


@mcp.tool(name="run_command_safe", description="安全执行命令（避免shell注入，不支持管道等shell特性）")
def run_command_safe(
    args: Annotated[list, Field(description="命令及其参数列表，如 ['echo', 'Hello']", json_schema_extra={"example": ["echo", "Hello"]})],
    capture_output: Annotated[bool, Field(description="是否捕获输出", default=True)] = True,
    text: Annotated[bool, Field(description="是否返回文本格式输出", default=True)] = True
) -> Dict[str, Any]:
    """
    安全执行命令（避免shell注入，不支持管道等shell特性）
    """
    result = subprocess.run(
        args, 
        capture_output=capture_output, 
        text=text,
        encoding='utf-8'
    )
    
    return {
        "returncode": result.returncode,
        "stdout": result.stdout.rstrip("\n") if result.stdout else "",
        "stderr": result.stderr.rstrip("\n") if result.stderr else ""
    }


@mcp.tool(name="run_command_with_shell", description="使用shell执行命令（支持管道、重定向等shell特性）")
def run_command_with_shell(
    command: Annotated[str, Field(description="要执行的命令字符串", json_schema_extra={"example": "echo 'Hello' | grep 'H'"})],
    capture_output: Annotated[bool, Field(description="是否捕获输出", default=True)] = True,
    text: Annotated[bool, Field(description="是否返回文本格式输出", default=True)] = True
) -> Dict[str, Any]:
    """
    使用shell执行命令（支持管道、重定向等shell特性）
    """
    result = subprocess.run(
        command, 
        shell=True, 
        capture_output=capture_output, 
        text=text,
        encoding='utf-8'
    )
    
    return {
        "returncode": result.returncode,
        "stdout": result.stdout.rstrip("\n") if result.stdout else "",
        "stderr": result.stderr.rstrip("\n") if result.stderr else ""
    }


# 启动FastMCP服务
if __name__ == "__main__":
    print("=== FastMCP Shell命令工具服务启动 ===")
    print("支持的工具：")
    # FastMCP实例没有直接的tools属性，直接列出工具名称
    tool_names = ["run_command_once", "run_command_safe", "run_command_with_shell"]
    for tool_name in tool_names:
        print(f"  - {tool_name}")
    print("\n服务运行中...")
    mcp.run(transport="stdio")
