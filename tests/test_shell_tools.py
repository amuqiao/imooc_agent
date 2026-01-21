#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 shell_tools.py 中的功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 直接测试 run_command_once 函数
from app.code_agent.tools.test_tools import run_command_once

def test_run_command_once():
    """测试一次性执行命令功能"""
    print("=== 测试 shell_tools.py 功能 ===")
    
    # 测试1: 执行简单命令
    print("\n测试1: 执行 'ls -la' 命令")
    result = run_command_once("ls -la")
    print(f"命令输出: \n{result}")
    assert isinstance(result, str), "命令输出应该是字符串"
    assert len(result) > 0, "命令输出不应该为空"
    print("✓ 测试1通过: 简单命令执行成功")
    
    # 测试2: 执行 echo 命令
    print("\n测试2: 执行 'echo hello world' 命令")
    result = run_command_once("echo hello world")
    print(f"命令输出: {result}")
    assert result == "hello world", f"预期输出 'hello world'，实际输出 '{result}'"
    print("✓ 测试2通过: echo 命令执行成功")
    
    # 测试3: 执行 pwd 命令
    print("\n测试3: 执行 'pwd' 命令")
    result = run_command_once("pwd")
    print(f"命令输出: {result}")
    assert os.path.exists(result), f"当前目录 '{result}' 应该存在"
    print("✓ 测试3通过: pwd 命令执行成功")
    
    # 测试4: 执行不存在的命令
    print("\n测试4: 执行不存在的命令 'invalid_command_123'")
    result = run_command_once("invalid_command_123")
    print(f"命令输出: {result}")
    # 注意：subprocess.Popen 会返回命令的 stderr，所以即使命令不存在，也会有输出
    assert isinstance(result, str), "命令输出应该是字符串"
    print("✓ 测试4通过: 不存在的命令处理成功")
    
    print("\n=== 所有测试通过 ===")

# 测试 MCP 工具集成
def test_mcp_tool():
    """测试 MCP 工具集成"""
    print("\n=== 测试 MCP 工具集成 ===")
    print("注意：MCP 工具需要在 MCP 服务器环境中运行")
    print("您可以通过以下方式测试：")
    print("1. 在项目根目录运行: python -m app.code_agent.tools.shell_tools")
    print("2. 使用 MCP 客户端连接并调用 run_command_once_tool")
    print("3. 或集成到支持 MCP 的 Agent 中进行测试")
    print("\n=== MCP 工具测试说明完成 ===")

if __name__ == "__main__":
    test_run_command_once()
    test_mcp_tool()
