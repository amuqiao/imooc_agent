from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage


def test_ollama_stream_chat():
    """测试使用 langchain 调用本地 ollama 模型进行流式对话"""
    # 初始化 ChatOllama，指定模型
    llm = ChatOllama(
        model="gemma3:1b",
        # 可以根据需要调整温度等参数
        temperature=0.7,
    )

    # 定义系统提示
    system_prompt = SystemMessage(
        content="你是一个乐于助人的AI助手，请用简洁明了的方式回答用户的问题。"
    )

    # 定义用户问题
    user_question = HumanMessage(content="你好！能给我简要介绍一下人工智能吗？")

    # 发送消息并获取流式响应
    messages = [system_prompt, user_question]

    print("=== AI 流式对话测试 ===")
    print(f"用户: {user_question.content}")
    print("AI: ", end="", flush=True)

    # 使用 stream 方法获取流式响应
    full_response = ""
    for chunk in llm.stream(messages):
        chunk_content = chunk.content
        print(chunk_content, end="", flush=True)
        full_response += chunk_content

    print()
    print("=" * 30)

    # 测试多轮流式对话
    follow_up_question = HumanMessage(content="人工智能有哪些常见的应用？")

    messages.append(full_response)
    messages.append(follow_up_question)

    print(f"用户: {follow_up_question.content}")
    print("AI: ", end="", flush=True)

    follow_up_full_response = ""
    for chunk in llm.stream(messages):
        chunk_content = chunk.content
        print(chunk_content, end="", flush=True)
        follow_up_full_response += chunk_content

    print()
    print("=" * 30)

    return full_response, follow_up_full_response


if __name__ == "__main__":
    test_ollama_stream_chat()
