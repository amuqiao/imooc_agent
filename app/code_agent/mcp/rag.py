#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
百炼知识库 MCP 工具
用于从百炼平台查询知识库
"""

import os
import sys
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# 导入阿里云百炼相关模块
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_bailian20231229 import client as bailian_20231229_client
from alibabacloud_bailian20231229 import models as bailian_20231229_models
from alibabacloud_tea_util import models as util_models

# 加载环境变量
load_dotenv()

# 创建 MCP 实例
mcp = FastMCP()


def create_client() -> bailian_20231229_client.Client:
    """
    创建并配置阿里云百炼客户端。

    返回:
        bailian_20231229_client.Client: 配置好的客户端。
    """
    # 从环境变量获取配置
    access_key_id = os.getenv('accessKeyId')
    access_key_secret = os.getenv('accessKeySecret')

    # 验证配置
    if not access_key_id:
        raise ValueError("accessKeyId 配置未找到，请在 .env 文件中设置")
    if not access_key_secret:
        raise ValueError("accessKeySecret 配置未找到，请在 .env 文件中设置")

    config = open_api_models.Config(
        access_key_id=access_key_id,
        access_key_secret=access_key_secret
    )
    config.endpoint = 'bailian.cn-beijing.aliyuncs.com'
    return bailian_20231229_client.Client(config=config)


def retrieve_index(client, workspace_id, index_id, query):
    """
    在指定的知识库中检索信息。

    参数:
        client (bailian_20231229_client.Client): 客户端（Client）。
        workspace_id (str): 业务空间ID。
        index_id (str): 知识库ID。
        query (str): 原始输入prompt。

    返回:
        阿里云百炼服务的响应。
    """
    headers = {}
    retrieve_request = bailian_20231229_models.RetrieveRequest(
        index_id=index_id,
        query=query
    )
    runtime = util_models.RuntimeOptions()
    return client.retrieve_with_options(workspace_id, retrieve_request, headers, runtime)


@mcp.tool(name="query_rag_from_bailian", description="当需要获取特定领域的知识或信息时，从百炼平台知识库查询相关内容，传入需要查询的知识关键字即可")
def query_rag_from_bailian(query: str) -> str:
    """
    从百炼平台查询知识库

    参数:
        query (str): 需要查询的知识关键字

    返回:
        str: 查询到的知识内容
    """
    try:
        # 创建百炼客户端
        bailian_client = create_client()

        # 从环境变量获取配置
        workspace_id = os.getenv('workspace_id')
        index_id = os.getenv('knowledge_base_id')

        # 验证配置
        if not workspace_id:
            return "错误：workspace_id 配置未找到，请在 .env 文件中设置"
        if not index_id:
            return "错误：knowledge_base_id 配置未找到，请在 .env 文件中设置"

        # 查询知识库
        rag = retrieve_index(bailian_client, workspace_id, index_id, query)

        # 处理查询结果
        if rag.body and hasattr(rag.body, 'data') and rag.body.data:
            if hasattr(rag.body.data, 'nodes') and rag.body.data.nodes:
                # 拼接查询结果
                result = ""
                index = 1
                for data in rag.body.data.nodes:
                    result += f"第{index}段知识：\n    {data.text}\n    --\n    "
                    index += 1
                # 打印 RAG 工具的结果
                print("\n=== RAG 工具查询结果 ===")
                print(result)
                print("====================\n")
                return result
            else:
                no_result_msg = "未找到相关知识节点"
                print("\n=== RAG 工具查询结果 ===")
                print(no_result_msg)
                print("====================\n")
                return no_result_msg
        else:
            # 处理错误情况
            error_message = "未知错误"
            if rag.body:
                if hasattr(rag.body, 'Message'):
                    error_message = rag.body.Message
                elif hasattr(rag.body, 'message'):
                    error_message = rag.body.message
            error_msg = f"查询失败: {error_message if rag.body else '无响应数据'}"
            print("\n=== RAG 工具查询结果 ===")
            print(error_msg)
            print("====================\n")
            return error_msg
    except Exception as e:
        error_msg = f"执行错误: {str(e)}"
        print("\n=== RAG 工具查询结果 ===")
        print(error_msg)
        print("====================\n")
        return error_msg


if __name__ == '__main__':
    """
    运行 MCP 工具
    """
    mcp.run(transport="stdio")
