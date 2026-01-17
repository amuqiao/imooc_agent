# MCP 三种连接方式与测试手册

本文档详细介绍 MCP（Model Context Protocol）服务器的三种连接方式及其测试用例的运行方法。

## 1. MCP 三种连接方式概述

MCP 服务器支持三种传输方式，每种方式都有其特点和适用场景：

| 传输方式 | 全称 | 特点 | 适用场景 |
|---------|------|------|----------|
| stdio | 标准输入输出 | 简单易用，适合本地开发和测试 | 本地开发、测试环境 |
| sse | 服务器发送事件 | 基于 HTTP 的单向流传输 | 已废弃，推荐使用 streamable-http |
| streamable-http | 流式 HTTP | 基于 HTTP 的双向流传输，支持长连接 | 生产环境、远程调用 |

## 2. 服务器端实现

### 2.1 服务器代码结构

MCP 数学服务器 `math_mcp_server.py` 实现了四个基本数学运算工具：
- `add(a, b)`: 加法运算
- `subtract(a, b)`: 减法运算
- `multiply(a, b)`: 乘法运算
- `divide(a, b)`: 除法运算

### 2.2 启动服务器

可以通过命令行参数指定传输方式启动服务器：

```bash
# 使用 stdio 传输方式（默认）
python math_mcp_server.py --transport stdio

# 使用 sse 传输方式
python math_mcp_server.py --transport sse

# 使用 streamable-http 传输方式
python math_mcp_server.py --transport streamable-http
```

## 3. 客户端连接方式

### 3.1 stdio 连接方式

**特点**：
- 客户端直接启动并管理服务器进程
- 通过标准输入输出进行通信
- 适合本地开发和测试

**使用方法**：

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 配置服务器参数
server_params = StdioServerParameters(
    command="python",
    args=["math_mcp_server.py", "--transport", "stdio"],
)

# 连接服务器
async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        # 使用 session 调用工具
```

**测试用例**：`math_mcp_client_stdio.py`

### 3.2 sse 连接方式

**特点**：
- 基于 HTTP 的单向流传输
- 服务器主动推送数据到客户端
- 已废弃，推荐使用 streamable-http

**使用方法**：

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

# 创建客户端
client = MultiServerMCPClient(
    {
        "math": {
            "url": "http://127.0.0.1:8000/sse",
            "transport": "sse",
        }
    }
)

# 获取工具
tools = await client.get_tools()
```

**测试用例**：`math_mcp_client_sse.py`

### 3.3 streamable-http 连接方式

**特点**：
- 基于 HTTP 的双向流传输
- 支持长连接和异步通信
- 推荐用于生产环境

**使用方法**：

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

# 创建客户端
client = MultiServerMCPClient(
    {
        "math": {
            "url": "http://127.0.0.1:8000/mcp",
            "transport": "streamable_http",
        }
    }
)

# 获取工具
tools = await client.get_tools()
```

**测试用例**：`math_mcp_client_streamable_http.py`

## 4. 运行测试用例

### 4.1 环境准备

1. 确保已安装必要的依赖：
   ```bash
   pip install langchain_mcp_adapters langgraph langchain_openai pydantic
   ```

2. 准备通义千问 API 密钥（代码中已提供测试密钥）

### 4.2 运行 stdio 测试

```bash
cd e:\github_project\imooc_agent\app\bailian
python math_mcp_client_stdio.py
```

### 4.3 运行 sse 测试

```bash
cd e:\github_project\imooc_agent\app\bailian
python math_mcp_client_sse.py
```

### 4.4 运行 streamable-http 测试

**步骤 1**：先启动服务器
```bash
cd e:\github_project\imooc_agent\app\bailian
python math_mcp_server.py --transport streamable-http
```

**步骤 2**：在另一个终端运行客户端
```bash
cd e:\github_project\imooc_agent\app\bailian
python math_mcp_client_streamable_http.py
```

## 5. 测试结果示例

所有测试用例都会执行相同的数学问题：`what's (3 + 5) x 12?`

预期输出：
```
用户输入：what's (3 + 5) x 12?

Agent响应：
  I need to solve the mathematical expression (3 + 5) x 12. First, I'll calculate the sum inside the parentheses, then multiply by 12.
  Let me break this down:
  1. Calculate 3 + 5
  2. Multiply the result by 12
  
  Let me use the available tools to solve this.
  
  Action: add
  Action Input: {"a": 3, "b": 5}
  
  Observation: 8
  
  Now I need to multiply this result by 12.
  
  Action: multiply
  Action Input: {"a": 8, "b": 12}
  
  Observation: 96
  
  So the final answer is 96.
  
  Final Answer: 96
```

## 6. 代码结构说明

| 文件 | 功能 |
|------|------|
| `math_mcp_server.py` | MCP 数学服务器实现 |
| `math_mcp_client_stdio.py` | stdio 方式客户端测试 |
| `math_mcp_client_sse.py` | sse 方式客户端测试 |
| `math_mcp_client_streamable_http.py` | streamable-http 方式客户端测试 |

## 7. 注意事项

1. **API 密钥**：测试用例中使用的是示例 API 密钥，实际使用时请替换为自己的密钥
2. **服务器端口**：默认使用 8000 端口，确保该端口未被占用
3. **传输方式兼容性**：客户端和服务器的传输方式必须匹配
4. **sse 方式**：已被标记为废弃，推荐使用 streamable-http 方式
5. **streamable-http 方式**：需要先启动服务器，再运行客户端

## 8. 故障排除

### 8.1 连接失败

- 检查服务器是否已启动
- 检查传输方式是否匹配
- 检查端口是否被占用
- 检查网络连接是否正常

### 8.2 工具调用失败

- 检查参数类型是否正确
- 检查参数名称是否与工具定义一致
- 检查是否有权限调用该工具

### 8.3 API 调用失败

- 检查 API 密钥是否有效
- 检查网络连接是否正常
- 检查模型是否支持相应功能

## 9. 总结

MCP 提供了三种灵活的连接方式，满足不同场景的需求：
- **stdio**：适合本地开发和测试
- **sse**：已废弃，不推荐使用
- **streamable-http**：推荐用于生产环境

通过本文档的介绍，您应该能够理解并使用这三种连接方式，以及如何运行相应的测试用例。