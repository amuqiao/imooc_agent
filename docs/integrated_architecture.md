# AI 系统整合架构图

```mermaid
graph TB
    %% 严格使用预设配色+样式规范，统一圆角rx8 ry8，避免STYLESEPARATOR报错
    classDef level1 fill:#45B7D1,stroke:#2D3436,stroke-width:3px,color:white,rx:8,ry:8
    classDef level2 fill:#4ECDC4,stroke:#2D3436,stroke-width:2px,color:#2D3436,rx:8,ry:8
    classDef level3 fill:#96CEB4,stroke:#2D3436,stroke-width:2px,color:#2D3436,rx:8,ry:8
    classDef level4 fill:#FFEAA7,stroke:#2D3436,stroke-width:2px,color:#2D3436,rx:8,ry:8
    classDef nodeStyle fill:#E9ECEF,stroke:#2D3436,stroke-width:2px,color:#2D3436,rx:8,ry:8
    
    %% 第1层：AI Agent 运行环境（来自1.md）
    subgraph Level1["第1层：AI Agent 运行环境"]
        direction TB
        subgraph DockerEnv["Docker 环境"]
            mongodb1[mongodb]:::nodeStyle
            mysql1[mysql]:::nodeStyle
            nginx1[nginx]:::nodeStyle
        end
        subgraph OSEnv["操作系统环境"]
            chrome[chrome]:::nodeStyle
            powershell[powershell]:::nodeStyle
            terminal[terminal]:::nodeStyle
        end
    end
    
    %% 第2层：MCP 服务（来自2.md）
    subgraph Level2["第2层：MCP 服务"]
        direction TB
        mongodb2[mongodb]:::nodeStyle
        mysql2[mysql]:::nodeStyle
        faas[faas]:::nodeStyle
        nginx2[nginx]:::nodeStyle
        terminal2[terminal]:::nodeStyle
        browser[browser]:::nodeStyle
        files[files]:::nodeStyle
        rag[rag]:::nodeStyle
        docker[docker]:::nodeStyle
        apis[apis]:::nodeStyle
    end
    
    %% 第3层：AI 核心框架（来自3.md，移除大模型基座）
    subgraph Level3["第3层：AI 核心框架"]
        direction TB
        subgraph AIMonitor["AI 监控"]
            langsmith[langsmith]:::nodeStyle
            langfuse[langfuse]:::nodeStyle
        end
        
        subgraph AIAgentFrame["AI Agent 框架"]
            langgraph[langgraph]:::nodeStyle
            subgraph langchain["langchain"]
                agents[agents]:::nodeStyle
                tools[tools]:::nodeStyle
                mcp[MCP]:::nodeStyle
                prompts[prompts]:::nodeStyle
                memory[memory]:::nodeStyle
                parsers[parsers]:::nodeStyle
            end
        end
        
        subgraph AIIde["AI IDE"]
            cursor[cursor]:::nodeStyle
        end
    end
    
    %% 第4层：大模型基座（来自3.md，提升为第4层）
    subgraph Level4["第4层：大模型基座"]
        direction TB
        qwen3[qwen3]:::nodeStyle
        DeepSeekR1[DeepSeekR1]:::nodeStyle
    end
    
    %% 层级关系连线
    Level1 --> Level2
    Level2 --> Level3
    Level3 --> Level4
    
    %% 绑定样式
    style Level1 level1
    style Level2 level2
    style Level3 level3
    style Level4 level4
    style DockerEnv level2
    style OSEnv level2
    style AIMonitor level3
    style AIAgentFrame level3
    style AIIde level3
    style langchain nodeStyle
end
```

## 架构说明

### 第1层：AI Agent 运行环境
- **Docker 环境**：包含 mongodb、mysql、nginx 等服务容器
- **操作系统环境**：包含 chrome 浏览器、powershell、terminal 等运行时工具

### 第2层：MCP 服务
- 提供 mongodb、mysql、faas、nginx 等基础服务
- 支持 terminal、browser、files、rag、docker、apis 等功能模块

### 第3层：AI 核心框架
- **AI 监控**：包含 langsmith、langfuse 等监控工具
- **AI Agent 框架**：包含 langgraph 和 langchain 生态系统
- **AI IDE**：包含 cursor 等 AI 辅助开发工具

### 第4层：大模型基座
- **qwen3**：通义千问大模型
- **DeepSeekR1**：深度求索大模型

## 数据流关系
1. AI Agent 在第1层的运行环境中执行
2. 通过调用第2层的 MCP 服务获取基础支持
3. 利用第3层的 AI 核心框架实现智能决策
4. 最终调用第4层的大模型基座生成结果

## 设计特点

- **分层架构**：清晰的四层结构，便于理解和维护
- **松耦合设计**：各层之间通过明确的接口交互
- **可扩展性**：每层都可以独立扩展新的功能模块
- **统一样式**：使用一致的 mermaid 样式规范，确保图表美观统一