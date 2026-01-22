import os
import shutil
from typing import Annotated, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP()

# 根目录设置
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.temp"))


def get_safe_path(path: str) -> str:
    """
    获取安全的文件路径，确保所有操作都在根目录下

    Args:
        path: 用户提供的文件路径

    Returns:
        str: 安全的绝对路径，确保在根目录下
    """
    # 转换为绝对路径
    if not os.path.isabs(path):
        safe_path = os.path.normpath(os.path.join(ROOT_DIR, path))
    else:
        # 如果是绝对路径，将其映射到根目录下
        safe_path = os.path.normpath(os.path.join(ROOT_DIR, os.path.basename(path)))

    # 确保路径在根目录下
    if not safe_path.startswith(ROOT_DIR):
        safe_path = ROOT_DIR

    return safe_path


@mcp.tool(name="save_file", description="保存文本内容到文件")
def save_file(
    file_path: Annotated[
        str, Field(description="文件路径", example="/path/to/file.txt")
    ],
    content: Annotated[str, Field(description="文件内容", example="Hello, World!")],
    encoding: Annotated[
        Optional[str], Field(description="文件编码", example="utf-8")
    ] = "utf-8",
) -> str:
    """
    保存文本内容到指定文件
    """
    try:
        # 获取安全路径
        safe_path = get_safe_path(file_path)

        # 确保目录存在
        dir_path = os.path.dirname(safe_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        # 写入文件
        with open(safe_path, "w", encoding=encoding) as f:
            f.write(content)

        return f"文件已成功保存到: {safe_path}"
    except Exception as e:
        return f"保存文件失败: {str(e)}"


@mcp.tool(name="append_file", description="追加文本内容到文件")
def append_file(
    file_path: Annotated[
        str, Field(description="文件路径", example="/path/to/file.txt")
    ],
    content: Annotated[
        str, Field(description="要追加的内容", example="Additional content")
    ],
    encoding: Annotated[
        Optional[str], Field(description="文件编码", example="utf-8")
    ] = "utf-8",
) -> str:
    """
    追加文本内容到指定文件
    """
    try:
        # 获取安全路径
        safe_path = get_safe_path(file_path)

        # 确保目录存在
        dir_path = os.path.dirname(safe_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        # 追加到文件
        with open(safe_path, "a", encoding=encoding) as f:
            f.write(content)

        return f"内容已成功追加到文件: {safe_path}"
    except Exception as e:
        return f"追加文件失败: {str(e)}"


@mcp.tool(name="create_directory", description="创建目录")
def create_directory(
    dir_path: Annotated[str, Field(description="目录路径", example="/path/to/dir")],
    exist_ok: Annotated[
        Optional[bool], Field(description="如果目录已存在是否忽略错误", example="True")
    ] = True,
) -> str:
    """
    创建指定目录
    """
    try:
        # 获取安全路径
        safe_path = get_safe_path(dir_path)

        os.makedirs(safe_path, exist_ok=exist_ok)
        return f"目录已成功创建: {safe_path}"
    except Exception as e:
        return f"创建目录失败: {str(e)}"


@mcp.tool(name="delete_file", description="删除文件")
def delete_file(
    file_path: Annotated[
        str, Field(description="文件路径", example="/path/to/file.txt")
    ],
) -> str:
    """
    删除指定文件
    """
    try:
        # 获取安全路径
        safe_path = get_safe_path(file_path)

        if os.path.exists(safe_path):
            os.remove(safe_path)
            return f"文件已成功删除: {safe_path}"
        else:
            return f"文件不存在: {safe_path}"
    except Exception as e:
        return f"删除文件失败: {str(e)}"


@mcp.tool(name="copy_file", description="复制文件")
def copy_file(
    src_path: Annotated[
        str, Field(description="源文件路径", example="/path/to/src.txt")
    ],
    dest_path: Annotated[
        str, Field(description="目标文件路径", example="/path/to/dest.txt")
    ],
    overwrite: Annotated[
        Optional[bool], Field(description="如果目标文件已存在是否覆盖", example="True")
    ] = True,
) -> str:
    """
    复制文件
    """
    try:
        # 获取安全路径
        safe_src_path = get_safe_path(src_path)
        safe_dest_path = get_safe_path(dest_path)

        if not os.path.exists(safe_src_path):
            return f"源文件不存在: {safe_src_path}"

        # 确保目标目录存在
        dest_dir = os.path.dirname(safe_dest_path)
        if dest_dir and not os.path.exists(dest_dir):
            os.makedirs(dest_dir, exist_ok=True)

        # 检查目标文件是否存在
        if os.path.exists(safe_dest_path) and not overwrite:
            return f"目标文件已存在: {safe_dest_path}"

        shutil.copy2(safe_src_path, safe_dest_path)
        return f"文件已成功复制: {safe_src_path} -> {safe_dest_path}"
    except Exception as e:
        return f"复制文件失败: {str(e)}"


@mcp.tool(name="move_file", description="移动文件")
def move_file(
    src_path: Annotated[
        str, Field(description="源文件路径", example="/path/to/src.txt")
    ],
    dest_path: Annotated[
        str, Field(description="目标文件路径", example="/path/to/dest.txt")
    ],
) -> str:
    """
    移动文件
    """
    try:
        # 获取安全路径
        safe_src_path = get_safe_path(src_path)
        safe_dest_path = get_safe_path(dest_path)

        if not os.path.exists(safe_src_path):
            return f"源文件不存在: {safe_src_path}"

        # 确保目标目录存在
        dest_dir = os.path.dirname(safe_dest_path)
        if dest_dir and not os.path.exists(dest_dir):
            os.makedirs(dest_dir, exist_ok=True)

        shutil.move(safe_src_path, safe_dest_path)
        return f"文件已成功移动: {safe_src_path} -> {safe_dest_path}"
    except Exception as e:
        return f"移动文件失败: {str(e)}"


@mcp.tool(name="get_file_content", description="获取文件内容")
def get_file_content(
    file_path: Annotated[
        str, Field(description="文件路径", example="/path/to/file.txt")
    ],
    encoding: Annotated[
        Optional[str], Field(description="文件编码", example="utf-8")
    ] = "utf-8",
) -> str:
    """
    获取指定文件的内容
    """
    try:
        # 获取安全路径
        safe_path = get_safe_path(file_path)

        if not os.path.exists(safe_path):
            return f"文件不存在: {safe_path}"

        with open(safe_path, "r", encoding=encoding) as f:
            content = f.read()

        return content
    except Exception as e:
        return f"读取文件失败: {str(e)}"


@mcp.tool(name="list_files", description="列出目录中的文件")
def list_files(
    dir_path: Annotated[str, Field(description="目录路径", example="/path/to/dir")],
    pattern: Annotated[
        Optional[str], Field(description="文件匹配模式", example="*.txt")
    ] = None,
) -> str:
    """
    列出目录中的文件
    """
    try:
        # 获取安全路径
        safe_path = get_safe_path(dir_path)

        if not os.path.exists(safe_path):
            return f"目录不存在: {safe_path}"

        if not os.path.isdir(safe_path):
            return f"指定路径不是目录: {safe_path}"

        files = os.listdir(safe_path)
        if pattern:
            import fnmatch

            files = fnmatch.filter(files, pattern)

        if not files:
            return f"目录 {safe_path} 中没有找到匹配的文件"

        result = f"目录 {safe_path} 中的文件:"
        for file in files:
            file_path = os.path.join(safe_path, file)
            if os.path.isfile(file_path):
                result += f"\n- {file}"

        return result
    except Exception as e:
        return f"列出文件失败: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
