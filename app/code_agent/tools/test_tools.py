import subprocess
from typing import Annotated
from pydantic import Field

from mcp.server.fastmcp import FastMCP
mcp = FastMCP()

@mcp.tool(name="run_command_once_tool", description="一次性执行命令并返回全部输出")
def run_command_once_tool(
        command: Annotated[str, Field(description="要执行的命令", example="ls -al")]
) -> str:
    """
    一次性执行命令并返回全部输出
    """
    return run_command_once(command)


def run_command_once(command):
    """
    执行命令并一次性返回所有输出
    """
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    output, _ = process.communicate()
    # 去除结尾多余换行
    output = output.rstrip('\n')
    return output


if __name__ == "__main__":
    mcp.run(transport="stdio")
    # print(run_command_once("ls -al"))
