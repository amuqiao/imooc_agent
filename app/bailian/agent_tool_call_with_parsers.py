#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能体开发流程示例
根据 docs/note.md 实现智能体开发的完整流程
包括：初始化工具、初始化大模型、创建智能体、调用智能体
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import StructuredTool
from langchain_core.output_parsers import (
    StrOutputParser,
    CommaSeparatedListOutputParser,
    SimpleJsonOutputParser,
    PydanticOutputParser,
)
from pydantic import BaseModel, Field, SecretStr
from enum import Enum


# 1. 定义工具相关的入参模型
class AddInputArgs(BaseModel):
    """加法工具的入参校验模型"""
    a: int = Field(description="first number")
    b: int = Field(description="second number")


# 2. 定义工具函数
def add(a: int, b: int) -> int:
    """add two numbers"""
    return a + b


# 3. 创建工具对象
def create_add_tool():
    """创建加法工具"""
    return StructuredTool.from_function(
        func=add,
        name="add",
        description="add two numbers",
        args_schema=AddInputArgs,
        return_direct=True,
    )


# 4. 创建工具列表
def create_calc_tools():
    """创建计算工具列表"""
    return [create_add_tool()]


# 5. 初始化大模型
def init_llm():
    """初始化通义千问大模型"""
    return ChatOpenAI(
        model="qwen-plus",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=SecretStr("sk-9ec27f85396f41788a441841e6d4a718"),
        temperature=0,
    )


# 6. 创建带工具的大模型
def create_llm_with_tools(llm, tools):
    """创建带工具的大模型"""
    return llm.bind_tools(tools)


# 7. 定义输出解析器相关的Pydantic模型
class Summary(BaseModel):
    """计算结果摘要模型"""
    result: int = Field(description="计算结果")
    args: list = Field(description="计算参数")


# 9. 测试基础输出解析器
def test_basic_parsers(llm):
    """测试基础输出解析器"""
    print("\n=== 测试基础输出解析器 ===")
    
    # 1. StrOutputParser
    str_parser = StrOutputParser()
    chain = llm | str_parser
    result = chain.invoke("你好，世界！")
    print(f"StrOutputParser: {result}")
    
    # 2. CommaSeparatedListOutputParser
    comma_parser = CommaSeparatedListOutputParser()
    comma_parser_instructions = comma_parser.get_format_instructions()
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"请按照以下格式返回：{comma_parser_instructions}"),
        ("human", "请列出三种水果")
    ])
    chain = prompt | llm | comma_parser
    result = chain.invoke({})
    print(f"CommaSeparatedListOutputParser: {result}")
    
    # 3. SimpleJsonOutputParser
    json_parser = SimpleJsonOutputParser()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "请返回一个JSON对象，包含name和age字段"),
        ("human", "请创建一个用户信息")
    ])
    chain = prompt | llm | json_parser
    result = chain.invoke({})
    print(f"SimpleJsonOutputParser: {result}")


# 10. 测试Pydantic输出解析器
def test_pydantic_parser(llm):
    """测试Pydantic输出解析器"""
    print("\n=== 测试Pydantic输出解析器 ===")
    
    # 创建解析器
    parser = PydanticOutputParser(pydantic_object=Summary)
    
    # 创建提示模板
    prompt = ChatPromptTemplate.from_messages([
        ("system", "请计算100+100的结果，并返回结果和参数"),
        ("human", "请返回一个JSON对象，包含result和args字段，其中result是计算结果，args是计算参数")
    ])
    
    # 构建链
    chain = prompt | llm | parser
    result = chain.invoke({})
    print(f"PydanticOutputParser: {result}")
    print(f"Result: {result.result}")
    print(f"Args: {result.args}")


# 12. 执行工具调用
def execute_tool_call(response, tools):
    """执行工具调用"""
    tools_dict = {tool.name: tool for tool in tools}
    
    if hasattr(response, "tool_calls") and response.tool_calls:
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            if tool_name in tools_dict:
                tool = tools_dict[tool_name]
                return tool.invoke(tool_args)
            else:
                return f"工具 {tool_name} 不存在"
    else:
        return response.content


# 13. 主函数
def main():
    """主函数"""
    print("=== 智能体开发流程测试 ===")
    
    # 步骤1：初始化工具
    print("\n步骤1：初始化工具")
    calc_tools = create_calc_tools()
    print("✓ 工具初始化完成")
    
    # 步骤2：初始化大模型
    print("\n步骤2：初始化大模型")
    llm = init_llm()
    print("✓ 大模型初始化完成")
    
    # 步骤3：创建带工具的大模型
    print("\n步骤3：创建带工具的大模型")
    llm_with_tools = create_llm_with_tools(llm, calc_tools)
    print("✓ 带工具的大模型创建完成")
    
    # 步骤4：调用带工具的大模型
    print("\n步骤4：调用带工具的大模型")
    
    # 创建提示模板
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一位计算专家，擅长回答使用工具进行数学计算领域的问题。"),
        ("human", "用户问题：{question}")
    ])
    
    # 组装调用链
    chain = prompt | llm_with_tools
    
    # 测试用例
    messages = prompt.format_messages(question="100+100=？")
    print("调用带工具的大模型计算 100+100...")
    response = chain.invoke({"question": "100+100=？"})
    print(f"模型响应：{response}")
    
    # 执行工具调用
    result = execute_tool_call(response, calc_tools)
    print(f"工具执行结果：{result}")
    
    # 测试输出解析器
    test_basic_parsers(llm)
    test_pydantic_parser(llm)
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    main()