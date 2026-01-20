# 为什么需要多轮对话能力

- 一轮对话无法完全解决用户问题，需要继续追问
- 由于大模型上下文限制，无法一次性回答全部问题（比如：写代码、写小说等）
- 需要记忆上次会话内容，继续开始下次会话

# 构建session级别的多轮对话能力

架构设计：

**LCEL**（LangChain Expression Language）是LangChain框架中用于高效构建和组合语言模型应用链的声明式表达式语言‌，具有异步支持、并行处理和集成监控等核心特性。‌‌

**‌LCEL核心定义与作用‌**

LCEL通过提供统一的编程接口和组合原语，简化了LangChain框架中组件（如提示模板、模型、输出解析器）的串联流程。开发者可通过类似Unix管道符（|）的语法快速构建应用链，例如：chain = prompt | model | output_parser。‌‌

‌**典型应用场景‌**

‌复杂对话链构建‌：如结合多个模型和解析器生成结构化输出；‌‌

‌并行处理优化‌：自动并行执行可独立运行的组件（如多检索器文档获取）。‌‌

# 第一步：构建提示词模板

这里在对话中注入了`MessagesPlaceholder`，用于注入对话历史：

```bash
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个技术专家，擅长解决各种Web开发中的技术问题"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}"),
])
```

# 第二步：创建大模型实例

这里使用 Anthropic 的 claude 大模型，因为需要借助它强大的编码能力：

```bash
llm = ChatAnthropic(
    base_url="https://api.aiclaude.site",
    api_key="sk-xxx",
    model_name="claude-3-7-sonnet-20250219"
)
```

# 第三步：构建链式调用

将提示词模板、大模型、输出结构化结合在一起使用：

```bash
chain = prompt | llm | StrOutputParser()
```

# 第四步：构建基于历史消息的Runnable实例

又分为三小步：

### 4.1 创建session存储对象

```bash
store = {}
```

### 4.2 创建获取session的函数

根据 session_id 获取 session 内容，如果 session_id 不存在时进行创建：

```bash
from langchain_community.chat_message_histories import ChatMessageHistory

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    print(store)
    return store[session_id]
```

**4.3 创建 runnable 实例**

```bash
chain_with_history = RunnableWithMessageHistory(
    runnable=chain,
    get_session_history=get_session_history,
    input_messages_key="question",
    history_messages_key="chat_history",
)
```

**第五步：构建多轮对话**

```bash
import uuid

def run_conversation():
    session_id = uuid.uuid4()
    while True:
        user_input = input("用户：")
        if user_input.lower() == "exit":
            break

        response = chain_with_history.invoke(
            {"question": user_input},
            config={"configurable": {"session_id": session_id}},
        )

        print("助手：")
        for chunk in response:
            print(chunk, end="")
        print("\n")
```

**第六步：运行多轮对话**

```bash
if __name__ == "__main__":
    run_conversation()
```

```bash
# 执行后，先生成 session_id：
session_id 8bfa86f0-740c-4532-8709-cccb65506b54
# 用户手动输入需求：
用户：写一个python的快速排序算法
# 生成 ChatMessageHistory 实例：
{UUID('8bfa86f0-740c-4532-8709-cccb65506b54'): InMemoryChatMessageHistory(messages=[])}
```

获得响应结果：

```bash
助手：
# Python 快速排序算法

快速排序是一种高效的排序算法，基于分治法的思想。以下是Python实现的快速排序算法：

```python
def quick_sort(arr):
    """
    快速排序函数
    :param arr: 待排序的列表
    :return: 排序后的列表
    """
    if len(arr) <= 1:
        return arr
    else:
        pivot = arr[0]  # 选择第一个元素作为基准
        # 分区操作
        less = [x for x in arr[1:] if x <= pivot]  # 小于等于pivot的元素
        greater = [x for x in arr[1:] if x > pivot]  # 大于pivot的元素
        
        # 递归排序并合并结果
        return quick_sort(less) + [pivot] + quick_sort(greater)
```

另一种实现方式（原地排序，更节省内存）：

```python
def quick_sort_in_place(arr, low, high):
    """
    原地快速排序
    :param arr: 待排序的列表
    :param low: 起始索引
    :param high: 结束索引
    """
    if low < high:
        # 找到分区点
        pivot_index = partition(arr, low, high)
        
        # 递归排序左右两部分
        quick_sort_in_place(arr, low, pivot_index - 1)
        quick_sort_in_place(arr, pivot_index + 1, high)

def partition(arr, low, high):
    """
    分区操作
    :param arr: 待分区的列表
    :param low: 起始索引
    :param high: 结束索引
    :return: 基准元素的最终位置
    """
    pivot = arr[high]  # 选择最后一个元素作为基准
    i = low - 1  # 小于等于pivot的区域的指针
    
    for j in range(low, high):
        # 如果当前元素小于或等于pivot
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]  # 交换元素
    
    # 将pivot放到正确的位置
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1

# 使用示例
def sort_array(arr):
    """
    使用快速排序对数组进行排序
    :param arr: 待排序的列表
    :return: 排序后的列表
    """
    if not arr:
        return []
    
    quick_sort_in_place(arr, 0, len(arr) - 1)
    return arr
```

快速排序的平均时间复杂度为O(n log n)，最坏情况下为O(n²)，但通过优化基准元素的选择（例如三数取中法）可以减少最坏情况的发生。快速排序是实践中最常用和最高效的排序算法之一。
```

用户可以持续提问，可以看到会话消息被缓存：

# 多轮对话能力持久化（复杂度高）

需要基于上一步的基础上进行改造

# 第一步：定义文件系统根路径

```bash
# ==================== 4. 文件系统存储 ====================
DATA_DIR = "data/conversations"
```

# 第二步：根据session_id获取文件名

目录结构为：`data/conversations/user_id/session_id`

```bash
data/conversations/user1/user1_82b8d5d4-8ebf-4a55-a892-426542deb8c8.json
```

通过 session_id 解析出 user_id，生成完整的文件路径：

```bash
def get_file_path(session_id):
    """根据会话 ID 生成文件路径"""
    user_id = session_id.split("_")[0]  # 假设 session_id 格式为 "user_id_session"
    dir_path = os.path.join(DATA_DIR, user_id)
    os.makedirs(dir_path, exist_ok=True)
    return os.path.join(dir_path, f"{session_id}.json")
```

# 第三步：根据session_id存储和读取对话json文件内容

存储：

```bash
def save_conversation_history(session_id, messages):
    """将历史记录保存到文件"""
    file_path = get_file_path(session_id)
    data = [
        {
            "session_id": session_id,
            "sender": "user" if isinstance(msg, HumanMessage) else "assistant",
            "content": msg.content,
            "timestamp": datetime.now().isoformat(),
        }
        for msg in messages
    ]
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
```

读取：

```bash
def load_conversation_history(session_id):
    """从文件中加载历史记录为消息列表"""
    file_path = get_file_path(session_id)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return [
                HumanMessage(content=msg["content"]) if msg["sender"] == "user"
                else AIMessage(content=msg["content"])
                for msg in json.load(f)
            ]
    except (FileNotFoundError, json.JSONDecodeError):
        return []
```

**第四步：改造get_session_history方法**

```bash
def get_session_history(session_id):
    """返回对应会话的历史记录（返回 BaseChatMessageHistory 实例）"""
    history = load_conversation_history(session_id)
    return InMemoryChatMessageHistory(messages=history)
```

# 第五步：改造运行会话方法

核心改动是：

```bash
# 构建新消息并保存
new_messages = load_conversation_history(session_id) + [HumanMessage(user_input), AIMessage(response)]
save_conversation_history(session_id, new_messages)
```

完整代码：

```bash
def run_conversation():
    user_id = "user1"
    # session_id = user_id + "_" + str(uuid.uuid4())  # 生成唯一会话 ID
    session_id = user_id + "_" + "82b8d5d4-8ebf-4a55-a892-426542deb8c8"  # 根据已有session会话生成
    print(f"\n[会话开始] 会话 ID: {session_id}")

    while True:
        try:
            user_input = input("用户: ")
            if user_input.lower() in ["退出", "exit"]:
                break

            # 获取历史 + 当前输入 -> 模型响应 -> 更新历史
            response = chain_with_history.invoke(
                {"question": user_input},
                config={"configurable": {"session_id": session_id}},
            )

            # 构建新消息并保存
            new_messages = load_conversation_history(session_id) + [HumanMessage(user_input), AIMessage(response)]
            save_conversation_history(session_id, new_messages)

            print(f"助手: {response}")

        except KeyboardInterrupt:
            print("\n用户中断了对话。")
            break

    print("[会话结束] 历史已保存至文件。")

if __name__ == "__main__":
    run_conversation()
```

**优化对话持久化（简单）**

```bash
from langchain_community.chat_message_histories import FileChatMessageHistory

def get_session_history(session_id: str):
    return FileChatMessageHistory(f"{session_id}.txt")
```