# AppleScript介绍

‌osascript是macOS系统中用于执行AppleScript脚本的命令行工具‌，主要用于自动化任务或控制应用程序。启动Safari浏览器，可以使用如下脚本：

```bash
osascript -e 'tell application "Safari" to activate'
```

#

步骤1：封装mcp stdio客户端通用方法

```bash
from langchain_mcp_adapters.client import MultiServerMCPClient

async def create_mcp_stdio_client(name, params):
    config = {
        name: {
            "transport": "stdio",
            **params,
        }
    }
    print(config)
    client = MultiServerMCPClient(config)

    tools = await client.get_tools()

    return client, tools
```

**步骤2：开发终端控制相关工具**

**通用方法封装**

```bash
import subprocess

def run_applescript(script):
    """调用 osascript 执行 AppleScript，并返回输出"""
    process = subprocess.Popen(["osascript", "-e", script],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    output, error = process.communicate()
    return output.decode('utf-8').strip(), error.decode('utf-8').strip()

def run_script(script):
    terminal_content, error = run_applescript(script)
    if error:
        print('\nrun_script error:')
        print(error)
        print('-' * 50)
    # else:
    # print('\nrun_script success:')
    # print(terminal_content)
    # print('-' * 50)
    return terminal_content, error
```

**工具1：关闭Terminal进程**

```bash
@mcp.tool(name="close_terminal_if_open", description="close terminal if terminal was open")
def close_terminal_if_open(args: str="") -> bool:
    terminal_content, error = run_script('''
tell application "System Events"
    if exists process "Terminal" then
        tell application "Terminal" to quit
    end if
end tell
''')
    if error:
        return False
    else:
        return True
```

**工具2：打开新的Terminal窗口**

```bash
@mcp.tool(name="open_new_terminal", description="open a new terminal, return window id of terminal")
def open_new_terminal(args: str="") -> str:
    terminal_content, error = run_script('''
tell application "Terminal"
    if (count of windows) > 0 then
        activate
    else
        activate
    end if
end tell
''')
    time.sleep(5)  # 等待5秒钟，Terminal打开需要一段时间
    if error:
        return error
    else:
        if terminal_content.strip() == "":
            return get_all_terminal_window_ids()[0]
        else:
            return terminal_content
```

**获取Terminal的window id**

```bash
def get_all_terminal_window_ids(args=None):
    script = """
tell application "Terminal"
    set outputList to {}
    repeat with aWindow in windows
        set windowID to id of aWindow
        set tabCount to number of tabs of aWindow
        repeat with tabIndex from 1 to tabCount
            set end of outputList to {tab tabIndex of window id windowID}
        end repeat
    end repeat
end tell
return outputList
"""
    terminal_content, error = run_script(script)
    if error:
        return error
    else:
        # 检查字符串中是否包含逗号
        if ',' in terminal_content:
            # 将字符串按逗号分割成列表
            list_data = terminal_content.split(",")
            list_data = [item.strip() for item in list_data]
        else:
            # 如果不包含逗号，将整个字符串作为一个元素放入列表
            list_data = [terminal_content.strip()]
        return list_data
```

**工具3：获取终端的显示内容**

```bash
@mcp.tool(name="get_terminal_full_text", description="get full text from terminal")
def get_terminal_full_text(args: str="") -> str:
    terminal_content, error = run_script('''
tell application "Terminal"
    set fullText to history of selected tab of front window
end tell
''')
    if error:
        return error
    else:
        return terminal_content
```

**工具4：向终端内输入脚本**

```bash
@mcp.tool(name="run_script_in_exist_terminal", description="run script in an existing terminal")
def run_script_in_exist_terminal(command: str) -> str:
    command = clean_bash_tags(command)  # 清除markdown字符串
    print('\nrun_script_in_exist_terminal command:')
    print(command)
    print('-' * 50)
    terminal_content, error = run_script(f'''
tell application "Terminal"
    activate
    if (count of windows) > 0 then
        do script "{command}" in window 1
    else
        do script "{command}"
    end if
end tell
''')
    if error:
        return error
    else:
        return terminal_content
```

**清除markdown字符串**

```bash
def clean_bash_tags(s):
    # 同时匹配开头和结尾的标记及周围可能的空白（包括换行符）
    s = re.sub(r'^\s*```bash\s*', '', s, flags=re.DOTALL)  # 去开头
    s = re.sub(r'^\s*```shell\s*', '', s, flags=re.DOTALL)  # 去开头
    s = re.sub(r'\s*```\s*$', '', s, flags=re.DOTALL)      # 去结尾
    return s.strip()
```

**工具5：向终端内输入按键**

```bash
@mcp.tool(name="send_terminal_keyboard_key", description="send a terminal keyboard key to an existing terminal")
def send_terminal_keyboard_key(key_codes: List[str]) -> bool:
    print('\nsend_terminal_keyboard_key keycode:', key_codes)
    print('-' * 50)
    script = f'''
    tell application "Terminal"
        activate
        tell application "System Events"
            {concat_key_codes(key_codes)}
        end tell
    end tell
    '''
    print(script)
    terminal_content, error = run_script(script)
    if error:
        return False
    else:
        return True
```

**keycode解析和处理**

```bash
def parse_key_code(button):
    button = button.lower()

    keycode_map = {
        'return': 'return',
        'space': 'space',
        'up': 126,
        'down': 125,
        'left': 123,
        'right': 124,
        'a': 0,
        'b': 11,
        'c': 8,
        'd': 2,
        'e': 14,
        'f': 3,
        'g': 5,
        'h': 4,
        'i': 34,
        'j': 38,
        'k': 40,
        'l': 37,
        'm': 46,
        'n': 45,
        'o': 31,
        'p': 35,
        'q': 12,
        'r': 15,
        's': 1,
        't': 17,
        'u': 32,
        'v': 9,
        'w': 13,
        'x': 7,
        'y': 16,
        'z': 6,
        '.': 47,
        'dot': 47,
        '0': 29,
        '1': 18,
        '2': 19,
        '3': 20,
        '4': 21,
        '5': 23,
        '6': 22,
        '7': 26,
        '8': 28,
        '9': 25,
        '-': 27,
    }

    return keycode_map[button]

def concat_key_codes(key_codes):
    script = ''
    for key in key_codes:
        key_code = parse_key_code(key)
        script += f'keystroke {key_code}\n'
        script += 'delay 0.5\n'
    return script.strip()
```

**步骤3：封装获取mcp tools的通用方法**

```bash
from app.utils.mcp import create_mcp_stdio_client

async def get_stdio_terminal_tools():
    params = {
        "command": "python",
        "args": [
            "/Users/sam/Xiaoluyy/ai/coding_agent/app/mcp/terminal.py",
        ],
    }

    client, tools = await create_mcp_stdio_client("terminal", params)

    return tools
```

**步骤4：创建提示词模板**

```bash
from langchain_core.prompts import PromptTemplate

def run_script_in_terminal_template():
    template = PromptTemplate.from_template("""你是一位技术专家，擅长各类脚本语句。

# 规范
- 严禁使用`rm`、`rm -rf`、`rm -r`、`rm -f`等删除命令！！！
- 执行脚本前，请先使用 close_terminal_if_open 关闭所有终端，再使用 open_new_terminal 打开一个新的终端
- 使用 run_script_in_exist_terminal 在终端内执行脚本语句，执行完成后使用 get_terminal_full_text 查看执行结果（会包含当前终端中的所有文本）
- 如果发现需要交互的场景，使用 send_terminal_keyboard_key 向终端发送控制命令，常用的控制命令如下：
    - 键盘向上：up
    - 键盘向下：down
    - 键盘向左：left
    - 键盘向右：right
    - 回车键：return
    - 空格键：space
- 工具 send_terminal_keyboard_key 调用时需要传入一个按键数组，示例如下：
```python
# 向上点击键盘
send_terminal_keyboard_key(["up"])

# 先输入向下，再输入回车
send_terminal_keyboard_key(["down", "return"])
```
- 如果出现下面的列表页面，说明需要选择，请看示例：
```bash
◆  "vue3" isn't a valid template. Please choose from below:
│  ● Vanilla
│  ○ Vue
│  ○ React
│  ○ Preact
│  ○ Lit
│  ○ Svelte
│  ○ Solid
│  ○ Qwik
│  ○ Angular
│  ○ Marko
│  ○ Others
└
```
此时如果要选中“React”，可以通过向Terminal输入两次向下按键后，再按回车键实现，方法如下：
```python
send_terminal_keyboard_key(["down", "down", "return"])
```
也可以分三次输入：
```python
send_terminal_keyboard_key(["down"])
send_terminal_keyboard_key(["down"])
send_terminal_keyboard_key(["return"])
```

- 如果出现下面的内容，说明需要输入项目名称：
```bash
│
◆  Project name:
│  vite-project
└
```
你需要使用 send_terminal_keyboard_key 工具，向 Terminal 一个一个输入项目名称字符，并按回车键确认，如：
```python
send_terminal_keyboard_key(["v", "u", "e", "3", "-", "p", "r", "o", "j", "e", "c", "t", "return"])
```

- 使用 `vue create` 命令初始化 vue 项目

# 问题
{question}
""")

    return template
```

**步骤5：创建智能体引用终端工具并运行**

```bash
import asyncio

from langchain.agents import initialize_agent, AgentType

from app.models.qwen import llm_qwen
from app.prompts.run_script_in_terminal import run_script_in_terminal_template
from app.tools.rag import get_stdio_rag_tools
from app.tools.terminal import get_stdio_terminal_tools

async def exec_command_in_terminal():
    terminal_tools = await get_stdio_terminal_tools()
    rag_tools = await get_stdio_rag_tools()
    tools = terminal_tools + rag_tools
    print(tools)

    agent = initialize_agent(
        llm=llm_qwen,
        tools=tools,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        max_iterations=50,
    )

    prompt_template = run_script_in_terminal_template()
    prompt = prompt_template.format(question="在 /Users/sam/llm/.temp/vue3-test 目录下初始化一个vue3的新项目并启动项目")

    resp = await agent.ainvoke(prompt)
    print(resp['output'])

    return resp

asyncio.run(exec_command_in_terminal())
```
