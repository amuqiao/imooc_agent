#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用LangChain调用通义千问并绑定自定义工具的示例脚本
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载项目根目录的 .env 文件
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field, SecretStr


# 1. 定义入参校验规则（Pydantic BaseModel）
class AddInputArgs(BaseModel):
    """加法工具的入参校验模型"""

    a: int = Field(description="需要相加的第一个数字")
    b: int = Field(description="需要相加的第二个数字")


# 2. 定义核心工具函数
# 2.1 加法工具函数
def add(a: int, b: int) -> int:
    """实现两个数字的加法运算"""
    return a + b


# 2.2 乘法工具函数（扩展工具示例）
def multiply(a: int, b: int) -> int:
    """实现两个数字的乘法运算"""
    return a * b


# 3. 初始化大模型
def init_llm():
    """初始化通义千问大模型"""
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("环境变量 DASHSCOPE_API_KEY 未设置，请在 .env 文件中配置")
    
    return ChatOpenAI(
        model="qwen-plus",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=SecretStr(api_key),
        streaming=True,  # 开启流式输出
    )


# 4. 创建工具对象
def create_tools():
    """创建工具列表"""
    # 加法工具
    add_tool = StructuredTool.from_function(
        func=add,
        name="add",
        description="用于计算两个数字的加法运算，当用户提出求和需求时调用该工具",
        args_schema=AddInputArgs,
        return_direct=True,
    )

    # 乘法工具
    multiply_tool = StructuredTool.from_function(
        func=multiply,
        name="multiply",
        description="用于计算两个数字的乘法运算，当用户提出求积需求时调用该工具",
        args_schema=AddInputArgs,  # 复用加法的入参校验模型（都是两个整数）
        return_direct=True,
    )

    return [add_tool, multiply_tool]


# 5. 组装调用链
def create_chain(llm, tools):
    """组装大模型调用链"""
    # 定义提示词模板
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "你是资深开发工程师小慕，能自主判断是否需要调用工具解决问题，直接返回最终结果。",
            ),
            ("human", "{user_input}"),
        ]
    )

    # 给大模型绑定工具
    llm_with_tools = llm.bind_tools(tools)

    # 组装调用链
    return prompt | llm_with_tools


# 6. 解析工具调用并执行
def execute_tool_call(response, tools):
    """解析工具调用指令并执行工具"""
    # 创建工具字典：工具名 → 工具对象
    tools_dict = {tool.name: tool for tool in tools}

    # 检查是否有工具调用
    if hasattr(response, "tool_calls") and response.tool_calls:
        # 遍历所有工具调用
        for tool_call in response.tool_calls:
            func_name = tool_call["name"]  # 获取工具名
            func_args = tool_call["args"]  # 获取工具入参

            if func_name in tools_dict:
                tool_func = tools_dict[func_name]
                # 执行工具并返回结果
                return tool_func.invoke(func_args)
            else:
                return f"错误：未找到工具 {func_name}"
    else:
        # 直接返回模型回答
        return response.content


# 7. 主函数
def main():
    """主函数"""
    print("=== 通义千问工具调用测试 ===")

    # 初始化大模型
    llm = init_llm()
    print("✓ 大模型初始化完成")

    # 创建工具
    tools = create_tools()
    print("✓ 自定义工具创建完成")

    # 组装调用链
    chain = create_chain(llm, tools)
    print("✓ 调用链组装完成")

    # 测试用例
    test_cases = ["计算100+200的结果", "计算50*30的结果", "你好，介绍一下你自己"]

    # 执行测试
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n--- 测试用例 {i} ---")
        print(f"用户输入：{test_input}")

        # 调用大模型
        response = chain.invoke({"user_input": test_input})

        # 解析并执行工具调用
        result = execute_tool_call(response, tools)
        print(f"AI输出：{result}")

    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    main()
