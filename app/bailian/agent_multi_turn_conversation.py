#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangChain 多轮对话能力实现
✅ 支持内存对话历史
✅ 支持持久化存储（可选开关）
✅ 支持 session 管理
✅ LangChain 1.2.4 兼容
"""
import os
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import (
    ChatMessageHistory,
    FileChatMessageHistory,
)
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.agent_toolkits.file_management import FileManagementToolkit
from langchain_core.tools import Tool
from pydantic import SecretStr

# 使用langgraph中的create_react_agent，忽略警告
from langgraph.prebuilt import create_react_agent
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)


# ===================== 1. 配置管理 =====================
class ConversationConfig:
    """对话配置管理"""

    def __init__(
        self,
        enable_persistence: bool = False,
        data_dir: str = "data/conversations",
        session_prefix: str = "session",
    ):
        self.enable_persistence = enable_persistence
        self.data_dir = data_dir
        self.session_prefix = session_prefix

    @classmethod
    def with_persistence(
        cls, data_dir: str = "data/conversations"
    ) -> "ConversationConfig":
        """创建支持持久化的配置"""
        return cls(enable_persistence=True, data_dir=data_dir)

    @classmethod
    def in_memory(cls, session_prefix: str = "session") -> "ConversationConfig":
        """创建内存配置（不支持持久化）"""
        return cls(enable_persistence=False, session_prefix=session_prefix)


# ===================== 2. 对话存储管理 =====================
class ConversationStore:
    """对话历史存储管理"""

    def __init__(self, config: ConversationConfig):
        self.config = config
        self.in_memory_store: Dict[str, BaseChatMessageHistory] = {}

        if self.config.enable_persistence:
            os.makedirs(self.config.data_dir, exist_ok=True)

    def _get_file_path(self, session_id: str) -> str:
        """生成对话文件路径"""
        if "_" in session_id:
            user_id = session_id.rsplit("_", 1)[0]
        else:
            user_id = self.config.session_prefix
        dir_path = os.path.join(self.config.data_dir, user_id)
        os.makedirs(dir_path, exist_ok=True)
        return os.path.join(dir_path, f"{session_id}.json")

    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """获取会话历史"""
        if self.config.enable_persistence:
            return self._get_persistent_history(session_id)
        else:
            return self._get_memory_history(session_id)

    def _get_memory_history(self, session_id: str) -> BaseChatMessageHistory:
        """获取内存对话历史"""
        if session_id not in self.in_memory_store:
            self.in_memory_store[session_id] = ChatMessageHistory()
        return self.in_memory_store[session_id]

    def _get_persistent_history(self, session_id: str) -> BaseChatMessageHistory:
        """获取持久化对话历史"""
        file_path = self._get_file_path(session_id)
        # FileChatMessageHistory 内部会自动处理文件初始化
        return FileChatMessageHistory(file_path)

    def save_conversation(self, session_id: str, messages: list) -> None:
        """保存对话到文件（FileChatMessageHistory 自动处理）"""
        # FileChatMessageHistory 会自动保存，无需手动处理
        pass

    def load_conversation(self, session_id: str) -> list:
        """从文件加载对话"""
        if not self.config.enable_persistence:
            return []

        # FileChatMessageHistory 会自动加载，直接从实例获取
        history = self.get_session_history(session_id)
        return list(history.messages)


# ===================== 3. 多轮对话管理器 =====================
class MultiTurnConversationManager:
    """多轮对话管理器"""

    def __init__(
        self,
        llm: ChatOpenAI,
        config: Optional[ConversationConfig] = None,
        system_prompt: Optional[str] = None,
    ):
        self.llm = llm
        self.config = config or ConversationConfig.in_memory()
        self.store = ConversationStore(self.config)
        self.system_prompt = (
            system_prompt
            or "你是一个智能助手，擅长帮助用户解决各种问题。你可以使用以下文件管理工具：\n"
            "- copy_file: 在指定位置创建文件的副本\n"
            "- create_directory: 创建目录，如果目录已存在则忽略\n"
            "- file_delete: 删除一个文件\n"
            "- file_search: 在子目录中递归搜索与正则表达式模式匹配的文件\n"
            "- move_file: 将文件从一个位置移动到另一个位置，或者重命名文件\n"
            "- read_file: 从磁盘读取文件内容\n"
            "- write_file: 将文件写入磁盘，可以选择追加到现有文件\n"
            "- list_directory: 列出指定文件夹中的文件\n"
            "所有文件操作都将在指定的临时目录中执行。如果需要执行文件操作，请使用适当的工具，并遵循工具的参数格式要求。"
        )
        self._agent = None
        self._tools = None
        self._init_tools()

    def _init_tools(self):
        """初始化文件管理工具"""
        # 创建 FileManagementToolkit 实例，设置根目录为当前工作目录
        toolkit = FileManagementToolkit(
            root_dir="e:/github_project/imooc_agent/.temp",  # 设置根目录为指定的 temp 目录
            selected_tools=[
                "copy_file",  # 在指定位置创建文件的副本
                "file_delete",  # 删除一个文件
                "file_search",  # 在子目录中递归搜索与正则表达式模式匹配的文件
                "move_file",  # 将文件从一个位置移动到另一个位置，或者重命名文件
                "read_file",  # 从磁盘读取文件内容
                "write_file",  # 将文件写入磁盘，可以选择追加到现有文件
                "list_directory",  # 列出指定文件夹中的文件
            ],  # 选择要使用的工具
        )
        # 获取工具列表
        self._tools = toolkit.get_tools()

        # 导入os模块，用于添加创建目录工具
        import os
        from langchain_core.tools import Tool

        # 定义创建目录工具
        def create_directory(path: str) -> str:
            """创建目录，如果目录已存在则忽略"""
            # 构建完整路径
            full_path = os.path.join("e:/github_project/imooc_agent/.temp", path)
            # 创建目录，包括所有中间目录
            os.makedirs(full_path, exist_ok=True)
            return f"目录已创建: {full_path}"

        # 将创建目录工具添加到工具列表
        self._tools.append(
            Tool.from_function(
                func=create_directory,
                name="create_directory",
                description="创建目录，如果目录已存在则忽略。参数：path - 要创建的目录路径",
            )
        )

    def _get_agent(self):
        """获取React Agent"""
        if self._agent is None:
            # 使用create_react_agent创建agent，自动处理工具调用
            self._agent = create_react_agent(self.llm, self._tools)
        return self._agent

    def create_session(self, session_id: Optional[str] = None) -> str:
        """创建新会话"""
        if session_id is None:
            if self.config.enable_persistence:
                session_id = f"{self.config.session_prefix}_{uuid.uuid4()}"
            else:
                session_id = str(uuid.uuid4())
        return session_id

    def chat(self, question: str, session_id: str, auto_save: bool = True) -> str:
        """发送消息并获取回复"""
        # 导入asyncio，用于处理异步调用
        import asyncio

        # 获取agent
        agent = self._get_agent()

        # 获取会话历史
        history = self.store.get_session_history(session_id)

        # 构建消息列表，包含历史消息和当前问题
        messages = []
        for msg in history.messages:
            messages.append(msg)
        messages.append(("user", question))

        # 使用asyncio.run执行异步调用
        response = asyncio.run(agent.ainvoke({"messages": messages}))

        # 保存对话历史
        history.add_user_message(question)
        history.add_ai_message(response["messages"][-1].content)

        # 返回响应内容
        return response["messages"][-1].content

    def get_history(self, session_id: str) -> list:
        """获取对话历史"""
        history = self.store.get_session_history(session_id)
        return [
            {
                "role": msg.__class__.__name__.replace("Message", "").lower(),
                "content": msg.content,
            }
            for msg in history.messages
        ]

    def clear_history(self, session_id: str) -> None:
        """清空对话历史"""
        if session_id in self.store.in_memory_store:
            del self.store.in_memory_store[session_id]

    def execute_tool_call(self, response) -> str:
        """执行工具调用"""
        tools_dict = {tool.name: tool for tool in self._tools}

        if hasattr(response, "tool_calls") and response.tool_calls:
            results = []
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                if tool_name in tools_dict:
                    tool = tools_dict[tool_name]
                    result = tool.invoke(tool_args)
                    results.append(f"工具 {tool_name} 执行结果: {result}")
                else:
                    results.append(f"工具 {tool_name} 不存在")
            return "\n".join(results)
        else:
            return response.content


# ===================== 4. 初始化函数 =====================
def init_llm():
    """初始化大模型"""
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("环境变量 DASHSCOPE_API_KEY 未设置，请在 .env 文件中配置")

    return ChatOpenAI(
        model="qwen-plus",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=SecretStr(api_key),
        temperature=0,
        max_tokens=2048,
    )


def create_conversation_manager(
    enable_persistence: bool = False,
    data_dir: str = "data/conversations",
    system_prompt: Optional[str] = None,
) -> MultiTurnConversationManager:
    """创建对话管理器"""
    llm = init_llm()
    config = ConversationConfig(
        enable_persistence=enable_persistence, data_dir=data_dir
    )
    return MultiTurnConversationManager(
        llm=llm, config=config, system_prompt=system_prompt
    )


# ===================== 5. 主函数示例 =====================
def run_conversation_example():
    """运行多轮对话示例"""
    print("=== LangChain 多轮对话示例 ===")
    print("输入 'exit' 或 '退出' 结束对话\n")

    # 创建对话管理器（支持持久化）
    manager = create_conversation_manager(
        enable_persistence=True,
        data_dir="data/conversations",
        system_prompt="你是一个技术专家，擅长解决各种编程和技术问题。",
    )

    # 创建会话
    session_id = manager.create_session()
    print(f"[会话ID] {session_id}\n")

    try:
        while True:
            user_input = input("用户: ")
            if user_input.lower() in ["exit", "退出"]:
                print("\n[对话结束]")
                print(f"历史记录已保存至: data/conversations/")
                break

            if not user_input.strip():
                continue

            response = manager.chat(question=user_input, session_id=session_id)
            print(f"\n助手: {response}\n")

    except KeyboardInterrupt:
        print("\n[对话中断]")


def demonstrate_persistence_switch():
    """演示持久化开关功能"""
    print("\n=== 持久化开关演示 ===\n")

    # 1. 内存模式（不支持持久化）
    print("1. 内存模式测试:")
    memory_manager = create_conversation_manager(enable_persistence=False)
    session_id = memory_manager.create_session()
    response = memory_manager.chat("你好，我是测试用户", session_id)
    print(f"内存模式回复: {response}\n")

    # 2. 持久化模式（支持持久化）
    print("2. 持久化模式测试:")
    persistent_manager = create_conversation_manager(
        enable_persistence=True, data_dir="data/conversations/demo"
    )
    session_id = persistent_manager.create_session()
    response = persistent_manager.chat("你好，我是测试用户", session_id)
    print(f"持久化模式回复: {response}")
    print(f"历史记录已保存\n")

    # 3. 查看历史记录
    print("3. 查看历史记录:")
    history = persistent_manager.get_history(session_id)
    for msg in history:
        print(f"  - [{msg['role']}]: {msg['content'][:50]}...")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demonstrate_persistence_switch()
    else:
        run_conversation_example()
