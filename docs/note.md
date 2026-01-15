# **深入MCP通信方式**

三种MCP通讯方式MCP（Model Context Protocol）协议目前支持三种主要通信方式，分别是：stdio（标准输入输出）工作原理：
通过本地进程的标准输入（stdin）和标准输出（stdout）进行通信。客户端以子进程的形式启动MCP服务器，双方通过管道交换JSON-RPC格式的消息，消息以换行符分隔。适用场景：本地进程间通信（如命令行工具、文件系统操作）。简单的批处理任务或工具调用。优点：实现简单，低延迟。无需网络配置，适合本地开发。限制：仅限本地使用，不支持分布式部署。服务端不能输出控制台日志（会污染协议流）。SSE（Server-Sent Events）工作原理：
基于HTTP长连接实现服务器到客户端的单向消息推送。客户端通过GET /sse建立长连接，服务器通过SSE流发送JSON-RPC消息；客户端通过POST /message发送请求或响应。适用场景：远程服务调用（如云服务、多客户端监控）。需要实时数据推送的场景（如对话式AI的流式输出）。优点：支持实时单向推送，适合流式交互。限制：已逐步被弃用（2025年3月后被Streamable HTTP取代）。连接中断后无法恢复，需重新建立。服务器需维持长连接，资源消耗较高。Streamable HTTP（流式HTTP）工作原理：
2025年3月引入的新传输方式，替代了SSE。通过统一的/message端点实现双向通信，支持以下特性：客户端通过HTTP POST发送请求（如工具调用）。服务器可将响应升级为SSE流式传输（当需要时）。支持无状态模式（Stateless Server），无需维持长连接。适用场景：高并发远程服务调用。需要灵活流式响应的场景（如AI助手的动态输出）。优点：解决SSE的缺陷：支持连接恢复（无需重新开始）。无需服务器维持长连接，降低资源压力。统一端点（/message），简化接口设计。兼容基础设施（如中间件、负载均衡）。推荐使用：
当前MCP官方推荐的传输方式，尤其适合生产环境和云服务。实现基于stdio的mcp服务stdio模式mcp服务架构：

第一步：创建mcp server（包含工具能力）使用 FastMCP 构建 mcp server：

```bash
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math Tools")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

以上代码包含两部分内容：

1. 使用`@mcp.tool()`装饰器注册的 mcp 工具方法；
2. 使用 `mcp.run(transport="stdio")`启动 stdio mcp 服务。

# 第二步：启动mcp server

找到 mcp server 所在文件夹，使用 python 命令启动服务（相当于启动了对 IO 流中 read 和 write 事件的监听）：

```bash
$ python app/fastmcp/stdio/math_tools.py
```

# 第三步：开发mcp client（包含智能体）

这里又分为三小步：

### 3.1 定义 stdio server 参数

```bash
server_params = StdioServerParameters(
    command="python",
    args=["/Users/sam/Xiaoluyy/ai/agent_test/app/fastmcp/math_tools.py"],
)
```

**3.2 读取 stdio mcp tools**

```bash
async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        tools = await load_mcp_tools(session)  # 自动加载MCP服务器提供的工具
```

**3.3 定义智能体，加载 mcp tools**

```bash
agent = create_react_agent(llm, tools)  # 创建React Agent
response = await agent.ainvoke(input={"messages": [("user", "what's (3 + 5) x 12?")]})  # 调用Agent
```

**mcp客户端完整源码**

```bash
import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent

from app.common import llm

# 使用stdio模式
server_params = StdioServerParameters(
    command="python",
    args=["/Users/sam/Xiaoluyy/ai/agent_test/app/fastmcp/math_tools.py"],
)

async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)  # 自动加载MCP服务器提供的工具
            print(tools)
            agent = create_react_agent(llm, tools)  # 创建React Agent
            response = await agent.ainvoke(input={"messages": [("user", "what's (3 + 5) x 12?")]})  # 调用Agent
            print(response)

```

**第四步：启动智能体**

```bash
asyncio.run(main())
```

运行结果：

```bash
{'messages': [
  HumanMessage(content="what's (3 + 5) x 12?", additional_kwargs={}, response_metadata={}, id='baefbd02-0e6f-4238-aac0-0989852ea097'),
  AIMessage(content='', additional_kwargs={'tool_calls': [{'index': 0, 'id': 'call_3f383dc314fe4b0ebc70c8', 'function': {'arguments': '{"a": 3, "b": 5}', 'name': 'add'}, 'type': 'function'}]}, response_metadata={'finish_reason': 'tool_calls', 'model_name': 'qwen3-235b-a22b'}, id='run--7477b051-f147-4772-be27-fc443813e5e4-0', tool_calls=[{'name': 'add', 'args': {'a': 3, 'b': 5}, 'id': 'call_3f383dc314fe4b0ebc70c8', 'type': 'tool_call'}]),
  ToolMessage(content='8', name='add', id='569efaef-c880-4b96-8a76-ecb1184da537', tool_call_id='call_3f383dc314fe4b0ebc70c8'),
  AIMessage(content='', additional_kwargs={'tool_calls': [{'index': 0, 'id': 'call_287db3d531af4d2d82adba', 'function': {'arguments': '{"a": 8, "b": 12}', 'name': 'multiply'}, 'type': 'function'}]}, response_metadata={'finish_reason': 'tool_calls', 'model_name': 'qwen3-235b-a22b'}, id='run--506ce062-0dcc-4217-bcca-0e1be306ad0c-0', tool_calls=[{'name': 'multiply', 'args': {'a': 8, 'b': 12}, 'id': 'call_287db3d531af4d2d82adba', 'type': 'tool_call'}]),
  ToolMessage(content='96', name='multiply', id='69357610-bd4b-4486-8192-b87a3d35d6eb', tool_call_id='call_287db3d531af4d2d82adba'),
  AIMessage(content='The result of $(3 + 5) \\times 12$ is $\\boxed{96}$.', additional_kwargs={}, response_metadata={'finish_reason': 'stop', 'model_name': 'qwen3-235b-a22b'}, id='run--428dda6d-ebd6-4efd-beb4-b93e7c595ecb-0')
  ]}
```

# 实现基于sse的mcp服务

注意：sse已被官方废弃，优先使用streamable-http，两者从代码层面来看，差异不大

sse/streamable-http模式mcp服务架构：

![](https://cdn.nlark.com/yuque/0/2025/jpeg/375559/1747493110889-cdc3410d-207d-4b21-b652-e06c095ae654.jpeg)

# 第一步：创建mcp server端

```bash
if __name__ == "__main__":
    mcp.run(transport="sse")
```

**第二步：启动mcp server**

```bash
$ python app/fastmcp/sse/math_tools.py
```

# 第三步：开发mcp client

与 stdio 差异点，其余相同：

```bash
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient(
    {
        "math": {
            "url": "http://127.0.0.1:8000/sse",
            "transport": "sse",
        }
    }
)
tools = await client.get_tools()
```

**第四步：启动智能体**

```bash
asyncio.run(main())
```

# 实现基于streamable_http的mcp服务

启动服务：

```bash
mcp.run(transport="streamable-http")
```

客户端连接服务：

```bash
client = MultiServerMCPClient(
    {
        "math": {
            "url": "http://127.0.0.1:8000/mcp",
            "transport": "streamable_http",
        }
    }
)
tools = await client.get_tools()
```

# 附python with 语法

```bash
from contextlib import contextmanager

@contextmanager
def go(num1, num2):
    print("go!")
    yield num1, num2, num1 + num2

with go(1, 2) as n:
    print(n)
```