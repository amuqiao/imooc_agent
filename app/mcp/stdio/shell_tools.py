#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基于MCP协议的Shell工具服务
提供各种Shell命令执行功能，通过stdio与Agent通信
"""

import subprocess
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

# 创建FastMCP实例
mcp = FastMCP()


@mcp.tool(name="run_shell_command", description="执行Shell命令并返回结果")
def run_shell_command(
    command: Annotated[str, Field(description="要执行的Shell命令", example="ls -la")],
    capture_output: Annotated[
        bool, Field(description="是否捕获命令输出", example="True")
    ] = True,
    shell: Annotated[
        bool, Field(description="是否使用shell执行命令", example="True")
    ] = True,
) -> str:
    """
    执行Shell命令并返回结果

    Args:
        command: 要执行的Shell命令
        capture_output: 是否捕获命令输出
        shell: 是否使用shell执行命令

    Returns:
        str: 命令执行结果或错误信息
    """
    try:
        if capture_output:
            result = subprocess.run(
                command, shell=shell, capture_output=True, text=True, encoding="utf-8"
            )

            if result.returncode == 0:
                return f"命令执行成功:\n{result.stdout.strip()}"
            else:
                return f"命令执行失败 (返回码: {result.returncode}):\n{result.stderr.strip()}"
        else:
            subprocess.run(command, shell=shell, encoding="utf-8")
            return "命令已执行 (未捕获输出)"
    except Exception as e:
        return f"执行命令时发生错误: {str(e)}"


@mcp.tool(name="run_shell_script", description="执行Shell脚本文件")
def run_shell_script(
    script_path: Annotated[
        str, Field(description="脚本文件路径", example="/path/to/script.sh")
    ],
    args: Annotated[str, Field(description="脚本参数", example="arg1 arg2")] = "",
) -> str:
    """
    执行Shell脚本文件

    Args:
        script_path: 脚本文件路径
        args: 脚本参数

    Returns:
        str: 脚本执行结果或错误信息
    """
    try:
        command = f"chmod +x {script_path} && {script_path} {args}"
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, encoding="utf-8"
        )

        if result.returncode == 0:
            return f"脚本执行成功:\n{result.stdout.strip()}"
        else:
            return (
                f"脚本执行失败 (返回码: {result.returncode}):\n{result.stderr.strip()}"
            )
    except Exception as e:
        return f"执行脚本时发生错误: {str(e)}"


@mcp.tool(name="get_current_directory", description="获取当前工作目录")
def get_current_directory() -> str:
    """
    获取当前工作目录

    Returns:
        str: 当前工作目录路径
    """
    try:
        import os

        return os.getcwd()
    except Exception as e:
        return f"获取当前目录失败: {str(e)}"


@mcp.tool(name="list_directory", description="列出目录内容")
def list_directory(
    path: Annotated[str, Field(description="目录路径", example=".")] = ".",
) -> str:
    """
    列出目录内容

    Args:
        path: 目录路径

    Returns:
        str: 目录内容列表
    """
    try:
        command = f"ls -la {path}"
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, encoding="utf-8"
        )

        if result.returncode == 0:
            return f"目录 {path} 内容:\n{result.stdout.strip()}"
        else:
            return f"列出目录 {path} 失败:\n{result.stderr.strip()}"
    except Exception as e:
        return f"列出目录时发生错误: {str(e)}"


if __name__ == "__main__":
    """
    启动MCP服务
    使用stdio传输协议，与Agent进行通信
    """
    try:
        print("Shell工具服务已启动，等待Agent连接...")
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        print("Shell工具服务已停止")
    except Exception as e:
        print(f"Shell工具服务启动失败: {str(e)}")
