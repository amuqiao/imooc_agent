import asyncio

from langchain_core.messages import HumanMessage, AIMessage
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent

from app.common import llm

async def main():
    # 1. 定义mcp参数
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@executeautomation/playwright-mcp-server"],
    )
    
    # 2. 实例化stdio_client
    async with stdio_client(server_params) as (read, write):
        # 3. 创建session
        async with ClientSession(read, write) as session:
            await session.initialize()
            # 4. 读取mcp tools配置
            tools = await load_mcp_tools(session)  # 自动加载MCP服务器提供的工具
            print(tools)
            # 5. 定义agent
            agent = create_react_agent(llm, tools)  # 创建React Agent
            # 6. 调用agent
            response = await agent.ainvoke(input={"messages": [("user", "在百度查询南京今天的天气")]})
            print(response, "\n")

            # 7. 打印调用过程
            messages = response["messages"]
            for message in messages:
                if isinstance(message, HumanMessage):
                    print("用户:", message.content)
                elif isinstance(message, AIMessage):
                    if message.content:
                        print("助理:", message.content)
                    else:
                        for tool_call in message.tool_calls:
                            print("调用工具:", tool_call["name"], tool_call["args"])


asyncio.run(main())


