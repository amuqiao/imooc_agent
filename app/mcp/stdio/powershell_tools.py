#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基于MCP协议的PowerShell工具服务
提供各种PowerShell操作功能，通过stdio与Agent通信
"""

import os
import subprocess
import time
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

# 创建FastMCP实例
mcp = FastMCP()


def run_powershell_command(command: str, capture_output: bool = True):
    """执行 PowerShell 命令"""
    try:
        # 使用 PowerShell 执行命令
        cmd = ["powershell", "-Command", command]
        if capture_output:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.stdout.strip(), result.stderr.strip(), result.returncode
        else:
            result = subprocess.run(cmd)
            return "", "", result.returncode
    except Exception as e:
        return "", str(e), 1


def get_powershell_processes():
    """获取所有 PowerShell 进程"""
    processes = []
    try:
        # 使用 PowerShell 命令获取进程信息
        cmd = "Get-Process powershell | Select-Object Id, ProcessName | ConvertTo-Json"
        stdout, stderr, returncode = run_powershell_command(cmd)
        if returncode == 0 and stdout:
            import json

            # 解析 JSON 输出
            process_list = json.loads(stdout)
            # 处理单个进程和多个进程的情况
            if isinstance(process_list, list):
                for proc in process_list:
                    processes.append(
                        {
                            "pid": proc["Id"],
                            "name": proc["ProcessName"],
                            "cmdline": [],
                        }
                    )
            elif isinstance(process_list, dict):
                processes.append(
                    {
                        "pid": process_list["Id"],
                        "name": process_list["ProcessName"],
                        "cmdline": [],
                    }
                )
    except Exception as e:
        # 如果 JSON 解析失败或命令执行失败，返回空列表
        pass
    return processes


def activate_powershell_window():
    """激活 PowerShell 窗口"""
    # 此功能需要 pyautogui 模块，已移除依赖
    return False


@mcp.tool(name="get_powershell_processes", description="获取所有 PowerShell 进程信息")
def get_all_powershell_processes() -> str:
    """获取所有正在运行的 PowerShell 进程列表"""
    try:
        processes = get_powershell_processes()
        if not processes:
            return "当前没有运行的 PowerShell 进程"

        result = "PowerShell 进程列表:\n"
        for proc in processes:
            result += f"PID: {proc['pid']}, 名称: {proc['name']}\n"
        return result
    except Exception as e:
        return f"获取 PowerShell 进程失败: {str(e)}"


@mcp.tool(name="close_powershell", description="关闭所有 PowerShell 进程")
def close_all_powershell() -> str:
    """关闭所有 PowerShell 进程"""
    try:
        # 使用 PowerShell 命令关闭所有 PowerShell 进程
        cmd = "Get-Process powershell | Stop-Process -Force"
        stdout, stderr, returncode = run_powershell_command(cmd)

        # 检查是否还有 PowerShell 进程在运行
        processes = get_powershell_processes()
        if not processes:
            return "已成功关闭所有 PowerShell 进程"
        else:
            return f"关闭 PowerShell 进程后，仍有 {len(processes)} 个进程在运行"
    except Exception as e:
        return f"关闭 PowerShell 进程失败: {str(e)}"


@mcp.tool(name="open_powershell", description="打开新的 PowerShell 窗口")
def open_new_powershell(
    working_directory: Annotated[
        str,
        Field(description="可选的工作目录，为空则使用当前目录", examples="C:\\Users"),
    ] = "",
) -> str:
    """打开新的 PowerShell 窗口"""
    try:
        if working_directory and os.path.exists(working_directory):
            # 在指定目录打开 PowerShell
            command = (
                f'Start-Process powershell -WorkingDirectory "{working_directory}"'
            )
        else:
            # 在当前目录打开 PowerShell
            command = "Start-Process powershell"

        stdout, stderr, returncode = run_powershell_command(
            command, capture_output=False
        )

        if returncode != 0 and stderr:
            return f"打开 PowerShell 失败: {stderr}"

        time.sleep(2)  # 等待窗口打开
        processes = get_powershell_processes()
        return f"PowerShell 已打开，当前运行进程数: {len(processes)}"
    except Exception as e:
        return f"打开 PowerShell 失败: {str(e)}"


@mcp.tool(
    name="run_powershell_script",
    description="通过 pyautogui 向 PowerShell 窗口发送命令",
)
def run_powershell_script(
    script: Annotated[
        str,
        Field(
            description="要在 PowerShell 窗口中执行的脚本命令", examples="Get-Location"
        ),
    ],
) -> str:
    """通过 pyautogui 向活动的 PowerShell 窗口发送命令"""
    try:
        print("-" * 50)
        print("run_powershell_script (pyautogui):")
        print(script)
        print("-" * 50)

        return "run_powershell_script 功能需要 pyautogui 模块，当前环境未安装此模块。请使用 execute_powershell_command 工具直接执行 PowerShell 命令。"
    except Exception as e:
        return f"发送 PowerShell 命令失败: {str(e)}"


@mcp.tool(
    name="execute_powershell_command", description="直接执行 PowerShell 命令并返回结果"
)
def execute_powershell_command(
    command: Annotated[
        str, Field(description="要执行的 PowerShell 命令", examples="Get-Process")
    ],
) -> str:
    """直接执行 PowerShell 命令并返回结果（不通过 GUI）"""
    try:
        print("-" * 50)
        print("execute_powershell_command:")
        print(command)
        print("-" * 50)

        stdout, stderr, returncode = run_powershell_command(command)

        if returncode != 0:
            if stderr:
                return f"命令执行失败: {stderr}"
            else:
                return "命令执行失败，但没有错误信息"

        if stdout:
            return f"命令执行成功:\n{stdout}"
        else:
            return "命令执行成功，但没有输出"
    except Exception as e:
        return f"执行 PowerShell 命令失败: {str(e)}"


if __name__ == "__main__":
    """启动MCP PowerShell工具服务"""
    try:
        print("PowerShell工具服务已启动，等待Agent连接...")
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        print("PowerShell工具服务已停止")
    except Exception as e:
        print(f"PowerShell工具服务启动失败: {str(e)}")
