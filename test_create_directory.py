#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试创建目录和文件的功能
"""

from app.bailian.agent_multi_turn_conversation import create_conversation_manager

def test_create_directory_file():
    """测试创建目录和文件"""
    print("=== 测试创建目录和文件 ===")
    
    # 创建对话管理器
    manager = create_conversation_manager(
        enable_persistence=False,
        system_prompt="你是一个技术专家，擅长解决各种编程和技术问题。"
    )
    
    # 创建会话
    session_id = manager.create_session()
    print(f"会话ID: {session_id}")
    
    # 测试1: 创建目录
    print("\n测试1: 创建code_agent目录")
    response = manager.chat("在根目录下创建code_agent目录", session_id)
    print(f"响应: {response}")
    
    # 测试2: 在目录中创建.keep文件
    print("\n测试2: 在code_agent目录下创建.keep文件")
    response = manager.chat("在code_agent目录下创建.keep文件", session_id)
    print(f"响应: {response}")
    
    # 测试3: 验证文件创建
    print("\n测试3: 验证.keep文件是否存在")
    response = manager.chat("查看code_agent目录下的文件", session_id)
    print(f"响应: {response}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_create_directory_file()
