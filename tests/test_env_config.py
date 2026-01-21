#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试环境变量配置是否正确
验证 .env 文件中的 DASHSCOPE_API_KEY 是否能被正确加载
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 设置Windows控制台编码为UTF-8
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# 加载项目根目录的 .env 文件
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

print("=== 环境变量配置测试 ===\n")

# 测试 DASHSCOPE_API_KEY
api_key = os.getenv("DASHSCOPE_API_KEY")
if api_key:
    # 只显示前10个和后10个字符，中间用*替代
    masked_key = f"{api_key[:10]}...{api_key[-10:]}" if len(api_key) > 20 else "***"
    print(f"✅ DASHSCOPE_API_KEY 加载成功")
    print(f"   值: {masked_key}")
else:
    print("❌ DASHSCOPE_API_KEY 未设置")
    print("   请检查 .env 文件是否存在且包含 DASHSCOPE_API_KEY 配置")

# 测试 GITHUB_PERSONAL_ACCESS_TOKEN
github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
if github_token:
    masked_token = f"{github_token[:10]}...{github_token[-10:]}" if len(github_token) > 20 else "***"
    print(f"\n✅ GITHUB_PERSONAL_ACCESS_TOKEN 加载成功")
    print(f"   值: {masked_token}")
else:
    print("\n⚠️  GITHUB_PERSONAL_ACCESS_TOKEN 未设置")

# 测试 LLM 初始化
print("\n=== 测试 LLM 初始化 ===\n")
try:
    from langchain_openai import ChatOpenAI
    from pydantic import SecretStr
    
    llm = ChatOpenAI(
        model="qwen-plus",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=SecretStr(api_key),
        temperature=0,
        max_tokens=100
    )
    print("✅ LLM 初始化成功")
    
    # 简单测试调用
    print("\n正在测试 LLM 调用（发送简单问题）...")
    response = llm.invoke("你好，请用一句话介绍你自己")
    print(f"✅ LLM 调用成功")
    print(f"   响应: {response.content}")
    
except ValueError as e:
    print(f"❌ LLM 初始化失败: {e}")
except Exception as e:
    print(f"❌ LLM 调用失败: {e}")

print("\n=== 测试完成 ===")
