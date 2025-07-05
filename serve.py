#!/usr/bin/env python3
import http.server
import socketserver
import webbrowser
import os
import threading
import time
import subprocess
import sys
import signal
import socket

HTML_PORT = 8010
CACHE_PORT = 8012

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def start_html_server():
    """启动HTML服务器"""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", HTML_PORT), CORSHTTPRequestHandler) as httpd:
        print(f"HTML服务器启动在端口 {HTML_PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nHTML服务器已停止")

def start_cache_server():
    """启动缓存服务器"""
    import cache_server
    cache_server.start_server()

def kill_port(port):
    """杀死占用指定端口的进程"""
    try:
        # 尝试连接端口，如果连接成功说明端口被占用
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print(f"端口 {port} 被占用，正在清理...")
            # 使用fuser命令杀死占用端口的进程
            subprocess.run(['fuser', '-k', f'{port}/tcp'], 
                         capture_output=True, text=True)
            time.sleep(1)
    except Exception as e:
        print(f"清理端口 {port} 时出错: {e}")

def start_servers():
    """启动所有服务器"""
    print("正在启动服务器...")
    
    # 清理端口
    print("检查并清理端口...")
    kill_port(HTML_PORT)
    kill_port(CACHE_PORT)
    
    # 启动缓存服务器线程
    cache_thread = threading.Thread(target=start_cache_server, daemon=True)
    cache_thread.start()
    
    # 等待缓存服务器启动
    time.sleep(2)
    
    # 启动HTML服务器线程
    html_thread = threading.Thread(target=start_html_server, daemon=True)
    html_thread.start()
    
    # 等待HTML服务器启动
    time.sleep(1)
    
    print(f"\n所有服务器已启动:")
    print(f"  HTML服务器: http://localhost:{HTML_PORT}")
    print(f"  缓存服务器: http://localhost:{CACHE_PORT}")
    print(f"  访问页面: http://localhost:{HTML_PORT}/tree-visualization.html")
    print("按 Ctrl+C 停止所有服务器")
    
    # 自动打开浏览器
    try:
        webbrowser.open(f'http://localhost:{HTML_PORT}/tree-visualization.html')
    except:
        pass
    
    try:
        # 保持主线程运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n所有服务器已停止")

if __name__ == "__main__":
    start_servers() 