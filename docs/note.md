# 高德MCP服务介绍

https://lbs.amap.com/api/mcp-server/summary

# 高德MCP服务集成

# 第一步：MCP客户端开发

过程分为三个小步骤：

### 1.1 安装依赖

```bash
$ uv add langchain_mcp_adapters
```

### 1.2 获取高德应用key

https://lbs.amap.com/api/mcp-server/create-project-and-key

### 1.3 开发高德mcp客户端

```bash
from langchain_mcp_adapters.client import MultiServerMCPClient

async def create_mcp_client():
    amap_key = os.environ.get("AMAP_KEY")

    client = MultiServerMCPClient({
        "amap": {
            "url": f"https://mcp.amap.com/sse?key={amap_key}",
            "transport": "sse",
        }
    })

    tools = await client.get_tools()

    return client, tools
```

# 第二步：创建智能体，集成MCP工具

过程分为四个小步骤：

### 2.1 获取mcp tools

注意：要创建 async function

```bash
client, tools = await create_mcp_client()
```

**2.2 创建智能体**

```bash
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)
```

**2.3 创建提示词**

```bash
prompt_template = PromptTemplate.from_template(
    "你是一个智能助手，可以调用高德 MCP 工具。\n\n问题: {input}"
)

prompt = prompt_template.format(input="""
- 我五月底端午节计划去杭州游玩4天。
- 帮制作旅行攻略，考虑出行时间和路线，以及天气状况路线规划。
- 制作网页地图自定义绘制旅游路线和位置。
    - 网页使用简约美观页面风格，景区图片以卡片展示。
- 行程规划结果在高德地图app展示，并集成到h5页面中。
- 同一天行程景区之间我想打车前往。
""")
```

**2.4 异步运行智能体**

```bash
resp = await agent.ainvoke(prompt)
```

**第三步：异步运行程序**

```bash
import asyncio

asyncio.run(main())
```

运行结果：

```bash
{
  'input': '你是一个智能助手，可以调用高德 MCP 工具。\n\n问题: \n- 我五月底端午节计划去杭州游玩4天。\n- 帮制作旅行攻略，考虑出行时间和路线，以及天气状况路线规划。\n- 制作网页地图自定义绘制旅游路线和位置。\n    - 网页使用简约美观页面风格，景区图片以卡片展示。\n- 行程规划结果在高德地图app展示，并集成到h5页面中。\n    - 同一天行程景区之间我想打车前往。\n', 
  'output': '已为您规划杭州端午四日游完整攻略：\n\n一、天气建议\n5月20日小雨转中雨，建议首日游览西湖周边室内景点（雷峰塔/河坊街），21日晴天安排千岛湖深度游，22日多云游览灵隐寺/龙井村，23日雨天预留缓冲。\n\n二、行程安排\nDay1：西湖文化之旅\n10:00 西湖音乐喷泉（B0FFGOWPEV）→ 12:00 湖滨银泰午餐 → 14:00 雷峰塔景区（B023B09LKR）→ 17:00 河坊街（B0FFGQ772L）\n打车链接：amapuri://drive/takeTaxi?sourceApplication=amapplatform&slat=30.240742&slon=120.146696&sname=西湖音乐喷泉&dlon=120.159374&dlat=30.244066&dname=雷峰塔景区\n\nDay2：自然风光探索\n09:00 灵隐寺（B023B02842）→ 12:30 龙井村（B023B17X30）品茶 → 16:00 茶园徒步\n景区间距仅5公里，推荐骑行路线：amapuri://map/route?from=navi&to=120.091753,29.984802\n\nDay3：千岛湖深度游\n08:30 千岛湖景区（B023B1E89A）乘船游览梅峰岛/猴岛，16:00 返回市区\n驾车路线：amapuri://map/route?from=navi&to=119.046341,29.768676\n\n三、H5地图集成\n自定义地图链接：amapuri://workInAmap/createWithToken?polymericId=mcp_6670030fac8142858790afc5db56207e\n包含每日行程卡片式展示，点击POI可查看景区图片：\n- 西湖：https://store.is.autonavi.com/showpic/046f7db069e380fdc29375807debee83\n- 灵隐寺：http://store.is.autonavi.com/showpic/4aa0a6a1b6ee72c9833441f363cbb43a\n- 千岛湖：https://aos-comment.amap.com/B0FFGQ772L/comment/dfda683d7fd2855875b23a290a590d3b_2048_2048_80.jpg'}
```

# 能力扩展和优化

# 第一步：增加文件工具

安装 langchain_community：

```bash
$ uv add langchain_community
```

```bash
获取文件工具：
from langchain_community.agent_toolkits import FileManagementToolkit

file_toolkit = FileManagementToolkit(root_dir="/Users/sam/llm/.temp")
file_tools = file_toolkit.get_tools()
```

**第二步：扩展智能体工具**

```bash
agent = initialize_agent(
    tools=tools + file_tools,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)
```

**第三步：优化提示词**

```bash
 prompt = prompt_template.format(input="""
- 我五月底端午节计划去杭州游玩4天。
- 帮制作旅行攻略，考虑出行时间和路线，以及天气状况路线规划。
- 行程规划结果在高德地图app展示，并集成到h5页面中。
    - 同一天行程景区之间我想打车前往。
- 制作网页地图自定义绘制旅游路线和位置，并提供专属地图链接、打车链接、骑行路线、驾车路径等。
- 将网页保存到：/Users/sam/llm/.temp/amap.html
""")
```

此时智能体会生成旅行计划，并开发 amap.html 保存到本地文件夹中