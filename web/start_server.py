#!/usr/bin/env python3
"""
llama.cpp 评测报告 HTTP 服务器
监听 0.0.0.0:9820，提供测试报告网页服务
"""

import http.server
import socketserver
import os
import sys

PORT = 9820
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # 添加 CORS 头，允许跨域访问
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def log_message(self, format, *args):
        # 自定义日志格式
        print(f"[{self.log_date_time_string()}] {args[0]}")

def main():
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           llama.cpp 评测报告 HTTP 服务器                      ║
╠══════════════════════════════════════════════════════════════╣
║  服务地址: http://0.0.0.0:{PORT}                            ║
║  网页目录: {DIRECTORY:<45} ║
╠══════════════════════════════════════════════════════════════╣
║  可用页面:                                                    ║
║    • http://localhost:{PORT}/index.html      - 概览          ║
║    • http://localhost:{PORT}/stage1.html     - Stage 1 性能  ║
║    • http://localhost:{PORT}/stage2.html     - Stage 2 基础  ║
║    • http://localhost:{PORT}/stage3.html     - Stage 3 综合  ║
║    • http://localhost:{PORT}/methodology.html - 测试规范     ║
╚══════════════════════════════════════════════════════════════╝
按 Ctrl+C 停止服务器
""")

    try:
        with socketserver.TCPServer(("0.0.0.0", PORT), MyHTTPRequestHandler) as httpd:
            print(f"服务器已启动，正在监听端口 {PORT}...")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n服务器已停止")
        sys.exit(0)
    except OSError as e:
        print(f"\n错误: 无法启动服务器 - {e}")
        print(f"端口 {PORT} 可能已被占用，请检查是否有其他程序在使用该端口")
        sys.exit(1)

if __name__ == "__main__":
    main()
