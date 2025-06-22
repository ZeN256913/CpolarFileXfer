import os
import threading
from flask import Flask, render_template, send_file, jsonify
import socket
import time
import requests

class ServerManager:
    def __init__(self):
        # 创建Flask应用
        self.flask_app = Flask(__name__, template_folder='templates')
        self.setup_flask_routes()
        
        # 服务器状态
        self.server_running = False
        self.server_thread = None
        self.port = 5000
        self.local_ip = "127.0.0.1"
        
        # 文件列表
        self.shared_files = []
        
        # 回调函数
        self.file_list_callback = None
    
    def setup_flask_routes(self):
        """设置Flask路由"""
        @self.flask_app.route('/')
        def index():
            """主页，显示可下载的文件列表"""
            return render_template('index.html', files=self.shared_files, ip=self.local_ip)
        
        @self.flask_app.route('/download/<int:file_index>')
        def download(file_index):
            """下载文件"""
            if 0 <= file_index < len(self.shared_files):
                file_path = self.shared_files[file_index]["path"]
                if os.path.exists(file_path):
                    return send_file(file_path, as_attachment=True)
            return "文件不存在", 404
        
        @self.flask_app.route('/api/files')
        def get_files():
            """获取文件列表API"""
            return jsonify(self.shared_files)
    
    def set_file_list_callback(self, callback):
        """设置文件列表更新回调函数"""
        self.file_list_callback = callback
    
    def update_files(self, files):
        """更新共享文件列表"""
        self.shared_files = files
        if self.file_list_callback:
            self.file_list_callback(files)
    
    def is_running(self):
        """检查服务器是否正在运行"""
        return self.server_running
    
    def start(self, port, files, local_ip):
        """启动Flask服务器"""
        if self.server_running:
            return
        
        self.port = port
        self.local_ip = local_ip
        self.shared_files = files
        
        # 启动Flask服务器线程
        self.server_running = True
        self.server_thread = threading.Thread(
            target=self.run_flask_server,
            daemon=True
        )
        self.server_thread.start()
        
        # 等待服务器启动
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                requests.get(f"http://{local_ip}:{port}", timeout=1)
                break
            except:
                if attempt == max_attempts - 1:
                    raise Exception("服务器启动超时")
                time.sleep(0.5)
    
    def run_flask_server(self):
        """运行Flask服务器"""
        try:
            self.flask_app.run(host='0.0.0.0', port=self.port, debug=False)
        except Exception as e:
            print(f"服务器错误: {e}")
            self.server_running = False
    
    def stop(self):
        """停止Flask服务器"""
        if not self.server_running:
            return
        
        self.server_running = False
        
        # 发送关闭请求到Flask服务器
        try:
            requests.get(f"http://{self.local_ip}:{self.port}/shutdown", timeout=1)
        except:
            pass
