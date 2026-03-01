#!/usr/bin/env python3
"""
Stage 3 深度Linux Shell测试 (100 cases)
涵盖：文件操作、文本处理、系统管理、网络、脚本编程等
"""

import time
import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from framework.base import BaseEvaluator, TestResult, StageResult


# Linux Shell测试用例 (100个)
SHELL_TEST_CASES = [
    # ===== 文件操作命令 (20题) =====
    {"id": 1, "name": "列出文件", "category": "文件操作", "difficulty": "简单",
     "question": "列出当前目录所有文件（包括隐藏文件）的命令是：",
     "options": ["ls", "ls -a", "ls -l", "ll"], "answer": "B"},
    {"id": 2, "name": "切换目录", "category": "文件操作", "difficulty": "简单",
     "question": "切换到上级目录的命令是：",
     "options": ["cd /", "cd ..", "cd ~", "cd -"], "answer": "B"},
    {"id": 3, "name": "创建目录", "category": "文件操作", "difficulty": "简单",
     "question": "递归创建多级目录的命令是：",
     "options": ["mkdir dir", "mkdir -p dir/subdir", "rmdir dir", "touch dir"], "answer": "B"},
    {"id": 4, "name": "复制文件", "category": "文件操作", "difficulty": "简单",
     "question": "复制目录及其内容的命令是：",
     "options": ["cp src dst", "cp -r src dst", "mv src dst", "scp src dst"], "answer": "B"},
    {"id": 5, "name": "移动文件", "category": "文件操作", "difficulty": "简单",
     "question": "移动文件并覆盖已存在文件的命令是：",
     "options": ["mv -f src dst", "cp src dst", "rm src", "ln src dst"], "answer": "A"},
    {"id": 6, "name": "删除文件", "category": "文件操作", "difficulty": "中等",
     "question": "强制递归删除目录的命令是：",
     "options": ["rm file", "rm -rf dir", "rmdir dir", "del dir"], "answer": "B"},
    {"id": 7, "name": "查看当前目录", "category": "文件操作", "difficulty": "简单",
     "question": "显示当前工作目录的命令是：",
     "options": ["pwd", "cd", "ls", "dir"], "answer": "A"},
    {"id": 8, "name": "创建空文件", "category": "文件操作", "difficulty": "简单",
     "question": "创建空文件或更新文件时间的命令是：",
     "options": ["mkdir", "touch", "cat", "echo"], "answer": "B"},
    {"id": 9, "name": "查看文件类型", "category": "文件操作", "difficulty": "中等",
     "question": "识别文件类型的命令是：",
     "options": ["type", "file", "whatis", "which"], "answer": "B"},
    {"id": 10, "name": "查找文件", "category": "文件操作", "difficulty": "中等",
     "question": "在当前目录查找所有.txt文件的命令是：",
     "options": ["find . -name '*.txt'", "grep '*.txt'", "locate '*.txt'", "search '*.txt'"], "answer": "A"},
    {"id": 11, "name": "文件链接", "category": "文件操作", "difficulty": "中等",
     "question": "创建软链接的命令是：",
     "options": ["ln file link", "ln -s file link", "link file link", "cp -l file link"], "answer": "B"},
    {"id": 12, "name": "修改权限", "category": "文件操作", "difficulty": "中等",
     "question": "给文件添加可执行权限的命令是：",
     "options": ["chmod +x file", "chmod 644 file", "chown +x file", "attrib +x file"], "answer": "A"},
    {"id": 13, "name": "修改所有者", "category": "文件操作", "difficulty": "中等",
     "question": "递归修改目录及其子目录所有者的命令是：",
     "options": ["chown user file", "chown -R user:group dir", "chmod -R user dir", "chgrp -R user dir"], "answer": "B"},
    {"id": 14, "name": "磁盘使用", "category": "文件操作", "difficulty": "中等",
     "question": "查看目录磁盘使用情况的命令是：",
     "options": ["df", "du -sh dir", "ls -lh", "fdisk"], "answer": "B"},
    {"id": 15, "name": "打包压缩", "category": "文件操作", "difficulty": "中等",
     "question": "将目录打包并用gzip压缩的命令是：",
     "options": ["tar -cvf dir.tar dir", "tar -czvf dir.tar.gz dir", "zip dir.zip dir", "gzip dir"], "answer": "B"},
    {"id": 16, "name": "解压缩", "category": "文件操作", "difficulty": "中等",
     "question": "解压tar.gz文件的命令是：",
     "options": ["tar -xvf file.tar.gz", "tar -xzvf file.tar.gz", "gzip -d file.tar.gz", "unzip file.tar.gz"], "answer": "B"},
    {"id": 17, "name": "比较文件", "category": "文件操作", "difficulty": "中等",
     "question": "逐行比较两个文本文件差异的命令是：",
     "options": ["cmp file1 file2", "diff file1 file2", "comm file1 file2", "patch file1 file2"], "answer": "B"},
    {"id": 18, "name": "查看文件属性", "category": "文件操作", "difficulty": "简单",
     "question": "详细显示文件信息的命令是：",
     "options": ["ls", "ls -l", "file", "stat"], "answer": "B"},
    {"id": 19, "name": "磁盘空间", "category": "文件操作", "difficulty": "简单",
     "question": "查看文件系统磁盘空间使用情况的命令是：",
     "options": ["du", "df -h", "ls", "free"], "answer": "B"},
    {"id": 20, "name": "文件同步", "category": "文件操作", "difficulty": "困难",
     "question": "本地与远程同步文件的命令是：",
     "options": ["scp", "rsync", "sftp", "ftp"], "answer": "B"},

    # ===== 文本处理命令 (20题) =====
    {"id": 21, "name": "查看文件内容", "category": "文本处理", "difficulty": "简单",
     "question": "分页查看大文件的命令是：",
     "options": ["cat", "more/less", "head", "tail"], "answer": "B"},
    {"id": 22, "name": "查看文件开头", "category": "文本处理", "difficulty": "简单",
     "question": "查看文件前10行的命令是：",
     "options": ["head file", "head -n 10 file", "tail file", "cat file | head"], "answer": "B"},
    {"id": 23, "name": "查看文件末尾", "category": "文本处理", "difficulty": "简单",
     "question": "实时查看日志文件新增内容的命令是：",
     "options": ["tail file", "tail -f file", "cat file", "watch file"], "answer": "B"},
    {"id": 24, "name": "文本搜索", "category": "文本处理", "difficulty": "中等",
     "question": "在文件中搜索'error'并显示行号的命令是：",
     "options": ["grep error file", "grep -n error file", "find error file", "search error file"], "answer": "B"},
    {"id": 25, "name": "正则搜索", "category": "文本处理", "difficulty": "中等",
     "question": "搜索以数字开头的行的命令是：",
     "options": ["grep '^[0-9]' file", "grep '[0-9]$' file", "grep '[0-9]' file", "grep -v '[0-9]' file"], "answer": "A"},
    {"id": 26, "name": "文本统计", "category": "文本处理", "difficulty": "简单",
     "question": "统计文件行数、字数、字节数的命令是：",
     "options": ["count", "wc", "stat", "size"], "answer": "B"},
    {"id": 27, "name": "文本排序", "category": "文本处理", "difficulty": "中等",
     "question": "按数字大小对文件内容进行排序的命令是：",
     "options": ["sort file", "sort -n file", "sort -r file", "uniq file"], "answer": "B"},
    {"id": 28, "name": "去重", "category": "文本处理", "difficulty": "中等",
     "question": "去除文件中相邻重复行的命令是：",
     "options": ["sort -u file", "uniq file", "sort file | uniq", "grep -v duplicate file"], "answer": "C"},
    {"id": 29, "name": "文本替换", "category": "文本处理", "difficulty": "中等",
     "question": "将文件中所有'apple'替换为'orange'的命令是：",
     "options": ["sed 's/apple/orange/' file", "sed 's/apple/orange/g' file", "grep 'apple' file | replace", "awk '{gsub(/apple/,orange)}' file"], "answer": "B"},
    {"id": 30, "name": "文本截取", "category": "文本处理", "difficulty": "中等",
     "question": "提取文件中第2到第5个字段的命令是：",
     "options": ["cut -f 2-5 file", "cut -d: -f 2-5 file", "awk '{print $2-$5}' file", "sed -n '2,5p' file"], "answer": "B"},
    {"id": 31, "name": "AWK基础", "category": "文本处理", "difficulty": "困难",
     "question": "打印文件第一列的命令是：",
     "options": ["awk '{print $1}' file", "awk '{print $0}' file", "cut -f1 file", "both A and C"], "answer": "D"},
    {"id": 32, "name": "AWK条件", "category": "文本处理", "difficulty": "困难",
     "question": "打印文件中第三列大于100的行的命令是：",
     "options": ["awk '$3 > 100' file", "awk '{if($3>100)print}' file", "grep '$3>100' file", "A和B都可以"], "answer": "D"},
    {"id": 33, "name": "SED删除", "category": "文本处理", "difficulty": "中等",
     "question": "删除文件中空行的命令是：",
     "options": ["sed '/^$/d' file", "sed 's/^$//' file", "grep -v '^$' file", "A和C都可以"], "answer": "D"},
    {"id": 34, "name": "SED多行", "category": "文本处理", "difficulty": "困难",
     "question": "删除文件中第3到第5行的命令是：",
     "options": ["sed '3,5d' file", "sed -n '3,5p' file", "head -2 file; tail -n +6 file", "A和C都可以"], "answer": "D"},
    {"id": 35, "name": "管道组合", "category": "文本处理", "difficulty": "中等",
     "question": "统计文件中不重复行数的命令是：",
     "options": ["sort file | uniq | wc -l", "sort -u file | wc -l", "uniq file | wc -l", "以上都可以"], "answer": "D"},
    {"id": 36, "name": "TR命令", "category": "文本处理", "difficulty": "中等",
     "question": "将小写字母转换为大写的命令是：",
     "options": ["tr 'a-z' 'A-Z'", "tr '[lower]' '[upper]'", "toupper", "uppercase"], "answer": "A"},
    {"id": 37, "name": "文本合并", "category": "文本处理", "difficulty": "简单",
     "question": "按行合并两个文件的命令是：",
     "options": ["cat file1 file2", "paste file1 file2", "join file1 file2", "merge file1 file2"], "answer": "B"},
    {"id": 38, "name": "字符串分割", "category": "文本处理", "difficulty": "困难",
     "question": "将逗号分隔的文件转换为制表符分隔的命令是：",
     "options": ["tr ',' '\\t'", "sed 's/,/\\t/g'", "awk 'BEGIN{FS=OFS=\"\\t\"}{gsub(/,/,OFS)}1'", "以上都可以"], "answer": "D"},
    {"id": 39, "name": "日志分析", "category": "文本处理", "difficulty": "困难",
     "question": "统计日志中每种HTTP状态码出现次数的命令是：",
     "options": ["awk '{print $9}' access.log | sort | uniq -c", "grep -c '200' access.log", "cat access.log | count status", "sort access.log | uniq"], "answer": "A"},
    {"id": 40, "name": "JSON处理", "category": "文本处理", "difficulty": "困难",
     "question": "命令行处理JSON的工具是：",
     "options": ["json", "jq", "yj", "pj"], "answer": "B"},

    # ===== 系统管理 (20题) =====
    {"id": 41, "name": "查看进程", "category": "系统管理", "difficulty": "简单",
     "question": "查看所有进程信息的命令是：",
     "options": ["ps", "ps aux", "top", "tasklist"], "answer": "B"},
    {"id": 42, "name": "实时进程", "category": "系统管理", "difficulty": "简单",
     "question": "实时显示进程状态的命令是：",
     "options": ["ps", "top", "htop", "proc"], "answer": "B"},
    {"id": 43, "name": "终止进程", "category": "系统管理", "difficulty": "中等",
     "question": "强制终止PID为1234的进程的命令是：",
     "options": ["kill 1234", "kill -9 1234", "stop 1234", "end 1234"], "answer": "B"},
    {"id": 44, "name": "查找进程", "category": "系统管理", "difficulty": "中等",
     "question": "查找名为nginx的进程ID的命令是：",
     "options": ["ps aux | grep nginx", "pgrep nginx", "pidof nginx", "以上都可以"], "answer": "D"},
    {"id": 45, "name": "系统信息", "category": "系统管理", "difficulty": "简单",
     "question": "查看系统内核版本的命令是：",
     "options": ["version", "uname -r", "kernel", "sysinfo"], "answer": "B"},
    {"id": 46, "name": "内存使用", "category": "系统管理", "difficulty": "简单",
     "question": "查看内存使用情况的命令是：",
     "options": ["mem", "free -h", "memory", "vmstat"], "answer": "B"},
    {"id": 47, "name": "CPU信息", "category": "系统管理", "difficulty": "简单",
     "question": "查看CPU信息的命令是：",
     "options": ["cpuinfo", "lscpu", "cat /proc/cpu", "processor"], "answer": "B"},
    {"id": 48, "name": "用户管理", "category": "系统管理", "difficulty": "中等",
     "question": "添加新用户的命令是：",
     "options": ["adduser username", "useradd username", "newuser username", "A和B都可以"], "answer": "D"},
    {"id": 49, "name": "切换用户", "category": "系统管理", "difficulty": "简单",
     "question": "切换到root用户并加载其环境的命令是：",
     "options": ["su root", "su - root", "sudo root", "login root"], "answer": "B"},
    {"id": 50, "name": "sudo权限", "category": "系统管理", "difficulty": "中等",
     "question": "编辑sudoers文件的推荐命令是：",
     "options": ["vi /etc/sudoers", "nano /etc/sudoers", "visudo", "edit sudoers"], "answer": "C"},
    {"id": 51, "name": "服务管理", "category": "系统管理", "difficulty": "中等",
     "question": "systemd系统中重启服务的命令是：",
     "options": ["service nginx restart", "systemctl restart nginx", "/etc/init.d/nginx restart", "A和B都可以"], "answer": "D"},
    {"id": 52, "name": "定时任务", "category": "系统管理", "difficulty": "中等",
     "question": "编辑当前用户定时任务的命令是：",
     "options": ["crontab -e", "cron -e", "at -e", "timer -e"], "answer": "A"},
    {"id": 53, "name": "crontab格式", "category": "系统管理", "difficulty": "困难",
     "question": "crontab中每天凌晨2点执行的写法是：",
     "options": ["* 2 * * *", "0 2 * * *", "2 0 * * *", "0 0 2 * *"], "answer": "B"},
    {"id": 54, "name": "环境变量", "category": "系统管理", "difficulty": "中等",
     "question": "查看所有环境变量的命令是：",
     "options": ["env", "printenv", "echo $PATH", "A和B都可以"], "answer": "D"},
    {"id": 55, "name": "系统时间", "category": "系统管理", "difficulty": "简单",
     "question": "查看当前系统时间的命令是：",
     "options": ["time", "date", "clock", "datetime"], "answer": "B"},
    {"id": 56, "name": "系统启动时间", "category": "系统管理", "difficulty": "中等",
     "question": "查看系统运行时间的命令是：",
     "options": ["uptime", "boottime", "runtime", "systemtime"], "answer": "A"},
    {"id": 57, "name": "已登录用户", "category": "系统管理", "difficulty": "简单",
     "question": "查看当前登录用户的命令是：",
     "options": ["who", "whoami", "users", "login"], "answer": "A"},
    {"id": 58, "name": "最后登录", "category": "系统管理", "difficulty": "中等",
     "question": "查看用户最后登录时间的命令是：",
     "options": ["last", "lastlog", "loginlog", "userlog"], "answer": "B"},
    {"id": 59, "name": "系统负载", "category": "系统管理", "difficulty": "中等",
     "question": "查看系统平均负载的命令是：",
     "options": ["load", "uptime", "w", "B和C都可以"], "answer": "D"},
    {"id": 60, "name": "硬件信息", "category": "系统管理", "difficulty": "中等",
     "question": "列出所有PCI设备的命令是：",
     "options": ["lsdev", "lspci", "listpci", "pcidev"], "answer": "B"},

    # ===== 网络命令 (20题) =====
    {"id": 61, "name": "查看IP", "category": "网络", "difficulty": "简单",
     "question": "查看网络接口IP地址的命令是：",
     "options": ["ipconfig", "ifconfig/ip addr", "netstat", "route"], "answer": "B"},
    {"id": 62, "name": "测试连通性", "category": "网络", "difficulty": "简单",
     "question": "测试与主机连通性的命令是：",
     "options": ["ping", "traceroute", "telnet", "nc"], "answer": "A"},
    {"id": 63, "name": "路由跟踪", "category": "网络", "difficulty": "中等",
     "question": "追踪数据包路由路径的命令是：",
     "options": ["ping", "traceroute/tracepath", "route", "path"], "answer": "B"},
    {"id": 64, "name": "查看端口", "category": "网络", "difficulty": "中等",
     "question": "查看所有网络连接和监听端口的命令是：",
     "options": ["netstat -tulpn", "ss -tulpn", "lsof -i", "以上都可以"], "answer": "D"},
    {"id": 65, "name": "下载文件", "category": "网络", "difficulty": "简单",
     "question": "从URL下载文件的命令是：",
     "options": ["download", "wget/curl", "fetch", "get"], "answer": "B"},
    {"id": 66, "name": "DNS查询", "category": "网络", "difficulty": "中等",
     "question": "查询域名DNS信息的命令是：",
     "options": ["dns", "nslookup/dig", "host", "B和C都可以"], "answer": "D"},
    {"id": 67, "name": "SSH连接", "category": "网络", "difficulty": "简单",
     "question": "远程登录到服务器的命令是：",
     "options": ["telnet", "ssh", "ftp", "rdp"], "answer": "B"},
    {"id": 68, "name": "SCP传输", "category": "网络", "difficulty": "中等",
     "question": "安全复制本地文件到远程服务器的命令是：",
     "options": ["cp file user@host:/path", "scp file user@host:/path", "sftp file user@host", "rsync file user@host:/path"], "answer": "B"},
    {"id": 69, "name": "防火墙", "category": "网络", "difficulty": "中等",
     "question": "iptables中允许80端口的命令是：",
     "options": ["iptables -A INPUT -p tcp --dport 80 -j ACCEPT", "iptables -I INPUT -p tcp --dport 80", "firewall-cmd --add-port=80/tcp", "A和C都可以"], "answer": "D"},
    {"id": 70, "name": "网络统计", "category": "网络", "difficulty": "中等",
     "question": "显示网络接口统计信息的命令是：",
     "options": ["netstat -i", "ifconfig -a", "ip -s link", "以上都可以"], "answer": "D"},
    {"id": 71, "name": "抓包", "category": "网络", "difficulty": "困难",
     "question": "抓取eth0网卡80端口流量的命令是：",
     "options": ["tcpdump -i eth0 port 80", "tcpdump port 80", "wireshark eth0:80", "capture eth0 80"], "answer": "A"},
    {"id": 72, "name": "HTTP请求", "category": "网络", "difficulty": "中等",
     "question": "使用curl发送POST请求携带JSON数据的命令是：",
     "options": ["curl -X POST -d '{\"key\":\"value\"}' URL", "curl -X POST -H 'Content-Type: application/json' -d '{\"key\":\"value\"}' URL", "curl POST URL data='{\"key\":\"value\"}'", "以上都可以"], "answer": "B"},
    {"id": 73, "name": "网卡重启", "category": "网络", "difficulty": "中等",
     "question": "重启网络服务的命令是：",
     "options": ["service network restart", "systemctl restart network", "/etc/init.d/network restart", "以上都可以"], "answer": "D"},
    {"id": 74, "name": "路由表", "category": "网络", "difficulty": "中等",
     "question": "查看系统路由表的命令是：",
     "options": ["route -n", "ip route", "netstat -r", "以上都可以"], "answer": "D"},
    {"id": 75, "name": "ARP缓存", "category": "网络", "difficulty": "中等",
     "question": "查看ARP缓存表的命令是：",
     "options": ["arp -a", "ip neigh", "cat /proc/net/arp", "以上都可以"], "answer": "D"},
    {"id": 76, "name": "端口扫描", "category": "网络", "difficulty": "困难",
     "question": "扫描主机开放端口的命令是：",
     "options": ["nmap", "scan", "portscan", "checkport"], "answer": "A"},
    {"id": 77, "name": "Socket统计", "category": "网络", "difficulty": "中等",
     "question": "查看socket统计信息的命令是：",
     "options": ["sockstat", "ss", "socket", "netsock"], "answer": "B"},
    {"id": 78, "name": "网卡配置", "category": "网络", "difficulty": "困难",
     "question": "临时配置eth0 IP地址的命令是：",
     "options": ["ifconfig eth0 192.168.1.100", "ip addr add 192.168.1.100/24 dev eth0", "ipconfig eth0 192.168.1.100", "A和B都可以"], "answer": "D"},
    {"id": 79, "name": "网络重启", "category": "网络", "difficulty": "中等",
     "question": "重新加载网络配置的命令是：",
     "options": ["reload network", "systemctl reload network", "ifdown eth0 && ifup eth0", "以上都可以"], "answer": "D"},
    {"id": 80, "name": "带宽测试", "category": "网络", "difficulty": "困难",
     "question": "测试网络带宽的工具是：",
     "options": ["speedtest", "iperf", "bandwidth", "netspeed"], "answer": "B"},

    # ===== Shell脚本 (20题) =====
    {"id": 81, "name": "变量定义", "category": "Shell脚本", "difficulty": "简单",
     "question": "Shell中定义变量并赋值的正确语法是：",
     "options": ["var = value", "var=value", "set var=value", "let var=value"], "answer": "B"},
    {"id": 82, "name": "变量引用", "category": "Shell脚本", "difficulty": "简单",
     "question": "引用变量值的正确方式是：",
     "options": ["var", "$var", "@var", "%var%"], "answer": "B"},
    {"id": 83, "name": "条件判断", "category": "Shell脚本", "difficulty": "中等",
     "question": "判断文件是否存在的正确语法是：",
     "options": ["if [ -f file ]", "if [ -e file ]", "if exists file", "A和B都可以"], "answer": "D"},
    {"id": 84, "name": "循环语句", "category": "Shell脚本", "difficulty": "中等",
     "question": "遍历1到10的for循环正确写法是：",
     "options": ["for i in {1..10}", "for i in $(seq 1 10)", "for((i=1;i<=10;i++))", "以上都可以"], "answer": "D"},
    {"id": 85, "name": "函数定义", "category": "Shell脚本", "difficulty": "中等",
     "question": "Shell中定义函数的正确语法是：",
     "options": ["function name() {}", "name() {}", "def name():", "A和B都可以"], "answer": "D"},
    {"id": 86, "name": "参数传递", "category": "Shell脚本", "difficulty": "中等",
     "question": "Shell脚本中获取所有参数的方法是：",
     "options": ["$*", "$@", "$#", "A和B都可以"], "answer": "D"},
    {"id": 87, "name": "参数个数", "category": "Shell脚本", "difficulty": "简单",
     "question": "Shell脚本中获取参数个数的特殊变量是：",
     "options": ["$#", "$*", "$@", "$$"], "answer": "A"},
    {"id": 88, "name": "退出状态", "category": "Shell脚本", "difficulty": "简单",
     "question": "获取上条命令退出状态的变量是：",
     "options": ["$?", "$!", "$$", "$0"], "answer": "A"},
    {"id": 89, "name": "命令替换", "category": "Shell脚本", "difficulty": "中等",
     "question": "将命令输出赋值给变量的正确方式是：",
     "options": ["var=$(command)", "var=`command`", "var=(command)", "A和B都可以"], "answer": "D"},
    {"id": 90, "name": "字符串比较", "category": "Shell脚本", "difficulty": "中等",
     "question": "Shell中判断字符串相等的正确语法是：",
     "options": ["if [ $a = $b ]", "if [ $a == $b ]", "if [ \"$a\" = \"$b\" ]", "以上都可以"], "answer": "C"},
    {"id": 91, "name": "数值比较", "category": "Shell脚本", "difficulty": "中等",
     "question": "Shell中判断数值大于的正确语法是：",
     "options": ["if [ $a > $b ]", "if [ $a -gt $b ]", "if (($a > $b))", "B和C都可以"], "answer": "D"},
    {"id": 92, "name": "数组定义", "category": "Shell脚本", "difficulty": "中等",
     "question": "Bash中定义数组的正确语法是：",
     "options": ["arr=(1 2 3)", "arr=[1,2,3]", "arr={1,2,3}", "arr=1,2,3"], "answer": "A"},
    {"id": 93, "name": "数组访问", "category": "Shell脚本", "difficulty": "中等",
     "question": "获取Bash数组长度的方法是：",
     "options": ["${#arr}", "${#arr[@]}", "${#arr[*]}", "B和C都可以"], "answer": "D"},
    {"id": 94, "name": "Here Document", "category": "Shell脚本", "difficulty": "中等",
     "question": "Here Document的正确语法是：",
     "options": ["cat << EOF ... EOF", "cat < EOF ... EOF", "cat > EOF ... EOF", "cat | EOF ... EOF"], "answer": "A"},
    {"id": 95, "name": "case语句", "category": "Shell脚本", "difficulty": "中等",
     "question": "Shell中case语句的结束标记是：",
     "options": ["end", "esac", "done", "fi"], "answer": "B"},
    {"id": 96, "name": "后台运行", "category": "Shell脚本", "difficulty": "简单",
     "question": "让命令在后台运行的方式是：",
     "options": ["command bg", "command &", "bg command", "command > /dev/null"], "answer": "B"},
    {"id": 97, "name": "信号捕获", "category": "Shell脚本", "difficulty": "困难",
     "question": "捕获Ctrl+C信号的命令是：",
     "options": ["catch SIGINT", "trap 'command' INT", "signal INT command", "handle INT"], "answer": "B"},
    {"id": 98, "name": "子Shell", "category": "Shell脚本", "difficulty": "困难",
     "question": "在当前Shell中执行脚本的命令是：",
     "options": ["./script.sh", "sh script.sh", "source script.sh 或 . script.sh", "exec script.sh"], "answer": "C"},
    {"id": 99, "name": "调试脚本", "category": "Shell脚本", "difficulty": "中等",
     "question": "启用Shell脚本调试模式的选项是：",
     "options": ["-d", "-x", "-v", "-debug"], "answer": "B"},
    {"id": 100, "name": "正则匹配", "category": "Shell脚本", "difficulty": "困难",
     "question": "Shell中判断字符串匹配正则的语法是：",
     "options": ["if [[ $var =~ regex ]]", "if [ $var =~ regex ]", "if match $var regex", "if regex $var"], "answer": "A"},
]


class ShellEvaluator(BaseEvaluator):
    """Linux Shell能力评估器"""

    name = "shell"
    description = "Linux Shell测试"

    @property
    def stage_name(self) -> str:
        return "深度能力测试-Linux Shell"

    @property
    def stage_number(self) -> int:
        return 3

    @property
    def threshold_percentage(self) -> float:
        return 0.6  # 60% 通过门槛

    def __init__(self, model_url: str, model_name: str, **kwargs):
        super().__init__(model_url, model_name, **kwargs)
        from utils.raw_data_logger import RawDataLogger
        backend = "v100" if "8401" in model_url else "vulkan"
        self.raw_logger = RawDataLogger(backend)

    def run_tests(self) -> StageResult:
        """运行Linux Shell测试"""
        import requests

        test_results = []
        start_time = time.time()

        for test_case in SHELL_TEST_CASES:
            result = self._test_single_case(test_case)
            test_results.append(result)

        elapsed = time.time() - start_time

        passed = sum(1 for r in test_results if r.passed)
        total = len(test_results)

        return StageResult(
            stage_name=self.stage_name,
            stage_number=self.stage_number,
            total_tests=total,
            passed_tests=passed,
            failed_tests=total - passed,
            duration_seconds=elapsed,
            test_results=test_results,
            passed_threshold=(passed / total >= self.threshold_percentage) if total > 0 else False,
            threshold_percentage=self.threshold_percentage
        )

    def _test_single_case(self, test_case: dict) -> TestResult:
        """测试单个Shell用例"""
        import requests

        url = f"{self.model_url}/v1/chat/completions"
        options_str = "\n".join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(test_case['options'])])
        prompt = f"回答以下Linux Shell问题，只输出选项字母(A/B/C/D)：\n\n{test_case['question']}\n\n{options_str}\n\n答案："

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "你是一个Linux系统专家。只回答选项字母，不要解释。"},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 4096,
            "temperature": 0.1
        }

        start = time.time()
        try:
            resp = requests.post(url, json=payload, timeout=60)
            elapsed = time.time() - start

            if resp.status_code != 200:
                return TestResult(
                    name=test_case['name'],
                    category=test_case['category'],
                    passed=False,
                    duration_ms=elapsed * 1000,
                    error_message=f"HTTP {resp.status_code}"
                )

            data = resp.json()
            content = data["choices"][0]["message"].get("content", "")
            if not content:
                content = data["choices"][0]["message"].get("reasoning_content", "")

            # 提取答案字母
            answer = self._extract_answer(content)
            expected = test_case['answer']
            passed = answer == expected

            # 记录原始数据
            self.raw_logger.log_test_result({
                "model": self.model_name,
                "test_name": test_case['name'],
                "question": test_case['question'],
                "expected": expected,
                "actual": answer,
                "passed": passed
            }, test_type="shell_stage3")

            return TestResult(
                name=test_case['name'],
                category=test_case['category'],
                passed=passed,
                duration_ms=elapsed * 1000,
                details={
                    "difficulty": test_case['difficulty'],
                    "expected": expected,
                    "actual": answer
                }
            )

        except Exception as e:
            return TestResult(
                name=test_case['name'],
                category=test_case['category'],
                passed=False,
                duration_ms=0,
                error_message=str(e)
            )

    def _extract_after_think(self, text: str) -> str:
        """提取 </think> 标签后的内容"""
        if not text:
            return text
        patterns = [
            r'</think>\s*(.*)',  # 标准格式
            r'\*\*Final Answer:\*\*\s*(.*)',  # 某些模型的格式
            r'答案是\s*[:：]\s*(.*)',  # 中文格式
            r'答案[是为]\s*[:：]\s*(.*)',  # 中文格式变体
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return text

    def _extract_answer(self, text: str) -> str:
        """从文本中提取答案字母 - 支持推理模型"""
        # 先提取 </think> 后的内容
        text = self._extract_after_think(text).upper()

        # 尝试匹配 "答案: A" 或 "答案是 B" 格式
        patterns = [
            r'答案[:：]\s*([A-D])',  # 答案: A
            r'答案(?:是|为)[:：]?\s*([A-D])',  # 答案是 A / 答案为A
            r'[\(\[\{]([A-D])[\)\]\}]',  # (A) [A] {A}
            r'\b([A-D])[\.、\)]',  # A. A、 A)
            r'选项[:：]?\s*([A-D])',  # 选项: A
            r'[选|答][择|案][:：]?\s*([A-D])',  # 选择: A / 答案: A
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)

        # 在 </think> 后的内容中找最后一个独立的 A-D 字母
        matches = re.findall(r'\b([A-D])\b', text)
        if matches:
            return matches[-1]  # 返回最后一个匹配

        # 最后的备选：找第一个 A-D 字符
        match = re.search(r'[A-D]', text)
        return match.group(0) if match else ""


def run_shell_test(model_url: str, model_name: str) -> dict:
    """运行Linux Shell测试"""
    evaluator = ShellEvaluator(model_url, model_name)
    stage_result = evaluator.run_tests()

    return {
        "model": model_name,
        "url": model_url,
        "stage": stage_result.stage_number,
        "stage_name": stage_result.stage_name,
        "total_tests": stage_result.total_tests,
        "passed_tests": stage_result.passed_tests,
        "failed_tests": stage_result.failed_tests,
        "pass_rate": stage_result.pass_rate,
        "duration_seconds": stage_result.duration_seconds,
        "passed_threshold": stage_result.passed_threshold,
        "tests": [
            {
                "name": r.name,
                "category": r.category,
                "passed": r.passed,
                "duration_ms": r.duration_ms,
                "details": r.details,
                "error": r.error_message
            }
            for r in stage_result.test_results
        ]
    }


if __name__ == "__main__":
    result = run_shell_test("http://localhost:8400", "Qwen3VL-4B-Instruct-Q8_0")
    print(f"Linux Shell测试: {result['passed_tests']}/{result['total_tests']} ({result['pass_rate']*100:.1f}%)")
