# 第一步：实例化大模型

```python
llm = ChatOpenAI(
    model="qwen-plus",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key="sk-xxx",
    streaming=True,
)
```

注意 api_key 会提示：Expected type 'SecretStr | None', got 'str' instead 错误

### 使用SecretStr类型对api_key进行加密

安装 pydantic：

```bash
uv add pydantic
```

**Pydantic** 是一个基于 Python 类型注解（type hints）的**数据验证与解析库**，广泛用于数据模型定义、数据验证、序列化和反序列化。它通过定义类（继承自 `BaseModel`）和类型注解，自动验证输入数据的结构和类型，确保数据符合预期格式，并提供清晰的错误信息。官网：https://docs.pydantic.dev/

可以使用 SecretStr 进行优化：

```python
from pydantic import SecretStr

api_key=SecretStr("sk-096bd79968744404807b9b3295d98247"),
```

llm 对象打印效果：

```bash
client=<openai.resources.chat.completions.completions.Completions object at 0x10796dd30> async_client=<openai.resources.chat.completions.completions.AsyncCompletions object at 0x10796e7b0> root_client=<openai.OpenAI object at 0x106ae2e40> root_async_client=<openai.AsyncOpenAI object at 0x10796de80> model_name='qwen-max-latest' temperature=0.0 model_kwargs={} openai_api_key=SecretStr('**********') openai_api_base='https://dashscope.aliyuncs.com/compatible-mode/v1'
```

# 第二步：初始化提示词模板

```mermaid
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一名资深的开发工程师，叫做小慕"),
    ("human", "{user_input}"),
])
```

### 常用的提示词模板

### `PromptTemplate`（字符串提示模板）

**适用场景**：

- 用于**文本补全模型**，输入是纯文本（单字符串）。
- 适用于简单的任务，例如生成一段文本、回答问题或执行指令。

**特点**：

- **输入变量插值**：通过 `{}` 占位符动态替换变量。
- **模板格式**：支持 `f-string`。
- **输出形式**：生成一个完整的字符串作为模型输入。

**示例：**

```python
template_prompt = PromptTemplate.from_template("今天{something}真不错")
print(template_prompt) # input_variables=['something'] input_types={} partial_variables={} template='今天{something}真不错'

formatted_prompt = template_prompt.format(something="天气")
print(formatted_prompt) # 今天天气真不错
```

### `ChatPromptTemplate`（聊天提示模板）

**适用场景**：

- 用于**聊天模型**（如 ChatGPT / 通义千问等），输入是多轮对话的消息列表（`SystemMessage`、`HumanMessage`、`AIMessage` 等）。
- 适用于需要模拟多轮对话或角色扮演的场景。

**特点**：

- **多消息类型支持**：可以组合系统指令、用户输入和助手回复。
- **消息格式化**：生成结构化的消息列表，供聊天模型处理。
- **灵活性**：支持动态替换变量（如 `SystemMessage` 中的占位符）。

```mermaid
system_message = "你是一位{role}专家，擅长回答{domain}领域的问题。"
human_message = "{question}"

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", system_message),
    ("human", human_message)
])

# 格式化消息
formatted_messages = chat_prompt.format_messages(
    role="技术",
    domain="Web开发",
    question="如何构建一个基于Vue的前端应用？"
)
print(formatted_messages)
"""
[
  SystemMessage(content='你是一位技术专家，擅长回答Web开发领域的问题。', additional_kwargs={}, response_metadata={}),
  HumanMessage(content='如何构建一个基于Vue的前端应用？', additional_kwargs={}, response_metadata={})
]
"""
```

python基础知识扩充：

这里的 `("system", system_message)`是 python 的 tuple 类型

**Tuple（元组）**：

- **有序**：元素按顺序排列，支持索引和切片操作。
- **不可变**：**创建后无法修改（不能增删改元素）**。
- **定义方式**：使用圆括号 `()` 或直接逗号分隔元素。

**Array（数组）**：相当于 JS 中的 Array

- **可变**：可以动态添加、删除或修改元素。
- **有序**：元素按顺序排列，支持索引和切片。

**Dict（字典）**：相当于 JS 中的 Object

- **无序**：元素（键值对）没有固定顺序。
- **可变**：可以动态添加、删除或修改键值对。
- **定义方式**：使用花括号 `{}`，键值对用冒号 `:` 分隔。

知识扩充：`ChatMessagePromptTemplate`可以结合 `ChatPromptTemplate`使用，同时对提示词模板和消息体进行抽象和复用：

```bash
system_template = ChatMessagePromptTemplate.from_template(
    template="你是一位{role}专家，擅长回答{domain}领域的问题。",
    role="system",
)

human_template = ChatMessagePromptTemplate.from_template(
    template="用户问题：{question}",
    role="human",
)

chat_prompt = ChatPromptTemplate.from_messages([
    system_template,
    human_template,
])

messages = chat_prompt.format_messages(
    role="技术",
    domain="Web开发",
    question="如何构建一个基于Vue的前端应用？"
)

print(messages)

"""
[
  ChatMessage(content='你是一位技术专家，擅长回答Web开发领域的问题。', additional_kwargs={}, response_metadata={}, role='system'),
  ChatMessage(content='用户问题：如何构建一个基于Vue的前端应用？', additional_kwargs={}, response_metadata={}, role='human')
]
"""
```

### `FewShotPromptTemplate`（少样本提示模板）

**适用场景**：

- 用于**少样本学习**（Few-Shot Learning），在提示中包含示例（Examples），帮助模型理解任务。
- 适用于复杂任务（如翻译、分类、推理），需要通过示例引导模型行为。

**特点**：

- **示例嵌入**：通过 `examples` 参数提供示例输入和输出。
- **动态示例选择**：支持 `ExampleSelector` 动态选择最相关的示例。
- **模板格式**：通常包含前缀（Prefix）、示例（Examples）和后缀（Suffix）。

**示例**：

```bash
# 定义示例模板
example_template = "输入: {input}\n输出: {output}"

# 创建示例
examples = [
    {"input": "将'Hello'翻译成中文", "output": "你好"},
    {"input": "将'Goodbye'翻译成中文", "output": "再见"},
]

# 创建少样本模板
few_shot_prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=PromptTemplate.from_template(example_template),
    prefix="请将以下英文翻译成中文：",
    suffix="输入: {text}\n输出:",
    input_variables=["text"]
)

# 格式化提示
formatted_prompt = few_shot_prompt.format(text="Thank you")
print(formatted_prompt)

"""
请将以下英文翻译成中文：

输入: 将'Hello'翻译成中文
输出: 你好

输入: 将'Goodbye'翻译成中文
输出: 再见

输入: Thank you
输出:
"""
```

### **总结对比**

### 常用模板类特性和使用场景对比

| **子类** | **适用模型类型** | **输入类型** | **主要用途** |
| --- | --- | --- | --- |
| `PromptTemplate` | 文本补全模型 | 单字符串 | 生成单轮文本任务的提示 |
| `ChatPromptTemplate` | 聊天模型 | 多消息列表 | 模拟多轮对话或角色扮演 |
| `FewShotPromptTemplate` | 所有模型 | 包含示例的模板 | 通过示例引导模型完成复杂任务 |

**常用提示词模板类的继承关系**

mermaid图，待补充

**第三步：链式调用大模型**

`chain = prompt | llm

response = chain.stream({"user_input": "计算100+100"})
# response = chain.stream(input={"user_input": "计算100+100"})

for chunk in response:
    print(chunk.content, end="")`
**绑定自定义工具
第一步：开发工具函数**

```bash
def add(a, b):
    return a + b
```

# 第二步：将工具函数转为LangChain Tool对象

LangChain中的工具（Tool）是一个封装了特定功能的类，它包含四个核心组成部分：

- 名称（name）：名称是工具在工具集合中的**唯一标识符**，必须确保在同一工具集中不重复
- 描述（description）：描述用于说明工具的功能，为LLM或代理提供上下文信息，**帮助模型理解何时以及如何调用该工具**
- 参数模式（args_schema）：是使用Pydantic BaseModel定义的输入参数结构，用于验证和解析工具调用的参数
- 是否直接返回（return_direct）：布尔值属性，当设置为True时，智能体会在调用工具后立即返回结果给用户，而不继续调用其他工具

```bash
class AddInputArgs(BaseModel):
    a: str = Field(description="first number")
    b: str = Field(description="second number")

@tool(
    description="add two numbers",
    args_schema=AddInputArgs,
    return_direct=True,
)
def add(a, b):
    """add two numbers"""
    return a + b
```

方法1：使用Tool.from_function生成

```bash
add_tools = Tool.from_function(
    func=add,
    name="add",
    description="计算两个数相加"
)
```

方法2：使用@tool装饰器生成

```bash
@tool
def add(a, b):
    """add two numbers"""
    return a + b
```

**第三步：将大模型和Tool对象绑定**

```bash
llm_with_tools = llm.bind_tools([add_tools])
```

**第四步：调用大模型，尝试让大模型调用工具**

```bash
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一名资深的开发工程师，叫做小慕"),
    ("human", "{user_input}"),
])

chain = prompt | llm_with_tools

response = chain.invoke({"user_input": "计算100+100"})
```

此时response会返回：

```bash
content='' additional_kwargs={'tool_calls': [{'index': 0, 'id': 'call_861b180aecc64989a1cbc7', 'function': {'arguments': '{"__arg1": "100 100"}', 'name': 'add'}, 'type': 'function'}]} response_metadata={'finish_reason': 'tool_calls', 'model_name': 'qwen-plus'} id='run--2e1ac07a-9956-4a86-b26b-a0c8555620c6-0' tool_calls=[{'name': 'add', 'args': {'__arg1': '100 100'}, 'id': 'call_861b180aecc64989a1cbc7', 'type': 'tool_call'}]
```

# 第五步：调用工具

根据大模型返回的Tools结果执行函数：

```bash
for tool_calls in resp.tool_calls:
    print(tool_calls)

    args = tool_calls['args']
    func_name = tool_calls['name']

    func = tools_dict[func_name]
    tool_content = func.invoke(args)
    print(tool_content)
```