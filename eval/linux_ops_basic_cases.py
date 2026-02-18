#!/usr/bin/env python3
"""
Linux/Shell 入门测试集 (30个案例)
用于筛选模型是否具备基础的系统运维工具调用能力

只有通过入门测试(>=40%)的模型，才进行深度测试(300案例)
"""

from typing import List, Dict

# 入门测试集 - 30个最基础的案例
LINUX_OPS_BASIC_CASES = [
    # ===== 文件目录操作 (6个) =====
    {
        "name": "列出文件",
        "category": "文件操作",
        "prompt": "列出当前目录的所有文件",
        "expected_tool": "execute_command",
        "expected_args": {"command": "ls", "args": "-la"},
        "description": "最基本的文件列表命令"
    },
    {
        "name": "查看路径",
        "category": "文件操作",
        "prompt": "显示当前所在的目录路径",
        "expected_tool": "execute_command",
        "expected_args": {"command": "pwd"},
        "description": "查看当前工作目录"
    },
    {
        "name": "创建目录",
        "category": "文件操作",
        "prompt": "创建一个名为test的新目录",
        "expected_tool": "execute_command",
        "expected_args": {"command": "mkdir", "args": "test"},
        "description": "创建新目录"
    },
    {
        "name": "复制文件",
        "category": "文件操作",
        "prompt": "将file1.txt复制为file2.txt",
        "expected_tool": "execute_command",
        "expected_args": {"command": "cp", "args": "file1.txt file2.txt"},
        "description": "复制文件"
    },
    {
        "name": "移动文件",
        "category": "文件操作",
        "prompt": "将data.txt移动到backup目录",
        "expected_tool": "execute_command",
        "expected_args": {"command": "mv", "args": "data.txt backup/"},
        "description": "移动文件到目录"
    },
    {
        "name": "删除文件",
        "category": "文件操作",
        "prompt": "删除temp.txt文件",
        "expected_tool": "execute_command",
        "expected_args": {"command": "rm", "args": "temp.txt"},
        "description": "删除文件"
    },

    # ===== 文本查看 (4个) =====
    {
        "name": "查看文件内容",
        "category": "文本处理",
        "prompt": "查看config.txt文件的内容",
        "expected_tool": "execute_command",
        "expected_args": {"command": "cat", "args": "config.txt"},
        "description": "查看文件内容"
    },
    {
        "name": "查看文件前10行",
        "category": "文本处理",
        "prompt": "查看log.txt文件的前10行",
        "expected_tool": "execute_command",
        "expected_args": {"command": "head", "args": "-10 log.txt"},
        "description": "查看文件开头"
    },
    {
        "name": "搜索文本",
        "category": "文本处理",
        "prompt": "在文件中搜索包含error的行",
        "expected_tool": "execute_command",
        "expected_args": {"command": "grep", "args": "error"},
        "description": "文本搜索"
    },
    {
        "name": "统计行数",
        "category": "文本处理",
        "prompt": "统计file.txt文件有多少行",
        "expected_tool": "execute_command",
        "expected_args": {"command": "wc", "args": "-l file.txt"},
        "description": "统计行数"
    },

    # ===== 系统信息 (4个) =====
    {
        "name": "查看磁盘空间",
        "category": "系统信息",
        "prompt": "查看磁盘使用情况",
        "expected_tool": "execute_command",
        "expected_args": {"command": "df", "args": "-h"},
        "description": "查看磁盘空间"
    },
    {
        "name": "查看内存",
        "category": "系统信息",
        "prompt": "查看系统内存使用情况",
        "expected_tool": "execute_command",
        "expected_args": {"command": "free", "args": "-h"},
        "description": "查看内存使用"
    },
    {
        "name": "查看当前用户",
        "category": "系统信息",
        "prompt": "显示当前登录的用户名",
        "expected_tool": "execute_command",
        "expected_args": {"command": "whoami"},
        "description": "查看当前用户"
    },
    {
        "name": "查看系统时间",
        "category": "系统信息",
        "prompt": "显示当前系统时间",
        "expected_tool": "execute_command",
        "expected_args": {"command": "date"},
        "description": "查看系统时间"
    },

    # ===== 进程管理 (4个) =====
    {
        "name": "查看进程",
        "category": "进程管理",
        "prompt": "查看当前运行的所有进程",
        "expected_tool": "execute_command",
        "expected_args": {"command": "ps", "args": "aux"},
        "description": "查看进程列表"
    },
    {
        "name": "结束进程",
        "category": "进程管理",
        "prompt": "结束PID为1234的进程",
        "expected_tool": "execute_command",
        "expected_args": {"command": "kill", "args": "1234"},
        "description": "终止进程"
    },
    {
        "name": "实时查看进程",
        "category": "进程管理",
        "prompt": "实时查看系统进程和资源占用",
        "expected_tool": "execute_command",
        "expected_args": {"command": "top"},
        "description": "动态查看进程"
    },
    {
        "name": "查找进程",
        "category": "进程管理",
        "prompt": "查找nginx进程的PID",
        "expected_tool": "execute_command",
        "expected_args": {"command": "pgrep", "args": "nginx"},
        "description": "查找进程ID"
    },

    # ===== 网络操作 (4个) =====
    {
        "name": "测试网络连通",
        "category": "网络管理",
        "prompt": "测试能否连接到baidu.com",
        "expected_tool": "execute_command",
        "expected_args": {"command": "ping", "args": "-c 4 baidu.com"},
        "description": "ping测试"
    },
    {
        "name": "下载文件",
        "category": "网络管理",
        "prompt": "下载http://example.com/file.txt文件",
        "expected_tool": "execute_command",
        "expected_args": {"command": "curl", "args": "-O http://example.com/file.txt"},
        "description": "下载文件"
    },
    {
        "name": "SSH登录",
        "category": "网络管理",
        "prompt": "使用ssh命令登录到192.168.1.100服务器",
        "expected_tool": "execute_command",
        "expected_args": {"command": "ssh", "args": "192.168.1.100"},
        "description": "SSH远程登录"
    },
    {
        "name": "查看网络连接",
        "category": "网络管理",
        "prompt": "查看当前的网络连接",
        "expected_tool": "execute_command",
        "expected_args": {"command": "netstat", "args": "-tuln"},
        "description": "查看网络连接"
    },

    # ===== Docker基础 (4个) =====
    {
        "name": "运行容器",
        "category": "容器操作",
        "prompt": "运行一个nginx容器",
        "expected_tool": "execute_command",
        "expected_args": {"command": "docker", "args": "run nginx"},
        "description": "运行Docker容器"
    },
    {
        "name": "查看容器",
        "category": "容器操作",
        "prompt": "列出正在运行的Docker容器",
        "expected_tool": "execute_command",
        "expected_args": {"command": "docker", "args": "ps"},
        "description": "查看运行容器"
    },
    {
        "name": "停止容器",
        "category": "容器操作",
        "prompt": "停止名为myapp的容器",
        "expected_tool": "execute_command",
        "expected_args": {"command": "docker", "args": "stop myapp"},
        "description": "停止容器"
    },
    {
        "name": "查看容器日志",
        "category": "容器操作",
        "prompt": "查看myapp容器的日志",
        "expected_tool": "execute_command",
        "expected_args": {"command": "docker", "args": "logs myapp"},
        "description": "查看容器日志"
    },

    # ===== Shell脚本 (4个) =====
    {
        "name": "创建脚本",
        "category": "Shell脚本",
        "prompt": "创建一个Shell脚本script.sh，输出Hello World",
        "expected_tool": "write_file",
        "expected_args": {"filename": "script.sh", "content": "#!/bin/bash\necho \"Hello World\""},
        "description": "创建Shell脚本"
    },
    {
        "name": "定义变量",
        "category": "Shell脚本",
        "prompt": "在Shell脚本script.sh中定义NAME变量并赋值为John",
        "expected_tool": "write_file",
        "expected_args": {"filename": "script.sh", "content": "NAME=\"John\""},
        "description": "定义变量"
    },
    {
        "name": "for循环",
        "category": "Shell脚本",
        "prompt": "写一个Shell脚本script.sh，包含遍历1到5的for循环",
        "expected_tool": "write_file",
        "expected_args": {"filename": "script.sh", "content": "for i in {1..5}; do echo \"$i\"; done"},
        "description": "for循环"
    },
    {
        "name": "if判断",
        "category": "Shell脚本",
        "prompt": "写一个Shell脚本script.sh，判断文件是否存在，存在则输出yes",
        "expected_tool": "write_file",
        "expected_args": {"filename": "script.sh", "content": "if [ -f file.txt ]; then echo \"yes\"; fi"},
        "description": "if条件判断"
    },
]


def get_basic_test_cases() -> List[Dict]:
    """获取入门测试案例"""
    return LINUX_OPS_BASIC_CASES.copy()


if __name__ == "__main__":
    cases = get_basic_test_cases()
    print(f"入门测试集: {len(cases)} 个案例")
    print("\n分类统计:")
    from collections import Counter
    categories = Counter(c["category"] for c in cases)
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}个")
