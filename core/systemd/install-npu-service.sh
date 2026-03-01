#!/bin/bash
#
# 安装 llama-npu-server systemd 服务
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_FILE="$SCRIPT_DIR/llama-npu-server.service"
SYSTEMD_DIR="/etc/systemd/system"

echo "=== llama-npu-server systemd 服务安装 ==="
echo ""

# 检查 root 权限
if [ "$EUID" -ne 0 ]; then
    echo "错误：请使用 sudo 运行此脚本"
    echo "用法：sudo $0"
    exit 1
fi

# 检查服务文件
if [ ! -f "$SERVICE_FILE" ]; then
    echo "错误：服务文件不存在：$SERVICE_FILE"
    exit 1
fi

# 复制服务文件
echo "复制服务文件到 $SYSTEMD_DIR..."
cp "$SERVICE_FILE" "$SYSTEMD_DIR/"

# 重载 systemd
echo "重载 systemd 配置..."
systemctl daemon-reload

# 启用服务（开机自启）
echo "启用服务（开机自启）..."
systemctl enable llama-npu-server.service

echo ""
echo "✓ 安装完成！"
echo ""
echo "用法:"
echo "  sudo systemctl start llama-npu-server    # 启动服务"
echo "  sudo systemctl stop llama-npu-server     # 停止服务"
echo "  sudo systemctl restart llama-npu-server  # 重启服务"
echo "  sudo systemctl status llama-npu-server   # 查看状态"
echo "  journalctl -u llama-npu-server -f        # 查看日志"
echo ""
echo "注意：请确保在服务文件中正确配置了模型路径和环境变量"
