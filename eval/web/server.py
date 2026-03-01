#!/usr/bin/env python3
"""
LLM 评测报告 Web 服务器
提供静态文件服务，监听 0.0.0.0:9820
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

PORT = 9820
HOST = "0.0.0.0"

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent), **kwargs)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[{self.log_date_time_string()}] {args[0]}")

def run_server():
    """启动 HTTP 服务器"""
    web_dir = Path(__file__).parent
    os.chdir(web_dir)

    with socketserver.TCPServer((HOST, PORT), MyHTTPRequestHandler) as httpd:
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║           LLM 评测报告 Web 服务器已启动                        ║
╠══════════════════════════════════════════════════════════════╣
║  访问地址: http://{HOST}:{PORT}                              ║
║  服务目录: {web_dir}
║  可用页面:                                                    ║
║    - 概览:      http://{HOST}:{PORT}/index.html              ║
║    - Stage 1:   http://{HOST}:{PORT}/stage1.html             ║
║    - Stage 2:   http://{HOST}:{PORT}/stage2.html             ║
║    - Stage 3:   http://{HOST}:{PORT}/stage3.html             ║
║    - 测试规范:  http://{HOST}:{PORT}/methodology.html        ║
╚══════════════════════════════════════════════════════════════╝
按 Ctrl+C 停止服务器
        """)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n服务器已停止")
            sys.exit(0)

if __name__ == "__main__":
    run_server()
