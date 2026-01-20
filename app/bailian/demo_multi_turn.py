#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多轮对话修复演示
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.bailian.agent_multi_turn_conversation import (
    create_conversation_manager,
    ConversationConfig
)

# 创建临时目录用于持久化
test_data_dir = "/tmp/multi_turn_demo"
if os.path.exists(test_data_dir):
    import shutil
    shutil.rmtree(test_data_dir)
os.makedirs(test_data_dir, exist_ok=True)

print("=== 多轮对话修复演示 ===")
print(f"持久化存储目录: {test_data_dir}")

# 选项菜单
print("\n请选择测试模式:")
print("1. 内存模式（不支持持久化）")
print("2. 持久化模式（支持持久化）")

choice = input("\n输入选项 (1/2): ").strip()

if choice == "1":
    enable_persistence = False
    print("\n使用内存模式，对话历史不会持久化")
elif choice == "2":
    enable_persistence = True
    print(f"\n使用持久化模式，对话历史会保存到: {test_data_dir}")
else:
    print("\n无效选项，默认使用内存模式")
    enable_persistence = False

# 创建对话管理器
manager = create_conversation_manager(
    enable_persistence=enable_persistence,
    data_dir=test_data_dir,
    system_prompt="你是一个智能助手，擅长回答各种问题。"
)

# 创建会话
session_id = manager.create_session()
print(f"\n创建会话成功，会话ID: {session_id}")

print("\n开始对话（输入 'exit' 结束）:")

while True:
    try:
        user_input = input("\n用户: ").strip()
        if user_input.lower() in ["exit", "退出"]:
            print("\n=== 对话结束 ===")
            break
        
        if not user_input:
            continue
        
        print("助手: ", end="")
        response = manager.chat(question=user_input, session_id=session_id)
        print(response)
        
    except KeyboardInterrupt:
        print("\n\n=== 对话中断 ===")
        break
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
        break

# 显示对话历史
print("\n=== 对话历史 ===")
history = manager.get_history(session_id)
if not history:
    print("暂无对话历史")
else:
    for i, msg in enumerate(history, 1):
        role = "用户" if msg["role"] == "human" else "助手"
        print(f"\n{i}. {role}: {msg['content']}")

# 清理
if os.path.exists(test_data_dir) and enable_persistence:
    print(f"\n持久化文件已保存到: {test_data_dir}")
    print("你可以使用以下命令查看文件内容:")
    print(f"   ls -la {test_data_dir}/")
    # 显示文件路径
    user_id = session_id.split("_")[0] if "_" in session_id else "session"
    file_path = os.path.join(test_data_dir, user_id, f"{session_id}.json")
    if os.path.exists(file_path):
        print(f"   cat {file_path}")
