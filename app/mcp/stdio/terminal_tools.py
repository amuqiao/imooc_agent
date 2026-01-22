#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
终端控制工具，通过直接执行命令实现对macOS的控制
"""

import re
import subprocess
from typing import List, Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

# 创建FastMCP实例
mcp = FastMCP()


def clean_bash_tags(s):
    """清除markdown中的bash/shell标签"""
    # 同时匹配开头和结尾的标记及周围可能的空白（包括换行符）
    s = re.sub(r'^\s*```bash\s*', '', s, flags=re.DOTALL)  # 去开头
    s = re.sub(r'^\s*```shell\s*', '', s, flags=re.DOTALL)  # 去开头
    s = re.sub(r'\s*```\s*$', '', s, flags=re.DOTALL)      # 去结尾
    return s.strip()


@mcp.tool(name="run_command", description="执行命令并返回结果")
def run_command(
    command: Annotated[str, Field(description="要执行的命令", example="ls -la")],
    capture_output: Annotated[bool, Field(description="是否捕获命令输出", example=True)] = True,
    shell: Annotated[bool, Field(description="是否使用shell执行命令", example=True)] = True
) -> str:
    """
    执行命令并返回结果

    Args:
        command: 要执行的命令
        capture_output: 是否捕获命令输出
        shell: 是否使用shell执行命令

    Returns:
        str: 命令执行结果或错误信息
    """
    try:
        command = clean_bash_tags(command)
        print(f"\n执行命令: {command}")

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
    path: Annotated[str, Field(description="目录路径", example=".")] = "."
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


@mcp.tool(name="create_directory", description="创建目录")
def create_directory(
    path: Annotated[str, Field(description="要创建的目录路径", example="/tmp/test")]
) -> str:
    """
    创建目录

    Args:
        path: 要创建的目录路径

    Returns:
        str: 创建结果
    """
    try:
        import os
        os.makedirs(path, exist_ok=True)
        return f"目录 {path} 创建成功"
    except Exception as e:
        return f"创建目录失败: {str(e)}"


@mcp.tool(name="delete_file", description="删除文件")
def delete_file(
    path: Annotated[str, Field(description="要删除的文件路径", example="/tmp/test.txt")]
) -> str:
    """
    删除文件

    Args:
        path: 要删除的文件路径

    Returns:
        str: 删除结果
    """
    try:
        import os
        os.remove(path)
        return f"文件 {path} 删除成功"
    except Exception as e:
        return f"删除文件失败: {str(e)}"


if __name__ == "__main__":
    """
    启动MCP服务
    使用stdio传输协议，与Agent进行通信
    """
    try:
        print("终端工具服务已启动，等待Agent连接...")
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        print("终端工具服务已停止")
    except Exception as e:
        print(f"终端工具服务启动失败: {str(e)}")
