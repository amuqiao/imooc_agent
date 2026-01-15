#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高德MCP服务集成示例

本脚本演示了如何使用LangChain集成高德MCP服务，包括：
1. 创建MCP客户端
2. 初始化智能体并集成MCP工具
3. 运行智能体生成旅行攻略
4. 扩展智能体，增加文件管理能力

参考文档：e:\github_project\imooc_agent\docs\note.md
"""

import os
import asyncio
from langchain_core.prompts import PromptTemplate
from langchain_community.agent_toolkits import FileManagementToolkit
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from pydantic import SecretStr


# ===================== 辅助函数：初始化大模型 =====================
def init_llm():
    """初始化通义千问大模型"""
    return ChatOpenAI(
        model="qwen-plus",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=SecretStr("sk-9ec27f85396f41788a441841e6d4a718"),
        temperature=0,
        max_tokens=2048,
    )


class AmapMCPAgent:
    """高德MCP智能体类"""

    def __init__(self, amap_key: str = None, llm=None):
        """
        初始化高德MCP智能体

        Args:
            amap_key: 高德应用Key，若为None则从环境变量AMAP_KEY获取
            llm: 语言模型实例，若为None则使用默认的init_llm()
        """
        self.amap_key = amap_key or os.environ.get("AMAP_KEY")
        if not self.amap_key:
            raise ValueError("高德应用Key未提供，请设置AMAP_KEY环境变量或直接传入")

        # 如果未提供llm，则使用默认的init_llm()
        self.llm = llm or init_llm()
        self.client = None
        self.tools = []
        self.agent = None

    async def create_mcp_client(self):
        """创建高德MCP客户端并获取工具"""
        # 创建MCP客户端
        self.client = MultiServerMCPClient(
            {
                "amap": {
                    "url": f"https://mcp.amap.com/sse?key={self.amap_key}",
                    "transport": "sse",
                }
            }
        )

        # 获取MCP工具
        self.tools = await self.client.get_tools()
        print(f"✓ 成功获取 {len(self.tools)} 个高德MCP工具")

    def initialize_agent(self, include_file_tools: bool = False, root_dir: str = None):
        """
        初始化智能体（使用最新LangChain StateGraph架构）

        Args:
            include_file_tools: 是否包含文件管理工具
            root_dir: 文件管理工具的根目录，若为None则使用当前目录
        """
        # 如果需要，添加文件管理工具
        if include_file_tools:
            root_dir = root_dir or os.getcwd()
            file_toolkit = FileManagementToolkit(root_dir=root_dir)
            file_tools = file_toolkit.get_tools()
            self.tools.extend(file_tools)
            print(f"✓ 已添加文件管理工具，根目录: {root_dir}")

        # 初始化智能体（使用最新StateGraph架构）
        from langchain import agents

        # 使用最新的 create_agent API (基于 StateGraph)
        self.agent = agents.create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt="你是一个智能助手，可以调用高德 MCP 工具和文件管理工具。请根据用户需求，自主判断是否需要调用工具解决问题，直接返回最终结果。\n\n注意：\n- 直接返回结果，不要添加额外的解释\n- 确保生成的HTML/CSS代码格式正确\n- 写入文件时必须指定utf-8编码，防止中文乱码",
        )
        print("✓ 智能体初始化完成 (使用最新 StateGraph 架构)")

    def create_travel_prompt(self, travel_info: dict, save_to_file: str = None):
        """
        创建旅行攻略提示词

        Args:
            travel_info: 旅行信息字典，包含目的地、天数、出行方式等
            save_to_file: 保存结果的文件路径，若为None则不保存

        Returns:
            格式化后的提示词
        """
        # 基础提示词模板
        base_prompt = """你是一个智能助手，可以调用高德 MCP 工具。

        问题: 
        - 我{time}计划去{destination}游玩{days}天。
        - 帮制作旅行攻略，考虑出行时间和路线，以及天气状况路线规划。
        - 行程规划结果在高德地图app展示，并集成到h5页面中。
            - 同一天行程景区之间我想{transport}前往。
        - 制作网页地图自定义绘制旅游路线和位置，并提供专属地图链接、打车链接、骑行路线、驾车路径等。
        """

        # 添加文件保存要求
        if save_to_file:
            base_prompt += f"- 将网页保存到：{save_to_file}\n"

        # 格式化提示词
        prompt_template = PromptTemplate.from_template(base_prompt)
        return prompt_template.format(
            time=travel_info.get("time", "五月底端午节"),
            destination=travel_info.get("destination", "杭州"),
            days=travel_info.get("days", 4),
            transport=travel_info.get("transport", "打车"),
        )

    async def run_agent(self, prompt: str):
        """
        运行智能体（异步版本，支持StructuredTool的异步调用）

        Args:
            prompt: 提示词

        Returns:
            智能体运行结果
        """
        if not self.agent:
            raise ValueError("智能体未初始化，请先调用initialize_agent方法")

        print("\n=== 开始运行智能体 ===")

        # 准备输入数据（新架构使用不同的输入格式）
        inputs = {"messages": [{"role": "user", "content": prompt}]}

        # 执行智能体（使用async_stream方法）
        result = None
        async for chunk in self.agent.astream(inputs, stream_mode="updates"):
            if chunk:
                # 处理每个chunk，这里简化处理，实际可能需要更复杂的处理
                print(chunk)
                result = chunk

        print("=== 智能体运行完成 ===\n")
        return result

    async def close(self):
        """关闭MCP客户端"""
        # MultiServerMCPClient没有close方法，直接返回
        if self.client:
            print("✓ MCP客户端资源已释放")


async def main():
    """主函数示例（使用最新StateGraph架构）"""
    print("=== 高德MCP智能体测试 (LangChain StateGraph新架构版) ===")

    try:
        # 1. 创建高德MCP智能体实例（自动初始化大模型）
        amap_key = "a2854b8c97e16885f90e697d0c121bcb"
        agent = AmapMCPAgent(amap_key=amap_key)
        print("✓ 高德MCP智能体实例创建完成")

        # 2. 创建MCP客户端
        await agent.create_mcp_client()

        # 3. 初始化智能体（包含文件工具）
        # 使用项目根目录下的.temp目录
        # 获取当前脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # 计算项目根目录
        project_root = os.path.abspath(os.path.join(script_dir, "../../"))
        # 项目根目录下的.temp目录
        root_dir = os.path.join(project_root, ".temp")
        # 确保目录存在
        os.makedirs(root_dir, exist_ok=True)
        agent.initialize_agent(
            include_file_tools=True, root_dir=root_dir  # 结果保存目录
        )

        # 4. 创建旅行攻略提示词
        travel_info = {
            "time": "五月底端午节",
            "destination": "杭州",
            "days": 4,
            "transport": "打车",
        }

        # 使用项目根目录下的.temp目录保存文件
        save_file_path = os.path.join(root_dir, "amap.html")
        prompt = agent.create_travel_prompt(
            travel_info=travel_info, save_to_file=save_file_path  # 保存结果到文件
        )
        print(f"\n✓ 旅行攻略提示词创建完成")
        print(f"提示词内容：{prompt[:100]}...")

        # 5. 运行智能体（使用新架构的async_stream方法）
        result = await agent.run_agent(prompt)

        # 6. 输出结果
        print("\n=== 旅行攻略结果 ===")
        print(result)

    except Exception as e:
        print(f"\n✗ 执行出错：{e}")
    finally:
        # 7. 关闭客户端
        if "agent" in locals():
            await agent.close()
            print("✓ MCP客户端已关闭")


if __name__ == "__main__":
    # 运行主函数
    asyncio.run(main())
