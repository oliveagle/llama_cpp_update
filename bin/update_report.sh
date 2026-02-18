#!/bin/bash
# llama.cpp 报告更新脚本
# 使用方法: ./update_report.sh

echo "🔄 更新 llama.cpp 测试报告..."

# 检查容器是否存在
if podman ps -a | grep -q nginx-llama-reports; then
    echo "🔄 重启 nginx 容器以同步最新内容..."
    podman restart nginx-llama-reports
    sleep 2

    # 验证服务状态
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8080 | grep -q "200"; then
        echo "✅ nginx 报告服务已更新并运行正常"
        echo "📍 访问地址: http://localhost:8080"
    else
        echo "❌ 服务启动失败，请检查日志:"
        podman logs nginx-llama-reports
        exit 1
    fi
else
    echo "❌ nginx 容器不存在，请先启动服务:"
    echo "   podman run -d --name nginx-llama-reports -p 8080:80 \\"
    echo "     -v /mnt/volume3/llama_cpp/report_web:/usr/share/nginx/html:ro \\"
    echo "     -v /mnt/volume3/llama_cpp/nginx.conf:/etc/nginx/conf.d/default.conf:ro \\"
    echo "     --restart=unless-stopped docker.io/library/nginx:alpine"
    exit 1
fi

echo ""
echo "📊 可用页面:"
echo "   - 首页:      http://localhost:8080/index.html"
echo "   - Stage 1:   http://localhost:8080/stage1.html (性能测试)"
echo "   - Stage 2:   http://localhost:8080/stage2.html (基础能力)"
echo "   - Stage 3:   http://localhost:8080/stage3.html (综合能力)"
echo "   - 测试规范:  http://localhost:8080/methodology.html"
