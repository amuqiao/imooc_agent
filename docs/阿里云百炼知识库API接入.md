# 阿里云百炼知识库API接入指南

## 一、API接入概述

本文档提供了阿里云百炼知识库的API接入指南，包括基础配置、客户端创建、知识库查询等操作。

## 二、环境准备

### 2.1 安装依赖

```bash
uv pip install alibabacloud_bailian20231229==2.8.1
uv add alibabacloud_bailian20231229==2.8.1
```

### 2.2 配置环境变量

```python
import os

# 请使用环境变量或配置文件管理这些敏感信息
os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'] = "your_access_key_id"
os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET'] = "your_access_key_secret"
os.environ['WORKSPACE_ID'] = "your_workspace_id"
os.environ['INDEX_ID'] = "your_index_id"
```

## 三、API调用示例

### 3.1 创建百炼客户端

```python
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_bailian20231229 import client as bailian_20231229_client

def create_client() -> bailian_20231229_client.Client:
    config = open_api_models.Config(
        access_key_id=os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_ID'),
        access_key_secret=os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_SECRET')
    )
    config.endpoint = 'bailian.cn-beijing.aliyuncs.com'
    return bailian_20231229_client.Client(config=config)
```

### 3.2 查询知识库

```python
from alibabacloud_bailian20231229 import models as bailian_20231229_models
from alibabacloud_tea_util import models as util_models

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
```

## 四、最佳实践

1. **敏感信息管理**：使用环境变量或配置文件管理AccessKey等敏感信息
2. **错误处理**：添加适当的错误处理机制
3. **日志记录**：记录API调用日志，便于排查问题
4. **性能优化**：合理设置超时时间和重试机制

## 五、参考文档

- [阿里云百炼API文档](https://api.aliyun.com/api/bailian/2023-12-29/Retrieve)
- [阿里云SDK使用指南](https://help.aliyun.com/document_detail/101228.html)
