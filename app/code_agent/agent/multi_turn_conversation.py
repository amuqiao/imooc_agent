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
from pydantic import SecretStr


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
            system_prompt or "你是一个智能助手，擅长帮助用户解决各种问题。"
        )
        self._chain = None
        self._chain_with_history = None

    def _create_prompt_template(self) -> ChatPromptTemplate:
        """创建提示词模板"""
        return ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                MessagesPlaceholder(variable_name="chat_history", optional=True),
                ("human", "{question}"),
            ]
        )

    def _get_base_chain(self):
        """获取基础链"""
        if self._chain is None:
            prompt = self._create_prompt_template()
            self._chain = prompt | self.llm | StrOutputParser()
        return self._chain

    def get_chain_with_history(self) -> RunnableWithMessageHistory:
        """获取带历史记录的链"""
        if self._chain_with_history is None:
            base_chain = self._get_base_chain()
            self._chain_with_history = RunnableWithMessageHistory(
                runnable=base_chain,
                get_session_history=self.store.get_session_history,
                input_messages_key="question",
                history_messages_key="chat_history",
            )
        return self._chain_with_history

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
        chain_with_history = self.get_chain_with_history()

        response = chain_with_history.invoke(
            {"question": question}, config={"configurable": {"session_id": session_id}}
        )

        return response

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
