#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基于MCP协议的文件工具服务
提供各种文件操作功能，通过stdio与Agent通信
"""

import os
import shutil
from typing import Annotated, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import Field

# 创建FastMCP实例
mcp = FastMCP()

# 根目录设置
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../.temp"))


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


@mcp.tool(name="read_file", description="读取文件内容")
def read_file(
    file_path: Annotated[
        str, Field(description="文件路径", example="/path/to/file.txt")
    ],
    encoding: Annotated[
        Optional[str], Field(description="文件编码", example="utf-8")
    ] = "utf-8",
) -> str:
    """
    读取指定文件的内容

    Args:
        file_path: 文件路径
        encoding: 文件编码

    Returns:
        str: 文件内容或错误信息
    """
    try:
        # 获取安全路径
        safe_path = get_safe_path(file_path)

        if not os.path.exists(safe_path):
            return f"错误：文件不存在 - {safe_path}"

        if not os.path.isfile(safe_path):
            return f"错误：指定路径不是文件 - {safe_path}"

        with open(safe_path, "r", encoding=encoding) as f:
            content = f.read()

        return content
    except Exception as e:
        return f"读取文件失败: {str(e)}"


@mcp.tool(name="write_file", description="写入内容到文件")
def write_file(
    file_path: Annotated[
        str, Field(description="文件路径", example="/path/to/file.txt")
    ],
    content: Annotated[str, Field(description="文件内容", example="Hello, World!")],
    encoding: Annotated[
        Optional[str], Field(description="文件编码", example="utf-8")
    ] = "utf-8",
    append: Annotated[bool, Field(description="是否追加模式", example="False")] = False,
) -> str:
    """
    写入内容到指定文件

    Args:
        file_path: 文件路径
        content: 文件内容
        encoding: 文件编码
        append: 是否追加模式

    Returns:
        str: 操作结果或错误信息
    """
    try:
        # 获取安全路径
        safe_path = get_safe_path(file_path)

        # 确保目录存在
        dir_path = os.path.dirname(safe_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        mode = "a" if append else "w"
        with open(safe_path, mode, encoding=encoding) as f:
            f.write(content)

        return f"文件已成功{'追加' if append else '写入'}到: {safe_path}"
    except Exception as e:
        return f"写入文件失败: {str(e)}"


@mcp.tool(name="list_directory", description="列出目录内容")
def list_directory(
    dir_path: Annotated[str, Field(description="目录路径", example="/path/to/dir")],
    pattern: Annotated[
        Optional[str], Field(description="文件匹配模式", example="*.txt")
    ] = None,
) -> str:
    """
    列出目录中的文件和子目录

    Args:
        dir_path: 目录路径
        pattern: 文件匹配模式

    Returns:
        str: 目录内容列表或错误信息
    """
    try:
        # 获取安全路径
        safe_path = get_safe_path(dir_path)

        if not os.path.exists(safe_path):
            return f"错误：目录不存在 - {safe_path}"

        if not os.path.isdir(safe_path):
            return f"错误：指定路径不是目录 - {safe_path}"

        # 获取目录内容
        entries = os.listdir(safe_path)

        # 应用匹配模式
        if pattern:
            import fnmatch

            entries = fnmatch.filter(entries, pattern)

        # 按文件和目录分组
        files = []
        dirs = []
        for entry in entries:
            entry_path = os.path.join(safe_path, entry)
            if os.path.isfile(entry_path):
                files.append(entry)
            elif os.path.isdir(entry_path):
                dirs.append(f"{entry}/")

        # 格式化输出
        result = f"目录 {safe_path} 包含 {len(files) + len(dirs)} 个条目:\n"
        if dirs:
            result += "\n子目录:\n"
            for d in sorted(dirs):
                result += f"  {d}\n"
        if files:
            result += "\n文件:\n"
            for f in sorted(files):
                result += f"  {f}\n"

        return result.strip()
    except Exception as e:
        return f"列出目录失败: {str(e)}"


@mcp.tool(name="create_directory", description="创建目录")
def create_directory(
    dir_path: Annotated[str, Field(description="目录路径", example="/path/to/new/dir")],
    exist_ok: Annotated[
        bool, Field(description="如果目录已存在是否忽略错误", example="True")
    ] = True,
) -> str:
    """
    创建指定目录

    Args:
        dir_path: 目录路径
        exist_ok: 如果目录已存在是否忽略错误

    Returns:
        str: 操作结果或错误信息
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

    Args:
        file_path: 文件路径

    Returns:
        str: 操作结果或错误信息
    """
    try:
        # 获取安全路径
        safe_path = get_safe_path(file_path)

        if not os.path.exists(safe_path):
            return f"错误：文件不存在 - {safe_path}"

        if not os.path.isfile(safe_path):
            return f"错误：指定路径不是文件 - {safe_path}"

        os.remove(safe_path)
        return f"文件已成功删除: {safe_path}"
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
        bool, Field(description="如果目标文件已存在是否覆盖", example="True")
    ] = True,
) -> str:
    """
    复制文件

    Args:
        src_path: 源文件路径
        dest_path: 目标文件路径
        overwrite: 如果目标文件已存在是否覆盖

    Returns:
        str: 操作结果或错误信息
    """
    try:
        # 获取安全路径
        safe_src_path = get_safe_path(src_path)
        safe_dest_path = get_safe_path(dest_path)

        if not os.path.exists(safe_src_path):
            return f"错误：源文件不存在 - {safe_src_path}"

        if not os.path.isfile(safe_src_path):
            return f"错误：源路径不是文件 - {safe_src_path}"

        if os.path.exists(safe_dest_path) and not overwrite:
            return f"错误：目标文件已存在 - {safe_dest_path}"

        # 确保目标目录存在
        dest_dir = os.path.dirname(safe_dest_path)
        if dest_dir and not os.path.exists(dest_dir):
            os.makedirs(dest_dir, exist_ok=True)

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

    Args:
        src_path: 源文件路径
        dest_path: 目标文件路径

    Returns:
        str: 操作结果或错误信息
    """
    try:
        # 获取安全路径
        safe_src_path = get_safe_path(src_path)
        safe_dest_path = get_safe_path(dest_path)

        if not os.path.exists(safe_src_path):
            return f"错误：源文件不存在 - {safe_src_path}"

        if not os.path.isfile(safe_src_path):
            return f"错误：源路径不是文件 - {safe_src_path}"

        # 确保目标目录存在
        dest_dir = os.path.dirname(safe_dest_path)
        if dest_dir and not os.path.exists(dest_dir):
            os.makedirs(dest_dir, exist_ok=True)

        shutil.move(safe_src_path, safe_dest_path)
        return f"文件已成功移动: {safe_src_path} -> {safe_dest_path}"
    except Exception as e:
        return f"移动文件失败: {str(e)}"


@mcp.tool(name="get_file_info", description="获取文件信息")
def get_file_info(
    file_path: Annotated[
        str, Field(description="文件路径", example="/path/to/file.txt")
    ],
) -> str:
    """
    获取文件信息

    Args:
        file_path: 文件路径

    Returns:
        str: 文件信息或错误信息
    """
    try:
        # 获取安全路径
        safe_path = get_safe_path(file_path)

        if not os.path.exists(safe_path):
            return f"错误：文件不存在 - {safe_path}"

        stat = os.stat(safe_path)
        is_file = os.path.isfile(safe_path)

        info = f"文件路径: {safe_path}\n"
        info += f"类型: {'文件' if is_file else '目录'}\n"
        info += f"大小: {stat.st_size} 字节\n"
        info += f"创建时间: {stat.st_ctime}\n"
        info += f"修改时间: {stat.st_mtime}\n"
        info += f"访问时间: {stat.st_atime}\n"
        info += f"权限: {oct(stat.st_mode)[-3:]}\n"

        return info.strip()
    except Exception as e:
        return f"获取文件信息失败: {str(e)}"


if __name__ == "__main__":
    """
    启动MCP文件工具服务
    使用stdio传输协议，与Agent通信
    """
    try:
        print("文件工具服务已启动，等待Agent连接...")
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        print("文件工具服务已停止")
    except Exception as e:
        print(f"文件工具服务启动失败: {str(e)}")
