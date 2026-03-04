#!/usr/bin/env python3
"""
Linux 操作、容器、Shell 测试案例集 (300个)
用于评估模型的系统运维和DevOps能力

⚠️ 安全警告 ⚠️
================
本文件只包含测试用例定义，用于评估模型是否能正确识别应该调用的工具和参数。

评估脚本 (eval_tools_capability.py) 只会:
1. 通过API发送prompt和工具定义给模型
2. 检查模型返回的tool_calls是否与预期匹配
3. 记录匹配结果

本脚本不会:
- 真的执行任何Linux命令
- 真的重启系统
- 真的删除文件
- 真的操作容器

但是，如果您使用其他自动化工具配合这些测试用例，请确保:
1. 不要在生产环境执行真实的命令
2. 使用沙箱/隔离环境运行实际命令
3. 仔细检查任何自动化执行逻辑

作者明确声明：这些测试用例仅用于模型能力评估，不对任何真实执行导致的损失负责。
"""

from typing import List, Dict

# ========== 基础Linux命令 (50个) ==========
BASE_LINUX_CASES = [
    # 文件和目录操作 (15个)
    {"name": "ls基础", "category": "文件目录", "prompt": "列出当前目录的文件", "expected_tool": "execute_command", "expected_args": {"command": "ls", "args": "-la"}},
    {"name": "pwd查看", "category": "文件目录", "prompt": "显示当前工作目录", "expected_tool": "execute_command", "expected_args": {"command": "pwd"}},
    {"name": "cd切换", "category": "文件目录", "prompt": "切换到/home目录", "expected_tool": "execute_command", "expected_args": {"command": "cd", "args": "/home"}},
    {"name": "mkdir创建", "category": "文件目录", "prompt": "创建test目录", "expected_tool": "execute_command", "expected_args": {"command": "mkdir", "args": "test"}},
    {"name": "rmdir删除", "category": "文件目录", "prompt": "删除空目录old", "expected_tool": "execute_command", "expected_args": {"command": "rmdir", "args": "old"}},
    {"name": "rm删除文件", "category": "文件目录", "prompt": "删除temp.txt文件", "expected_tool": "execute_command", "expected_args": {"command": "rm", "args": "temp.txt"}},
    {"name": "rm递归删除", "category": "文件目录", "prompt": "递归强制删除backup目录", "expected_tool": "execute_command", "expected_args": {"command": "rm", "args": "-rf backup"}},
    {"name": "cp复制文件", "category": "文件目录", "prompt": "复制file1.txt到file2.txt", "expected_tool": "execute_command", "expected_args": {"command": "cp", "args": "file1.txt file2.txt"}},
    {"name": "cp复制目录", "category": "文件目录", "prompt": "递归复制src目录到dst", "expected_tool": "execute_command", "expected_args": {"command": "cp", "args": "-r src dst"}},
    {"name": "mv移动", "category": "文件目录", "prompt": "移动data.csv到backup目录", "expected_tool": "execute_command", "expected_args": {"command": "mv", "args": "data.csv backup/"}},
    {"name": "mv重命名", "category": "文件目录", "prompt": "将old.txt重命名为new.txt", "expected_tool": "execute_command", "expected_args": {"command": "mv", "args": "old.txt new.txt"}},
    {"name": "touch创建", "category": "文件目录", "prompt": "创建空文件note.txt", "expected_tool": "execute_command", "expected_args": {"command": "touch", "args": "note.txt"}},
    {"name": "cat查看", "category": "文件目录", "prompt": "查看config.txt内容", "expected_tool": "execute_command", "expected_args": {"command": "cat", "args": "config.txt"}},
    {"name": "head查看", "category": "文件目录", "prompt": "查看log.txt前20行", "expected_tool": "execute_command", "expected_args": {"command": "head", "args": "-20 log.txt"}},
    {"name": "tail查看", "category": "文件目录", "prompt": "实时查看app.log日志", "expected_tool": "execute_command", "expected_args": {"command": "tail", "args": "-f app.log"}},

    # 文本处理 (15个)
    {"name": "grep搜索", "category": "文本处理", "prompt": "在文件中搜索error关键字", "expected_tool": "execute_command", "expected_args": {"command": "grep", "args": "error"}},
    {"name": "grep忽略大小写", "category": "文本处理", "prompt": "忽略大小写搜索Warning", "expected_tool": "execute_command", "expected_args": {"command": "grep", "args": "-i Warning"}},
    {"name": "grep递归", "category": "文本处理", "prompt": "递归搜索所有文件中的TODO", "expected_tool": "execute_command", "expected_args": {"command": "grep", "args": "-r TODO ."}},
    {"name": "grep反转", "category": "文本处理", "prompt": "显示不包含success的行", "expected_tool": "execute_command", "expected_args": {"command": "grep", "args": "-v success"}},
    {"name": "wc计数", "category": "文本处理", "prompt": "统计文件行数", "expected_tool": "execute_command", "expected_args": {"command": "wc", "args": "-l"}},
    {"name": "sort排序", "category": "文本处理", "prompt": "按字母排序文件内容", "expected_tool": "execute_command", "expected_args": {"command": "sort", "args": "data.txt"}},
    {"name": "sort逆序", "category": "文本处理", "prompt": "逆序排序并去重", "expected_tool": "execute_command", "expected_args": {"command": "sort", "args": "-ru"}},
    {"name": "uniq去重", "category": "文本处理", "prompt": "统计重复行出现次数", "expected_tool": "execute_command", "expected_args": {"command": "uniq", "args": "-c"}},
    {"name": "sed替换", "category": "文本处理", "prompt": "将文件中的foo替换为bar", "expected_tool": "execute_command", "expected_args": {"command": "sed", "args": "'s/foo/bar/g'"}},
    {"name": "sed删除", "category": "文本处理", "prompt": "删除文件中的空行", "expected_tool": "execute_command", "expected_args": {"command": "sed", "args": "'/^$/d'"}},
    {"name": "awk处理", "category": "文本处理", "prompt": "打印文件的第2列", "expected_tool": "execute_command", "expected_args": {"command": "awk", "args": "'{print $2}'"}},
    {"name": "awk条件", "category": "文本处理", "prompt": "打印大于100的行", "expected_tool": "execute_command", "expected_args": {"command": "awk", "args": "'$1 > 100'"}},
    {"name": "cut截取", "category": "文本处理", "prompt": "提取每行的前5个字符", "expected_tool": "execute_command", "expected_args": {"command": "cut", "args": "-c1-5"}},
    {"name": "cut字段", "category": "文本处理", "prompt": "按冒号分割取第1,3字段", "expected_tool": "execute_command", "expected_args": {"command": "cut", "args": "-d: -f1,3"}},
    {"name": "tr转换", "category": "文本处理", "prompt": "将小写转换为大写", "expected_tool": "execute_command", "expected_args": {"command": "tr", "args": "'a-z' 'A-Z'"}},

    # 系统信息 (10个)
    {"name": "uname系统", "category": "系统信息", "prompt": "显示系统内核信息", "expected_tool": "execute_command", "expected_args": {"command": "uname", "args": "-a"}},
    {"name": "df磁盘", "category": "系统信息", "prompt": "查看磁盘使用情况", "expected_tool": "execute_command", "expected_args": {"command": "df", "args": "-h"}},
    {"name": "du目录", "category": "系统信息", "prompt": "查看当前目录总大小", "expected_tool": "execute_command", "expected_args": {"command": "du", "args": "-sh ."}},
    {"name": "du详细", "category": "系统信息", "prompt": "显示各子目录大小并排序", "expected_tool": "execute_command", "expected_args": {"command": "du", "args": "-sh * | sort -h"}},
    {"name": "free内存", "category": "系统信息", "prompt": "查看内存使用情况", "expected_tool": "execute_command", "expected_args": {"command": "free", "args": "-h"}},
    {"name": "uptime负载", "category": "系统信息", "prompt": "查看系统运行时间和负载", "expected_tool": "execute_command", "expected_args": {"command": "uptime"}},
    {"name": "who用户", "category": "系统信息", "prompt": "查看当前登录用户", "expected_tool": "execute_command", "expected_args": {"command": "who"}},
    {"name": "whoami当前", "category": "系统信息", "prompt": "显示当前用户名", "expected_tool": "execute_command", "expected_args": {"command": "whoami"}},
    {"name": "date时间", "category": "系统信息", "prompt": "显示当前日期时间", "expected_tool": "execute_command", "expected_args": {"command": "date"}},
    {"name": "hostname主机", "category": "系统信息", "prompt": "显示主机名", "expected_tool": "execute_command", "expected_args": {"command": "hostname"}},

    # 权限管理 (10个)
    {"name": "chmod权限", "category": "权限管理", "prompt": "给script.sh添加执行权限", "expected_tool": "execute_command", "expected_args": {"command": "chmod", "args": "+x script.sh"}},
    {"name": "chmod数字", "category": "权限管理", "prompt": "设置文件权限为755", "expected_tool": "execute_command", "expected_args": {"command": "chmod", "args": "755 file"}},
    {"name": "chown属主", "category": "权限管理", "prompt": "将文件改为root用户所有", "expected_tool": "execute_command", "expected_args": {"command": "chown", "args": "root file"}},
    {"name": "chown递归", "category": "权限管理", "prompt": "递归更改目录属主和属组", "expected_tool": "execute_command", "expected_args": {"command": "chown", "args": "-R user:group dir"}},
    {"name": "ls权限", "category": "权限管理", "prompt": "显示文件详细权限信息", "expected_tool": "execute_command", "expected_args": {"command": "ls", "args": "-la"}},
    {"name": "umask掩码", "category": "权限管理", "prompt": "查看当前umask值", "expected_tool": "execute_command", "expected_args": {"command": "umask"}},
    {"name": "sudo执行", "category": "权限管理", "prompt": "以root权限执行apt update", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "apt update"}},
    {"name": "sudo编辑", "category": "权限管理", "prompt": "用sudo编辑系统配置文件", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "vi /etc/hosts"}},
    {"name": "su切换", "category": "权限管理", "prompt": "切换到root用户", "expected_tool": "execute_command", "expected_args": {"command": "su", "args": "-"}},
    {"name": "passwd密码", "category": "权限管理", "prompt": "修改当前用户密码", "expected_tool": "execute_command", "expected_args": {"command": "passwd"}},
]


# ========== 进程和网络管理 (50个) ==========
PROCESS_NETWORK_CASES = [
    # 进程管理 (25个)
    {"name": "ps查看", "category": "进程管理", "prompt": "查看当前运行的进程", "expected_tool": "execute_command", "expected_args": {"command": "ps", "args": "aux"}},
    {"name": "ps用户", "category": "进程管理", "prompt": "查看特定用户的进程", "expected_tool": "execute_command", "expected_args": {"command": "ps", "args": "-u username"}},
    {"name": "top动态", "category": "进程管理", "prompt": "实时查看系统进程和资源使用", "expected_tool": "execute_command", "expected_args": {"command": "top"}},
    {"name": "htop增强", "category": "进程管理", "prompt": "使用htop查看进程", "expected_tool": "execute_command", "expected_args": {"command": "htop"}},
    {"name": "pgrep查找", "category": "进程管理", "prompt": "查找nginx进程的PID", "expected_tool": "execute_command", "expected_args": {"command": "pgrep", "args": "nginx"}},
    {"name": "pkill结束", "category": "进程管理", "prompt": "强制结束所有python进程", "expected_tool": "execute_command", "expected_args": {"command": "pkill", "args": "-9 python"}},
    {"name": "kill终止", "category": "进程管理", "prompt": "结束PID为1234的进程", "expected_tool": "execute_command", "expected_args": {"command": "kill", "args": "1234"}},
    {"name": "kill强制", "category": "进程管理", "prompt": "强制结束进程", "expected_tool": "execute_command", "expected_args": {"command": "kill", "args": "-9 1234"}},
    {"name": "killall名称", "category": "进程管理", "prompt": "结束所有名为firefox的进程", "expected_tool": "execute_command", "expected_args": {"command": "killall", "args": "firefox"}},
    {"name": "nice优先级", "category": "进程管理", "prompt": "以低优先级运行备份脚本", "expected_tool": "execute_command", "expected_args": {"command": "nice", "args": "-n 19 backup.sh"}},
    {"name": "renice调整", "category": "进程管理", "prompt": "调整进程1234的优先级为10", "expected_tool": "execute_command", "expected_args": {"command": "renice", "args": "10 -p 1234"}},
    {"name": "nohup后台", "category": "进程管理", "prompt": "在后台运行长时间任务", "expected_tool": "execute_command", "expected_args": {"command": "nohup", "args": "long_task.sh &"}},
    {"name": "bg后台", "category": "进程管理", "prompt": "将暂停的作业放到后台", "expected_tool": "execute_command", "expected_args": {"command": "bg"}},
    {"name": "fg前台", "category": "进程管理", "prompt": "将后台作业切换到前台", "expected_tool": "execute_command", "expected_args": {"command": "fg"}},
    {"name": "jobs列表", "category": "进程管理", "prompt": "查看当前shell的后台作业", "expected_tool": "execute_command", "expected_args": {"command": "jobs"}},
    {"name": "wait等待", "category": "进程管理", "prompt": "等待所有后台作业完成", "expected_tool": "execute_command", "expected_args": {"command": "wait"}},
    {"name": "disown脱离", "category": "进程管理", "prompt": "使作业不受shell退出影响", "expected_tool": "execute_command", "expected_args": {"command": "disown"}},
    {"name": "trap信号", "category": "进程管理", "prompt": "捕获SIGINT信号", "expected_tool": "execute_command", "expected_args": {"command": "trap", "args": "'echo caught' INT"}},
    {"name": "sleep暂停", "category": "进程管理", "prompt": "暂停5秒", "expected_tool": "execute_command", "expected_args": {"command": "sleep", "args": "5"}},
    {"name": "timeout超时", "category": "进程管理", "prompt": "10秒后自动终止命令", "expected_tool": "execute_command", "expected_args": {"command": "timeout", "args": "10 command"}},
    {"name": "watch监控", "category": "进程管理", "prompt": "每2秒刷新显示负载", "expected_tool": "execute_command", "expected_args": {"command": "watch", "args": "-n 2 uptime"}},
    {"name": "cron定时", "category": "进程管理", "prompt": "编辑当前用户的crontab", "expected_tool": "execute_command", "expected_args": {"command": "crontab", "args": "-e"}},
    {"name": "crontab列表", "category": "进程管理", "prompt": "列出当前定时任务", "expected_tool": "execute_command", "expected_args": {"command": "crontab", "args": "-l"}},
    {"name": "at单次", "category": "进程管理", "prompt": "在下午3点执行脚本", "expected_tool": "execute_command", "expected_args": {"command": "at", "args": "15:00"}},
    {"name": "atq队列", "category": "进程管理", "prompt": "查看待执行的at任务", "expected_tool": "execute_command", "expected_args": {"command": "atq"}},

    # 网络管理 (25个)
    {"name": "ifconfig接口", "category": "网络管理", "prompt": "查看所有网络接口", "expected_tool": "execute_command", "expected_args": {"command": "ifconfig", "args": "-a"}},
    {"name": "ip地址", "category": "网络管理", "prompt": "显示IP地址信息", "expected_tool": "execute_command", "expected_args": {"command": "ip", "args": "addr"}},
    {"name": "ip路由", "category": "网络管理", "prompt": "查看路由表", "expected_tool": "execute_command", "expected_args": {"command": "ip", "args": "route"}},
    {"name": "ping测试", "category": "网络管理", "prompt": "测试到baidu.com的连通性", "expected_tool": "execute_command", "expected_args": {"command": "ping", "args": "-c 4 baidu.com"}},
    {"name": "traceroute追踪", "category": "网络管理", "prompt": "追踪到google.com的路由", "expected_tool": "execute_command", "expected_args": {"command": "traceroute", "args": "google.com"}},
    {"name": "netstat连接", "category": "网络管理", "prompt": "查看所有网络连接", "expected_tool": "execute_command", "expected_args": {"command": "netstat", "args": "-tuln"}},
    {"name": "ss套接字", "category": "网络管理", "prompt": "查看监听端口", "expected_tool": "execute_command", "expected_args": {"command": "ss", "args": "-tlnp"}},
    {"name": "curl请求", "category": "网络管理", "prompt": "获取网页内容", "expected_tool": "execute_command", "expected_args": {"command": "curl", "args": "http://example.com"}},
    {"name": "curl下载", "category": "网络管理", "prompt": "下载文件", "expected_tool": "execute_command", "expected_args": {"command": "curl", "args": "-O http://example.com/file.zip"}},
    {"name": "wget下载", "category": "网络管理", "prompt": "递归下载网站", "expected_tool": "execute_command", "expected_args": {"command": "wget", "args": "-r http://example.com"}},
    {"name": "wget后台", "category": "网络管理", "prompt": "后台下载大文件", "expected_tool": "execute_command", "expected_args": {"command": "wget", "args": "-b http://example.com/large.zip"}},
    {"name": "scp复制", "category": "网络管理", "prompt": "复制文件到远程服务器", "expected_tool": "execute_command", "expected_args": {"command": "scp", "args": "file.txt user@host:/path"}},
    {"name": "scp递归", "category": "网络管理", "prompt": "递归复制目录到远程", "expected_tool": "execute_command", "expected_args": {"command": "scp", "args": "-r dir/ user@host:/backup/"}},
    {"name": "ssh登录", "category": "网络管理", "prompt": "SSH登录到远程服务器", "expected_tool": "execute_command", "expected_args": {"command": "ssh", "args": "user@192.168.1.100"}},
    {"name": "ssh执行", "category": "网络管理", "prompt": "在远程执行命令", "expected_tool": "execute_command", "expected_args": {"command": "ssh", "args": "user@host 'ls -la'"}},
    {"name": "ssh端口", "category": "网络管理", "prompt": "指定端口SSH连接", "expected_tool": "execute_command", "expected_args": {"command": "ssh", "args": "-p 2222 user@host"}},
    {"name": "ssh密钥", "category": "网络管理", "prompt": "使用密钥登录", "expected_tool": "execute_command", "expected_args": {"command": "ssh", "args": "-i ~/.ssh/id_rsa user@host"}},
    {"name": "nc测试", "category": "网络管理", "prompt": "测试端口连通性", "expected_tool": "execute_command", "expected_args": {"command": "nc", "args": "-zv host 80"}},
    {"name": "nc监听", "category": "网络管理", "prompt": "在端口8080监听", "expected_tool": "execute_command", "expected_args": {"command": "nc", "args": "-l 8080"}},
    {"name": "telnet连接", "category": "网络管理", "prompt": "测试SMTP端口", "expected_tool": "execute_command", "expected_args": {"command": "telnet", "args": "smtp.example.com 25"}},
    {"name": "host解析", "category": "网络管理", "prompt": "查询域名IP", "expected_tool": "execute_command", "expected_args": {"command": "host", "args": "google.com"}},
    {"name": "dig详细", "category": "网络管理", "prompt": "查询DNS详细记录", "expected_tool": "execute_command", "expected_args": {"command": "dig", "args": "example.com"}},
    {"name": "nslookup", "category": "网络管理", "prompt": "查询域名服务器", "expected_tool": "execute_command", "expected_args": {"command": "nslookup", "args": "example.com"}},
    {"name": "arp表", "category": "网络管理", "prompt": "查看ARP缓存表", "expected_tool": "execute_command", "expected_args": {"command": "arp", "args": "-a"}},
    {"name": "iptables规则", "category": "网络管理", "prompt": "查看防火墙规则", "expected_tool": "execute_command", "expected_args": {"command": "iptables", "args": "-L"}},
]


# ========== 容器操作 (60个) ==========
CONTAINER_CASES = [
    # Docker基础 (30个)
    {"name": "docker运行", "category": "Docker基础", "prompt": "运行nginx容器", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "run nginx"}},
    {"name": "docker后台", "category": "Docker基础", "prompt": "后台运行ubuntu容器", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "run -d ubuntu"}},
    {"name": "docker交互", "category": "Docker基础", "prompt": "交互式运行并进入容器", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "run -it ubuntu bash"}},
    {"name": "docker端口", "category": "Docker基础", "prompt": "映射端口80到主机的8080", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "run -p 8080:80 nginx"}},
    {"name": "docker卷", "category": "Docker基础", "prompt": "挂载主机目录到容器", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "run -v /host:/container nginx"}},
    {"name": "docker名称", "category": "Docker基础", "prompt": "运行并指定容器名", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "run --name mynginx nginx"}},
    {"name": "docker环境", "category": "Docker基础", "prompt": "运行并设置环境变量", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "run -e MYSQL_ROOT_PASSWORD=secret mysql"}},
    {"name": "docker自动重启", "category": "Docker基础", "prompt": "运行并设置自动重启", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "run --restart always nginx"}},
    {"name": "docker资源", "category": "Docker基础", "prompt": "限制容器内存为512MB", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "run -m 512m ubuntu"}},
    {"name": "dockerCPU", "category": "Docker基础", "prompt": "限制容器使用1个CPU", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "run --cpus=1 ubuntu"}},
    {"name": "docker列表", "category": "Docker基础", "prompt": "列出运行中的容器", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "ps"}},
    {"name": "docker全部", "category": "Docker基础", "prompt": "列出所有容器包括停止的", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "ps -a"}},
    {"name": "docker停止", "category": "Docker基础", "prompt": "停止容器myapp", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "stop myapp"}},
    {"name": "docker启动", "category": "Docker基础", "prompt": "启动已停止的容器", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "start myapp"}},
    {"name": "docker重启", "category": "Docker基础", "prompt": "重启容器", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "restart myapp"}},
    {"name": "docker删除", "category": "Docker基础", "prompt": "删除容器", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "rm myapp"}},
    {"name": "docker强制删", "category": "Docker基础", "prompt": "强制删除运行中的容器", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "rm -f myapp"}},
    {"name": "docker进入", "category": "Docker基础", "prompt": "进入运行中的容器", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "exec -it myapp bash"}},
    {"name": "docker执行", "category": "Docker基础", "prompt": "在容器中执行命令", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "exec myapp ls -la"}},
    {"name": "docker日志", "category": "Docker基础", "prompt": "查看容器日志", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "logs myapp"}},
    {"name": "docker日志跟随", "category": "Docker基础", "prompt": "实时查看容器日志", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "logs -f myapp"}},
    {"name": "docker信息", "category": "Docker基础", "prompt": "查看容器详细信息", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "inspect myapp"}},
    {"name": "docker状态", "category": "Docker基础", "prompt": "查看容器资源使用", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "stats myapp"}},
    {"name": "docker复制进", "category": "Docker基础", "prompt": "复制文件到容器", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "cp file.txt myapp:/tmp/"}},
    {"name": "docker复制出", "category": "Docker基础", "prompt": "从容器复制文件出来", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "cp myapp:/var/log/log.txt ./"}},
    {"name": "docker镜像列", "category": "Docker基础", "prompt": "列出本地镜像", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "images"}},
    {"name": "docker镜像删", "category": "Docker基础", "prompt": "删除镜像", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "rmi nginx:latest"}},
    {"name": "docker拉取", "category": "Docker基础", "prompt": "拉取最新镜像", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "pull ubuntu:22.04"}},
    {"name": "docker构建", "category": "Docker基础", "prompt": "构建Docker镜像", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "build -t myapp ."}},
    {"name": "docker标签", "category": "Docker基础", "prompt": "给镜像打标签", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "tag myapp:latest myapp:v1.0"}},

    # Docker高级 (15个)
    {"name": "docker网络", "category": "Docker高级", "prompt": "列出Docker网络", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "network ls"}},
    {"name": "docker网络创", "category": "Docker高级", "prompt": "创建桥接网络", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "network create mynet"}},
    {"name": "docker连接", "category": "Docker高级", "prompt": "连接容器到网络", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "network connect mynet myapp"}},
    {"name": "docker卷列", "category": "Docker高级", "prompt": "列出数据卷", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "volume ls"}},
    {"name": "docker卷创", "category": "Docker高级", "prompt": "创建命名卷", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "volume create mydata"}},
    {"name": "docker清理", "category": "Docker高级", "prompt": "清理未使用的资源", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "system prune"}},
    {"name": "docker组合", "category": "Docker高级", "prompt": "启动docker-compose所有服务", "expected_tool": "execute_command", "expected_args": {"command": "docker-compose", "args": "up -d"}},
    {"name": "docker组合停", "category": "Docker高级", "prompt": "停止docker-compose服务", "expected_tool": "execute_command", "expected_args": {"command": "docker-compose", "args": "down"}},
    {"name": "docker组合日", "category": "Docker高级", "prompt": "查看docker-compose日志", "expected_tool": "execute_command", "expected_args": {"command": "docker-compose", "args": "logs -f"}},
    {"name": "docker导出", "category": "Docker高级", "prompt": "导出容器为tar", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "export -o myapp.tar myapp"}},
    {"name": "docker导入", "category": "Docker高级", "prompt": "从tar导入镜像", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "import myapp.tar"}},
    {"name": "docker保存", "category": "Docker高级", "prompt": "保存镜像到tar", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "save -o myapp.tar myapp:latest"}},
    {"name": "docker加载", "category": "Docker高级", "prompt": "从tar加载镜像", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "load -i myapp.tar"}},
    {"name": "docker推送", "category": "Docker高级", "prompt": "推送镜像到仓库", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "push myregistry/myapp:latest"}},
    {"name": "docker历史", "category": "Docker高级", "prompt": "查看镜像构建历史", "expected_tool": "execute_command", "expected_args": {"command": "docker", "args": "history myapp"}},

    # Podman (15个)
    {"name": "podman运行", "category": "Podman", "prompt": "用podman运行容器", "expected_tool": "execute_command", "expected_args": {"command": "podman", "args": "run nginx"}},
    {"name": "podman后台", "category": "Podman", "prompt": "podman后台运行", "expected_tool": "execute_command", "expected_args": {"command": "podman", "args": "run -d ubuntu"}},
    {"name": "podman列表", "category": "Podman", "prompt": "列出podman容器", "expected_tool": "execute_command", "expected_args": {"command": "podman", "args": "ps"}},
    {"name": "podman全部", "category": "Podman", "prompt": "列出所有podman容器", "expected_tool": "execute_command", "expected_args": {"command": "podman", "args": "ps -a"}},
    {"name": "podman停止", "category": "Podman", "prompt": "停止podman容器", "expected_tool": "execute_command", "expected_args": {"command": "podman", "args": "stop myapp"}},
    {"name": "podman删除", "category": "Podman", "prompt": "删除podman容器", "expected_tool": "execute_command", "expected_args": {"command": "podman", "args": "rm myapp"}},
    {"name": "podman镜像", "category": "Podman", "prompt": "列出podman镜像", "expected_tool": "execute_command", "expected_args": {"command": "podman", "args": "images"}},
    {"name": "podman拉取", "category": "Podman", "prompt": "podman拉取镜像", "expected_tool": "execute_command", "expected_args": {"command": "podman", "args": "pull ubuntu"}},
    {"name": "podman构建", "category": "Podman", "prompt": "podman构建镜像", "expected_tool": "execute_command", "expected_args": {"command": "podman", "args": "build -t myapp ."}},
    {"name": "podman进入", "category": "Podman", "prompt": "进入podman容器", "expected_tool": "execute_command", "expected_args": {"command": "podman", "args": "exec -it myapp bash"}},
    {"name": "podman日志", "category": "Podman", "prompt": "查看podman日志", "expected_tool": "execute_command", "expected_args": {"command": "podman", "args": "logs myapp"}},
    {"name": "podman生成", "category": "Podman", "prompt": "生成systemd服务文件", "expected_tool": "execute_command", "expected_args": {"command": "podman", "args": "generate systemd myapp"}},
    {"name": "podman无根", "category": "Podman", "prompt": "以非root运行容器", "expected_tool": "execute_command", "expected_args": {"command": "podman", "args": "run --user 1000 ubuntu"}},
    {"name": "podmanPod", "category": "Podman", "prompt": "创建pod", "expected_tool": "execute_command", "expected_args": {"command": "podman", "args": "pod create mypod"}},
    {"name": "podmanPod列表", "category": "Podman", "prompt": "列出pods", "expected_tool": "execute_command", "expected_args": {"command": "podman", "args": "pod list"}},
]


# ========== Shell脚本编程 (60个) ==========
SHELL_SCRIPT_CASES = [
    # 基础语法 (20个)
    {"name": "shebang", "category": "Shell基础", "prompt": "写shebang指定bash解释器", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "#!/bin/bash"}},
    {"name": "变量定义", "category": "Shell基础", "prompt": "定义NAME变量值为John", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "NAME=\"John\""}},
    {"name": "变量引用", "category": "Shell基础", "prompt": "输出变量NAME的值", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "echo \"$NAME\""}},
    {"name": "只读变量", "category": "Shell基础", "prompt": "定义只读变量PI", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "readonly PI=3.14159"}},
    {"name": "删除变量", "category": "Shell基础", "prompt": "删除变量TEMP", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "unset TEMP"}},
    {"name": "位置参数", "category": "Shell基础", "prompt": "输出第一个参数", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "echo \"$1\""}},
    {"name": "参数个数", "category": "Shell基础", "prompt": "输出参数个数", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "echo \"$#\""}},
    {"name": "所有参数", "category": "Shell基础", "prompt": "输出所有参数", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "echo \"$@\""}},
    {"name": "脚本名", "category": "Shell基础", "prompt": "输出脚本名称", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "echo \"$0\""}},
    {"name": "退出码", "category": "Shell基础", "prompt": "设置退出码为1", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "exit 1"}},
    {"name": "上一个命令", "category": "Shell基础", "prompt": "输出上一个命令退出码", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "echo \"$?\""}},
    {"name": "进程ID", "category": "Shell基础", "prompt": "输出当前进程ID", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "echo \"$$\""}},
    {"name": "后台进程", "category": "Shell基础", "prompt": "输出最后一个后台进程ID", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "echo \"$!\""}},
    {"name": "字符串长度", "category": "Shell基础", "prompt": "计算字符串长度", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "echo \"${#STR}\""}},
    {"name": "字符串截取", "category": "Shell基础", "prompt": "截取字符串前5个字符", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "echo \"${STR:0:5}\""}},
    {"name": "默认值", "category": "Shell基础", "prompt": "变量为空时使用默认值", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "echo \"${NAME:-default}\""}},
    {"name": "赋值默认值", "category": "Shell基础", "prompt": "变量为空时赋值默认值", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "echo \"${NAME:=default}\""}},
    {"name": "数组定义", "category": "Shell基础", "prompt": "定义数组", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "ARR=(a b c)"}},
    {"name": "数组元素", "category": "Shell基础", "prompt": "取数组第一个元素", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "echo \"${ARR[0]}\""}},
    {"name": "数组全部", "category": "Shell基础", "prompt": "取数组所有元素", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "echo \"${ARR[@]}\""}},

    # 流程控制 (20个)
    {"name": "if判断", "category": "流程控制", "prompt": "判断文件是否存在", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "if [ -f file.txt ]; then echo \"exists\"; fi"}},
    {"name": "if_else", "category": "流程控制", "prompt": "条件判断加else", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "if [ -f file ]; then echo yes; else echo no; fi"}},
    {"name": "if_elif", "category": "流程控制", "prompt": "多条件判断", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "if [ $A -gt 10 ]; then echo big; elif [ $A -gt 5 ]; then echo mid; else echo small; fi"}},
    {"name": "数值比较", "category": "流程控制", "prompt": "比较两个数字相等", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "if [ \"$A\" -eq \"$B\" ]; then echo equal; fi"}},
    {"name": "字符串相等", "category": "流程控制", "prompt": "比较字符串相等", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "if [ \"$A\" = \"$B\" ]; then echo equal; fi"}},
    {"name": "非空判断", "category": "流程控制", "prompt": "判断字符串非空", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "if [ -n \"$STR\" ]; then echo not empty; fi"}},
    {"name": "与条件", "category": "流程控制", "prompt": "多个条件同时满足", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "if [ -f file ] && [ -r file ]; then echo ok; fi"}},
    {"name": "或条件", "category": "流程控制", "prompt": "任一条件满足", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "if [ -f file ] || [ -d dir ]; then echo ok; fi"}},
    {"name": "for循环", "category": "流程控制", "prompt": "遍历文件列表", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "for f in *.txt; do echo \"$f\"; done"}},
    {"name": "for范围", "category": "流程控制", "prompt": "1到10循环", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "for i in {1..10}; do echo \"$i\"; done"}},
    {"name": "while循环", "category": "流程控制", "prompt": "while循环计数", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "while [ \"$i\" -lt 10 ]; do echo \"$i\"; i=$((i+1)); done"}},
    {"name": "until循环", "category": "流程控制", "prompt": "until循环直到条件满足", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "until [ \"$i\" -ge 10 ]; do echo \"$i\"; i=$((i+1)); done"}},
    {"name": "break跳出", "category": "流程控制", "prompt": "循环中break", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "for i in {1..10}; do if [ \"$i\" -eq 5 ]; then break; fi; done"}},
    {"name": "continue继续", "category": "流程控制", "prompt": "循环中continue", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "for i in {1..10}; do if [ \"$i\" -eq 5 ]; then continue; fi; done"}},
    {"name": "case分支", "category": "流程控制", "prompt": "case多分支", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "case \"$1\" in start) echo start;; stop) echo stop;; esac"}},
    {"name": "函数定义", "category": "流程控制", "prompt": "定义函数", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "myfunc() { echo \"hello\"; }"}},
    {"name": "函数调用", "category": "流程控制", "prompt": "调用函数", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "myfunc"}},
    {"name": "函数传参", "category": "流程控制", "prompt": "函数接收参数", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "myfunc() { echo \"$1\"; }; myfunc arg1"}},
    {"name": "函数返回", "category": "流程控制", "prompt": "函数返回值", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "myfunc() { return 0; }"}},
    {"name": "local局部", "category": "流程控制", "prompt": "函数内局部变量", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "myfunc() { local var=1; }"}},

    # 高级特性 (20个)
    {"name": "重定向输出", "category": "Shell高级", "prompt": "命令输出重定向到文件", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "command > output.txt"}},
    {"name": "重定向追加", "category": "Shell高级", "prompt": "追加输出到文件", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "echo \"log\" >> log.txt"}},
    {"name": "重定向错误", "category": "Shell高级", "prompt": "重定向错误输出", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "command 2> error.log"}},
    {"name": "重定向合并", "category": "Shell高级", "prompt": "合并stdout和stderr", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "command > all.log 2>&1"}},
    {"name": "输入重定向", "category": "Shell高级", "prompt": "从文件输入", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "command < input.txt"}},
    {"name": "管道", "category": "Shell高级", "prompt": "管道传递", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "cat file | grep pattern"}},
    {"name": "命令替换", "category": "Shell高级", "prompt": "获取命令输出", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "DATE=$(date)"}},
    {"name": "算术扩展", "category": "Shell高级", "prompt": "算术运算", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "RESULT=$((1+2))"}},
    {"name": "子shell", "category": "Shell高级", "prompt": "在子shell执行", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "(cd /tmp; ls)"}},
    {"name": "后台执行", "category": "Shell高级", "prompt": "后台运行命令", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "long_running_command &"}},
    {"name": "here文档", "category": "Shell高级", "prompt": "here document", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "cat << EOF\nline1\nline2\nEOF"}},
    {"name": "here字符串", "category": "Shell高级", "prompt": "here string", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "cat <<< \"hello world\""}},
    {"name": "source执行", "category": "Shell高级", "prompt": "source执行脚本", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "source ./config.sh"}},
    {"name": "点执行", "category": "Shell高级", "prompt": "点命令执行脚本", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": ". ./config.sh"}},
    {"name": "exec替换", "category": "Shell高级", "prompt": "exec替换进程", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "exec /bin/bash"}},
    {"name": "eval执行", "category": "Shell高级", "prompt": "eval执行字符串", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "eval \"echo hello\""}},
    {"name": "shift移位", "category": "Shell高级", "prompt": "shift参数左移", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "shift 2"}},
    {"name": "getopts选项", "category": "Shell高级", "prompt": "解析命令行选项", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "while getopts \"a:b\" opt; do case \\$opt in a) echo \"\$OPTARG\";; esac; done"}},
    {"name": "select菜单", "category": "Shell高级", "prompt": "创建选择菜单", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "select opt in a b c; do echo \"$opt\"; done"}},
    {"name": "别名设置", "category": "Shell高级", "prompt": "设置别名", "expected_tool": "write_file", "expected_args": {"filename": "script.sh", "content": "alias ll='ls -la'"}},
]


# ========== 系统管理 (50个) ==========
SYSTEM_ADMIN_CASES = [
    # 用户管理 (15个)
    {"name": "useradd添加", "category": "用户管理", "prompt": "添加新用户", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "useradd -m newuser"}},
    {"name": "userdel删除", "category": "用户管理", "prompt": "删除用户及其主目录", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "userdel -r olduser"}},
    {"name": "usermod修改", "category": "用户管理", "prompt": "修改用户shell", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "usermod -s /bin/bash user"}},
    {"name": "passwd密码", "category": "用户管理", "prompt": "修改用户密码", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "passwd username"}},
    {"name": "chage密码期", "category": "用户管理", "prompt": "查看密码过期信息", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "chage -l user"}},
    {"name": "groupadd组", "category": "用户管理", "prompt": "添加用户组", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "groupadd developers"}},
    {"name": "groupdel删组", "category": "用户管理", "prompt": "删除用户组", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "groupdel oldgroup"}},
    {"name": "usermod加组", "category": "用户管理", "prompt": "将用户添加到组", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "usermod -aG sudo user"}},
    {"name": "gpasswd组", "category": "用户管理", "prompt": "设置组管理员", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "gpasswd -A admin developers"}},
    {"name": "groups查看", "category": "用户管理", "prompt": "查看用户所属组", "expected_tool": "execute_command", "expected_args": {"command": "groups", "args": "username"}},
    {"name": "id信息", "category": "用户管理", "prompt": "查看用户ID信息", "expected_tool": "execute_command", "expected_args": {"command": "id", "args": "user"}},
    {"name": "whoami我", "category": "用户管理", "prompt": "当前用户名", "expected_tool": "execute_command", "expected_args": {"command": "whoami"}},
    {"name": "w活动", "category": "用户管理", "prompt": "查看登录用户活动", "expected_tool": "execute_command", "expected_args": {"command": "w"}},
    {"name": "last登录", "category": "用户管理", "prompt": "查看最近登录记录", "expected_tool": "execute_command", "expected_args": {"command": "last"}},
    {"name": "faillock", "category": "用户管理", "prompt": "查看登录失败记录", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "faillock"}},

    # 服务管理 (15个)
    {"name": "systemctl状态", "category": "服务管理", "prompt": "查看ssh服务状态", "expected_tool": "execute_command", "expected_args": {"command": "systemctl", "args": "status sshd"}},
    {"name": "systemctl启动", "category": "服务管理", "prompt": "启动nginx服务", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "systemctl start nginx"}},
    {"name": "systemctl停止", "category": "服务管理", "prompt": "停止mysql服务", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "systemctl stop mysql"}},
    {"name": "systemctl重启", "category": "服务管理", "prompt": "重启apache服务", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "systemctl restart apache2"}},
    {"name": "systemctl启用", "category": "服务管理", "prompt": "设置开机启动", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "systemctl enable nginx"}},
    {"name": "systemctl禁用", "category": "服务管理", "prompt": "禁用开机启动", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "systemctl disable nginx"}},
    {"name": "systemctl重载", "category": "服务管理", "prompt": "重载配置", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "systemctl daemon-reload"}},
    {"name": "systemctl列表", "category": "服务管理", "prompt": "列出所有服务", "expected_tool": "execute_command", "expected_args": {"command": "systemctl", "args": "list-units --type=service"}},
    {"name": "service启动", "category": "服务管理", "prompt": "用service启动", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "service nginx start"}},
    {"name": "journalctl日", "category": "服务管理", "prompt": "查看系统日志", "expected_tool": "execute_command", "expected_args": {"command": "journalctl", "args": "-xe"}},
    {"name": "journalctl服", "category": "服务管理", "prompt": "查看nginx日志", "expected_tool": "execute_command", "expected_args": {"command": "journalctl", "args": "-u nginx"}},
    {"name": "journalctl实", "category": "服务管理", "prompt": "实时跟踪日志", "expected_tool": "execute_command", "expected_args": {"command": "journalctl", "args": "-f"}},
    {"name": "logrotate", "category": "服务管理", "prompt": "手动执行日志轮转", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "logrotate -f /etc/logrotate.conf"}},
    {"name": "updategrub", "category": "服务管理", "prompt": "更新GRUB配置", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "update-grub"}},
    {"name": "initramfs", "category": "服务管理", "prompt": "更新initramfs", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "update-initramfs -u"}},

    # 包管理 (10个)
    {"name": "apt更新", "category": "包管理", "prompt": "更新包列表", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "apt update"}},
    {"name": "apt升级", "category": "包管理", "prompt": "升级所有包", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "apt upgrade"}},
    {"name": "apt安装", "category": "包管理", "prompt": "安装nginx", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "apt install nginx"}},
    {"name": "apt删除", "category": "包管理", "prompt": "删除包", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "apt remove nginx"}},
    {"name": "apt清理", "category": "包管理", "prompt": "清理无用包", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "apt autoremove"}},
    {"name": "apt搜索", "category": "包管理", "prompt": "搜索包", "expected_tool": "execute_command", "expected_args": {"command": "apt", "args": "search nginx"}},
    {"name": "dpkg安装", "category": "包管理", "prompt": "安装deb包", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "dpkg -i package.deb"}},
    {"name": "dpkg列表", "category": "包管理", "prompt": "列出已安装包", "expected_tool": "execute_command", "expected_args": {"command": "dpkg", "args": "-l"}},
    {"name": "snap安装", "category": "包管理", "prompt": "snap安装应用", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "snap install firefox"}},
    {"name": "flatpak", "category": "包管理", "prompt": "flatpak安装", "expected_tool": "execute_command", "expected_args": {"command": "flatpak", "args": "install flathub com.spotify.Client"}},

    # 存储管理 (10个)
    {"name": "fdisk分区", "category": "存储管理", "prompt": "查看分区表", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "fdisk -l"}},
    {"name": "mkfs格式", "category": "存储管理", "prompt": "格式化ext4", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "mkfs.ext4 /dev/sdb1"}},
    {"name": "mount挂载", "category": "存储管理", "prompt": "挂载分区", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "mount /dev/sdb1 /mnt"}},
    {"name": "umount卸载", "category": "存储管理", "prompt": "卸载分区", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "umount /mnt"}},
    {"name": "fstab配置", "category": "存储管理", "prompt": "查看fstab", "expected_tool": "execute_command", "expected_args": {"command": "cat", "args": "/etc/fstab"}},
    {"name": "lsblk块", "category": "存储管理", "prompt": "查看块设备", "expected_tool": "execute_command", "expected_args": {"command": "lsblk"}},
    {"name": "blkidUUID", "category": "存储管理", "prompt": "查看UUID", "expected_tool": "execute_command", "expected_args": {"command": "blkid"}},
    {"name": "lvm创建", "category": "存储管理", "prompt": "创建物理卷", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "pvcreate /dev/sdb"}},
    {"name": "lvm卷组", "category": "存储管理", "prompt": "创建卷组", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "vgcreate vg0 /dev/sdb"}},
    {"name": "lvm逻辑", "category": "存储管理", "prompt": "创建逻辑卷", "expected_tool": "execute_command", "expected_args": {"command": "sudo", "args": "lvcreate -L 10G -n lv0 vg0"}},
]


# ========== 包管理和压缩 (30个) ==========
COMPRESSION_CASES = [
    # tar归档 (10个)
    {"name": "tar创建", "category": "归档压缩", "prompt": "创建tar归档", "expected_tool": "execute_command", "expected_args": {"command": "tar", "args": "-cvf archive.tar files/"}},
    {"name": "tar解压", "category": "归档压缩", "prompt": "解压tar归档", "expected_tool": "execute_command", "expected_args": {"command": "tar", "args": "-xvf archive.tar"}},
    {"name": "targz压缩", "category": "归档压缩", "prompt": "gzip压缩归档", "expected_tool": "execute_command", "expected_args": {"command": "tar", "args": "-czvf archive.tar.gz files/"}},
    {"name": "targz解压", "category": "归档压缩", "prompt": "解压tar.gz", "expected_tool": "execute_command", "expected_args": {"command": "tar", "args": "-xzvf archive.tar.gz"}},
    {"name": "tarbz2压", "category": "归档压缩", "prompt": "bzip2压缩归档", "expected_tool": "execute_command", "expected_args": {"command": "tar", "args": "-cjvf archive.tar.bz2 files/"}},
    {"name": "tarbz2解", "category": "归档压缩", "prompt": "解压tar.bz2", "expected_tool": "execute_command", "expected_args": {"command": "tar", "args": "-xjvf archive.tar.bz2"}},
    {"name": "tarxz压", "category": "归档压缩", "prompt": "xz压缩归档", "expected_tool": "execute_command", "expected_args": {"command": "tar", "args": "-cJvf archive.tar.xz files/"}},
    {"name": "tarxz解", "category": "归档压缩", "prompt": "解压tar.xz", "expected_tool": "execute_command", "expected_args": {"command": "tar", "args": "-xJvf archive.tar.xz"}},
    {"name": "tar列出", "category": "归档压缩", "prompt": "列出tar内容", "expected_tool": "execute_command", "expected_args": {"command": "tar", "args": "-tvf archive.tar"}},
    {"name": "tar追加", "category": "归档压缩", "prompt": "追加文件到tar", "expected_tool": "execute_command", "expected_args": {"command": "tar", "args": "-rvf archive.tar newfile"}},

    # gzip/bzip2/xz (10个)
    {"name": "gzip压缩", "category": "归档压缩", "prompt": "gzip压缩文件", "expected_tool": "execute_command", "expected_args": {"command": "gzip", "args": "file.txt"}},
    {"name": "gzip解压", "category": "归档压缩", "prompt": "gzip解压", "expected_tool": "execute_command", "expected_args": {"command": "gzip", "args": "-d file.txt.gz"}},
    {"name": "gunzip", "category": "归档压缩", "prompt": "gunzip解压", "expected_tool": "execute_command", "expected_args": {"command": "gunzip", "args": "file.txt.gz"}},
    {"name": "zcat查看", "category": "归档压缩", "prompt": "直接查看gzip内容", "expected_tool": "execute_command", "expected_args": {"command": "zcat", "args": "file.txt.gz"}},
    {"name": "bzip2压", "category": "归档压缩", "prompt": "bzip2压缩", "expected_tool": "execute_command", "expected_args": {"command": "bzip2", "args": "file.txt"}},
    {"name": "bzip2解", "category": "归档压缩", "prompt": "bzip2解压", "expected_tool": "execute_command", "expected_args": {"command": "bzip2", "args": "-d file.txt.bz2"}},
    {"name": "bzcat", "category": "归档压缩", "prompt": "直接查看bz2内容", "expected_tool": "execute_command", "expected_args": {"command": "bzcat", "args": "file.txt.bz2"}},
    {"name": "xz压缩", "category": "归档压缩", "prompt": "xz压缩文件", "expected_tool": "execute_command", "expected_args": {"command": "xz", "args": "file.txt"}},
    {"name": "xz解压", "category": "归档压缩", "prompt": "xz解压", "expected_tool": "execute_command", "expected_args": {"command": "xz", "args": "-d file.txt.xz"}},
    {"name": "xzcat", "category": "归档压缩", "prompt": "直接查看xz内容", "expected_tool": "execute_command", "expected_args": {"command": "xzcat", "args": "file.txt.xz"}},

    # zip/7z (10个)
    {"name": "zip创建", "category": "归档压缩", "prompt": "创建zip压缩", "expected_tool": "execute_command", "expected_args": {"command": "zip", "args": "-r archive.zip files/"}},
    {"name": "zip解压", "category": "归档压缩", "prompt": "解压zip", "expected_tool": "execute_command", "expected_args": {"command": "unzip", "args": "archive.zip"}},
    {"name": "zip列表", "category": "归档压缩", "prompt": "列出zip内容", "expected_tool": "execute_command", "expected_args": {"command": "unzip", "args": "-l archive.zip"}},
    {"name": "zip密码", "category": "归档压缩", "prompt": "带密码压缩", "expected_tool": "execute_command", "expected_args": {"command": "zip", "args": "-e secure.zip file.txt"}},
    {"name": "7z压缩", "category": "归档压缩", "prompt": "7z压缩", "expected_tool": "execute_command", "expected_args": {"command": "7z", "args": "a archive.7z files/"}},
    {"name": "7z解压", "category": "归档压缩", "prompt": "7z解压", "expected_tool": "execute_command", "expected_args": {"command": "7z", "args": "x archive.7z"}},
    {"name": "7z列表", "category": "归档压缩", "prompt": "列出7z内容", "expected_tool": "execute_command", "expected_args": {"command": "7z", "args": "l archive.7z"}},
    {"name": "rar解压", "category": "归档压缩", "prompt": "解压rar", "expected_tool": "execute_command", "expected_args": {"command": "unrar", "args": "x archive.rar"}},
    {"name": "gzcat", "category": "归档压缩", "prompt": "gzcat查看", "expected_tool": "execute_command", "expected_args": {"command": "gzcat", "args": "file.gz"}},
    {"name": "pigz并行", "category": "归档压缩", "prompt": "并行gzip压缩", "expected_tool": "execute_command", "expected_args": {"command": "pigz", "args": "-p 4 file.txt"}},
]


def get_all_linux_test_cases() -> List[Dict]:
    """获取所有Linux操作测试案例 (300个)"""
    all_cases = []

    # 1. 基础Linux命令 (50个)
    all_cases.extend(BASE_LINUX_CASES)

    # 2. 进程和网络管理 (50个)
    all_cases.extend(PROCESS_NETWORK_CASES)

    # 3. 容器操作 (60个)
    all_cases.extend(CONTAINER_CASES)

    # 4. Shell脚本编程 (60个)
    all_cases.extend(SHELL_SCRIPT_CASES)

    # 5. 系统管理 (50个)
    all_cases.extend(SYSTEM_ADMIN_CASES)

    # 6. 归档压缩 (30个)
    all_cases.extend(COMPRESSION_CASES)

    # 确保每个案例都有description字段
    for case in all_cases:
        if "description" not in case:
            case["description"] = f"测试{case['category']}操作"

    return all_cases


# 导出测试案例
LINUX_OPS_TEST_CASES = get_all_linux_test_cases()

if __name__ == "__main__":
    print(f"生成了 {len(LINUX_OPS_TEST_CASES)} 个Linux操作测试案例")

    # 统计各类别数量
    from collections import Counter
    categories = Counter(case["category"] for case in LINUX_OPS_TEST_CASES)
    print("\n类别分布:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}个")
