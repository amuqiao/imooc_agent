# Python代码格式化配置指南

## 项目结构树

```
imooc_agent/
├── .flake8                 # flake8 配置文件
├── .vscode/
│   └── settings.json       # VSCode 工作区配置
├── pyproject.toml          # black + isort 配置文件
└── tt.py                   # 示例测试文件
```

## 一、依赖安装

使用 uv 安装代码格式化所需依赖：

```bash
# 安装核心格式化工具
uv add black isort flake8 --dev

# 验证安装
uv pip list | grep -E "black|isort|flake8"
```

## 二、配置文件设置

### 1. pyproject.toml（black + isort 配置）

```toml
[tool.black]
line-length = 120          # 行长度限制
target-version = ['py311']  # 适配的Python版本（根据项目调整）
include = '\.pyi?$'        # 格式化的文件类型
exclude = '''              # 排除不需要格式化的目录/文件
/(
    \.git
  | \.venv
  | __pycache__
  | migrations
)/
'''

[tool.isort]
profile = "black"          # 对齐black的风格
line_length = 120
multi_line_output = 3      # 导入语句的换行风格
include_trailing_comma = true  # 导入列表末尾添加逗号
use_parentheses = true     # 导入语句使用圆括号包裹
```

### 2. .flake8（flake8 配置）

```ini
[flake8]
# 行长度限制
max-line-length = 120
# 忽略与black冲突的检查项
ignore = E203, W503, E501
# 排除检查的目录
exclude =
    .git,
    __pycache__,
    .venv,
    migrations
```

### 3. VSCode 工作区配置（.vscode/settings.json）

```json
{
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": [
        "--line-length", "120"
    ],
    "python.sortImports.args": [
        "--profile", "black",
        "--line-length", "120"
    ],
    "flake8.args": [
        "--max-line-length=120",
        "--ignore=E203,W503"
    ],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": "explicit"
    },
    "editor.rulers": [120],
    "files.trimTrailingWhitespace": true,
    "files.insertFinalNewline": true
}
```

## 三、验证配置生效

### 1. 手动验证

```bash
# 测试 black 格式化
uv run black tt.py

# 测试 isort 排序
uv run isort tt.py

# 测试 flake8 检查
uv run flake8 tt.py
```

### 2. VSCode 自动格式化验证

1. 在 VSCode 中打开 `tt.py` 文件
2. 写入不规范的代码：
   ```python
   import sys
   import os
def test():
    print("hello" , 123, 456)
   ```
3. 保存文件（`Cmd+S`/`Ctrl+S`）
4. 观察代码是否自动格式化为：
   ```python
   import os
   import sys

   def test():
       print("hello", 123, 456)
   ```

## 四、常见问题排查

### 1. black 报错 "Invalid value for '-t' / '--target-version'"

**原因**：`pyproject.toml` 中 `target-version` 设置错误
**解决**：使用正确的版本标识，如 `['py311']` 而非 `['py11']`

### 2. flake8 报错 "ValueError: invalid literal for int() with base 10"

**原因**：`.flake8` 文件中注释与配置值写在同一行
**解决**：注释单独占一行，如：
```ini
# 行长度限制
max-line-length = 120
```

### 3. VSCode 保存时不自动格式化

**解决步骤**：
1. 确保已安装 Python 扩展
2. 重启 VSCode
3. 检查 `.vscode/settings.json` 配置是否正确
4. 确认项目根目录存在 `pyproject.toml` 和 `.flake8` 文件

## 五、工具说明

- **black**：Python 代码格式化工具，强制统一代码风格
- **isort**：Python 导入语句排序工具，保持导入顺序一致
- **flake8**：Python 代码风格检查工具，基于 PEP8 规范
- **uv**：Python 包管理器，用于依赖安装和管理

## 六、最佳实践

1. 提交代码前先运行格式化命令
2. 团队协作时统一使用项目级配置文件
3. 定期更新依赖版本
4. 结合 CI/CD 流水线进行自动化格式检查

## 七、命令速查

```bash
# 安装依赖
uv add black isort flake8 --dev

# 格式化单个文件
uv run black <file.py>

# 格式化整个项目
uv run black .

# 排序导入语句
uv run isort <file.py>

# 排序整个项目导入
uv run isort .

# 代码风格检查
uv run flake8 <file.py>

# 检查整个项目
uv run flake8 .

# 一键格式化并检查
uv run black . && uv run isort . && uv run flake8 .
```
