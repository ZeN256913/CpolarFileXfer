import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import threading
import os
import socket as socket_module  # 重命名socket模块导入，避免命名冲突
import time
import subprocess
import re
import sys

class FileTransferGUI:
    """文件互传应用的图形用户界面"""
    
    def __init__(self, root, server_manager):
        """初始化GUI界面"""
        self.root = root
        self.server_manager = server_manager
        self.root.title("文件互传应用 - 发送端")
        self.root.geometry("700x600")
        
        # 设置微软雅黑字体
        self.font_family = "微软雅黑"
        
        # 存储文件信息的列表
        self.shared_files = []
        
        # cpolar状态
        self.cpolar_running = False
        self.cpolar_thread = None
        self.cpolar_public_url = ""
        
        # 获取本机IP
        self.local_ip = self.get_local_ip()
        
        # 检查cpolar是否安装
        self.cpolar_installed = self.check_cpolar_installed()
        
        self.create_widgets()
        
        # 连接服务器管理器的回调
        self.server_manager.set_file_list_callback(self.update_file_list)
    
    def get_local_ip(self):
        """获取本机IP地址"""
        try:
            # 使用重命名后的socket模块
            s = socket_module.socket(socket_module.AF_INET, socket_module.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception as e:
            print(f"获取IP失败: {e}")
            return "127.0.0.1"
    
    def check_cpolar_installed(self):
        """检查cpolar是否安装"""
        try:
            # 尝试运行cpolar命令检查版本
            result = subprocess.run(['cpolar', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                return True
            return False
        except FileNotFoundError:
            return False
    
    def create_widgets(self):
        """创建Tkinter界面组件"""
        # 创建选项卡
        tab_control = ttk.Notebook(self.root)
        
        # 文件共享选项卡
        file_tab = ttk.Frame(tab_control)
        tab_control.add(file_tab, text="文件共享")
        
        # cpolar选项卡
        cpolar_tab = ttk.Frame(tab_control)
        tab_control.add(cpolar_tab, text="内网穿透 (cpolar)")
        
        tab_control.pack(expand=1, fill="both")
        
        # ===== 文件共享选项卡内容 =====
        # 标题
        title_label = tk.Label(file_tab, text="文件互传应用 - 发送端", font=(self.font_family, 16))
        title_label.pack(pady=10)
        
        # IP和端口信息
        info_frame = tk.Frame(file_tab)
        info_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ip_label = tk.Label(info_frame, text=f"本机IP: {self.local_ip}", font=(self.font_family, 10))
        ip_label.pack(side=tk.LEFT, padx=5)
        
        self.port_var = tk.StringVar(value="5000")
        port_label = tk.Label(info_frame, text="端口:", font=(self.font_family, 10))
        port_label.pack(side=tk.LEFT, padx=5)
        port_entry = tk.Entry(info_frame, textvariable=self.port_var, width=8, font=(self.font_family, 10))
        port_entry.pack(side=tk.LEFT, padx=5)
        
        # 服务器控制按钮
        control_frame = tk.Frame(file_tab)
        control_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.start_button = tk.Button(control_frame, text="启动服务器", command=self.start_server, font=(self.font_family, 10))
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(control_frame, text="停止服务器", command=self.stop_server, state=tk.DISABLED, font=(self.font_family, 10))
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # 操作按钮
        button_frame = tk.Frame(file_tab)
        button_frame.pack(fill=tk.X, padx=20, pady=5)
        
        add_file_button = tk.Button(button_frame, text="添加文件", command=self.add_file, font=(self.font_family, 10))
        add_file_button.pack(side=tk.LEFT, padx=5)
        
        add_folder_button = tk.Button(button_frame, text="添加文件夹", command=self.add_folder, font=(self.font_family, 10))
        add_folder_button.pack(side=tk.LEFT, padx=5)
        
        remove_button = tk.Button(button_frame, text="移除选中", command=self.remove_selected, font=(self.font_family, 10))
        remove_button.pack(side=tk.LEFT, padx=5)
        
        # 文件列表
        list_frame = tk.Frame(file_tab)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        columns = ("文件名", "大小", "路径")
        self.file_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # 设置列标题
        for col in columns:
            self.file_tree.heading(col, text=col)
            self.file_tree.column(col, width=100)
        
        # 调整列宽
        self.file_tree.column("文件名", width=200)
        self.file_tree.column("大小", width=100)
        self.file_tree.column("路径", width=250)
        
        # 设置Treeview字体
        style = ttk.Style()
        style.configure("Treeview", font=(self.font_family, 10))
        style.configure("Treeview.Heading", font=(self.font_family, 10, "bold"))
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)
        
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # ===== cpolar选项卡内容 =====
        cpolar_info_frame = tk.Frame(cpolar_tab)
        cpolar_info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # 显示cpolar安装状态
        if self.cpolar_installed:
            status_text = "已安装"
            status_color = "green"
        else:
            status_text = "未安装"
            status_color = "red"
        
        cpolar_status_label = tk.Label(cpolar_info_frame, text=f"cpolar状态: {status_text}", 
                                        font=(self.font_family, 10), fg=status_color)
        cpolar_status_label.pack(side=tk.LEFT, padx=5)
        
        # cpolar token输入
        token_frame = tk.Frame(cpolar_tab)
        token_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(token_frame, text="cpolar认证令牌:", font=(self.font_family, 10)).pack(side=tk.LEFT, padx=5)
        self.cpolar_token_var = tk.StringVar()
        token_entry = tk.Entry(token_frame, textvariable=self.cpolar_token_var, width=30, show="*", font=(self.font_family, 10))
        token_entry.pack(side=tk.LEFT, padx=5)
        
        # cpolar配置
        config_frame = tk.Frame(cpolar_tab)
        config_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(config_frame, text="内网地址:", font=(self.font_family, 10)).pack(side=tk.LEFT, padx=5)
        self.cpolar_local_addr_var = tk.StringVar(value=f"127.0.0.1:{self.port_var.get()}")
        local_addr_entry = tk.Entry(config_frame, textvariable=self.cpolar_local_addr_var, width=15, font=(self.font_family, 10))
        local_addr_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(config_frame, text="协议:", font=(self.font_family, 10)).pack(side=tk.LEFT, padx=5)
        self.cpolar_protocol_var = tk.StringVar(value="http")
        protocol_combo = ttk.Combobox(config_frame, textvariable=self.cpolar_protocol_var, values=["http", "https", "tcp", "tls"], width=8, font=(self.font_family, 10))
        protocol_combo.pack(side=tk.LEFT, padx=5)
        
        # cpolar控制按钮
        cpolar_control_frame = tk.Frame(cpolar_tab)
        cpolar_control_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.start_cpolar_button = tk.Button(cpolar_control_frame, text="启动内网穿透", command=self.start_cpolar, 
                                            state=tk.NORMAL if self.cpolar_installed else tk.DISABLED, 
                                            font=(self.font_family, 10))
        self.start_cpolar_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_cpolar_button = tk.Button(cpolar_control_frame, text="停止内网穿透", command=self.stop_cpolar, 
                                           state=tk.DISABLED, font=(self.font_family, 10))
        self.stop_cpolar_button.pack(side=tk.LEFT, padx=5)
        
        # 公网地址显示
        url_frame = tk.Frame(cpolar_tab)
        url_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(url_frame, text="公网访问地址:", font=(self.font_family, 10)).pack(side=tk.LEFT, padx=5)
        self.cpolar_url_var = tk.StringVar(value="未启动")
        url_label = tk.Label(url_frame, textvariable=self.cpolar_url_var, font=(self.font_family, 10, "bold"), fg="blue")
        url_label.pack(side=tk.LEFT, padx=5)
        
        copy_button = tk.Button(url_frame, text="复制", command=self.copy_url, font=(self.font_family, 10))
        copy_button.pack(side=tk.LEFT, padx=5)
        
        # cpolar日志显示
        log_frame = tk.Frame(cpolar_tab)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        tk.Label(log_frame, text="cpolar日志:", font=(self.font_family, 10)).pack(anchor=tk.W, pady=2)
        
        self.cpolar_log = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=80, height=15, font=(self.font_family, 9))
        self.cpolar_log.pack(fill=tk.BOTH, expand=True)
        
        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        status_label = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, font=(self.font_family, 10))
        status_label.pack(side=tk.BOTTOM, fill=tk.X)
    
    def add_file(self):
        """添加单个文件到共享列表"""
        file_path = filedialog.askopenfilename()
        if file_path:
            self.add_file_to_list(file_path)
            self.status_var.set(f"已添加文件: {os.path.basename(file_path)}")
    
    def add_folder(self):
        """添加文件夹中的所有文件到共享列表"""
        folder_path = filedialog.askdirectory()
        if folder_path:
            files_added = 0
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    self.add_file_to_list(file_path)
                    files_added += 1
            self.status_var.set(f"已添加 {files_added} 个文件")
    
    def add_file_to_list(self, file_path):
        """将文件添加到列表和共享文件列表中"""
        if not os.path.exists(file_path):
            return
        
        file_name = os.path.basename(file_path)
        file_size = self.format_size(os.path.getsize(file_path))
        
        # 添加到Treeview
        self.file_tree.insert("", tk.END, values=(file_name, file_size, file_path))
        
        # 添加到共享文件列表
        file_info = {
            "name": file_name,
            "size": file_size,
            "path": file_path
        }
        self.shared_files.append(file_info)
        
        # 更新服务器文件列表
        self.server_manager.update_file_list(self.shared_files)
    
    def remove_selected(self):
        """移除选中的文件"""
        selected_items = self.file_tree.selection()
        if not selected_items:
            return
        
        for item in selected_items:
            values = self.file_tree.item(item, "values")
            file_path = values[2]
            
            # 从共享文件列表中移除
            for i, file_info in enumerate(self.shared_files):
                if file_info["path"] == file_path:
                    self.shared_files.pop(i)
                    break
            
            # 从Treeview中移除
            self.file_tree.delete(item)
        
        # 更新服务器文件列表
        self.server_manager.update_file_list(self.shared_files)
    
    def update_file_list(self, file_list):
        """更新文件列表显示"""
        # 清空现有列表
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # 添加新的文件列表
        for file_info in file_list:
            self.file_tree.insert("", tk.END, values=(
                file_info["name"],
                file_info["size"],
                file_info["path"]
            ))
        
        # 更新本地文件列表
        self.shared_files = file_list
    
    def format_size(self, size_bytes):
        """格式化文件大小显示"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
    
    def start_server(self):
        """启动Flask服务器"""
        try:
            port = int(self.port_var.get())
        except ValueError:
            messagebox.showerror("错误", "端口必须是数字")
            return
        
        # 更新cpolar内网地址
        self.cpolar_local_addr_var.set(f"127.0.0.1:{port}")
        
        # 启动服务器
        success = self.server_manager.start_server(port, self.shared_files)
        if success:
            self.status_var.set(f"服务器已启动在 http://{self.local_ip}:{port}")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
        else:
            messagebox.showerror("错误", "无法启动服务器")
    
    def stop_server(self):
        """停止Flask服务器"""
        self.server_manager.stop_server()
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("服务器已停止")
        
        # 如果cpolar正在运行，也停止它
        if self.cpolar_running:
            self.stop_cpolar()
    
    def start_cpolar(self):
        """启动cpolar内网穿透"""
        if not self.cpolar_installed:
            messagebox.showerror("错误", "未检测到cpolar安装，请先安装cpolar")
            return
        
        if not self.server_manager.is_server_running():
            messagebox.showwarning("警告", "Flask服务器未启动，将自动启动")
            self.start_server()
            time.sleep(1)  # 等待服务器启动
            
            if not self.server_manager.is_server_running():
                return
        
        token = self.cpolar_token_var.get().strip()
        if not token:
            messagebox.showerror("错误", "请输入cpolar认证令牌")
            return
        
        # 配置cpolar
        try:
            # 设置认证令牌
            subprocess.run(['cpolar', 'authtoken', token], check=True, capture_output=True)
            
            # 启动cpolar
            self.cpolar_running = True
            self.start_cpolar_button.config(state=tk.DISABLED)
            self.stop_cpolar_button.config(state=tk.NORMAL)
            
            self.cpolar_thread = threading.Thread(
                target=self.run_cpolar,
                daemon=True
            )
            self.cpolar_thread.start()
            
            self.status_var.set("正在启动cpolar内网穿透...")
            self.cpolar_log.delete(1.0, tk.END)
            self.cpolar_log.insert(tk.END, "正在启动cpolar...\n")
            self.cpolar_log.see(tk.END)
            
        except subprocess.CalledProcessError as e:
            messagebox.showerror("错误", f"cpolar配置失败: {e.stderr.decode()}")
    
    def run_cpolar(self):
        """运行cpolar进程"""
        try:
            protocol = self.cpolar_protocol_var.get()
            local_addr = self.cpolar_local_addr_var.get()
            
            # 启动cpolar进程，指定UTF-8编码
            cpolar_process = subprocess.Popen(
                ['cpolar', protocol, local_addr],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=False  # 使用二进制模式读取输出
            )
            
            # 读取输出并更新UI
            while self.cpolar_running and cpolar_process.poll() is None:
                try:
                    line = cpolar_process.stdout.readline()
                    if not line:
                        break
                    
                    # 尝试使用UTF-8解码，如果失败则使用系统默认编码
                    try:
                        decoded_line = line.decode('utf-8')
                    except UnicodeDecodeError:
                        # 尝试使用系统默认编码
                        decoded_line = line.decode(sys.getdefaultencoding(), errors='replace')
                    
                    # 更新日志
                    self.root.after(0, lambda l=decoded_line: self.update_cpolar_log(l))
                    
                    # 提取公网地址
                    if 'Forwarding' in decoded_line:
                        match = re.search(r'https?://[^\s]+', decoded_line)
                        if match:
                            public_url = match.group(0)
                            self.root.after(0, lambda url=public_url: self.update_cpolar_url(url))
                except Exception as e:
                    # 捕获并记录读取错误
                    self.root.after(0, lambda: self.update_cpolar_log(f"读取错误: {str(e)}\n"))
            
            # 进程结束
            self.root.after(0, self.cpolar_stopped)
            
        except Exception as e:
            self.root.after(0, lambda: self.update_cpolar_log(f"错误: {str(e)}\n"))
            self.root.after(0, self.cpolar_stopped)
    
    def update_cpolar_log(self, line):
        """更新cpolar日志"""
        self.cpolar_log.insert(tk.END, line)
        self.cpolar_log.see(tk.END)
    
    def update_cpolar_url(self, url):
        """更新cpolar公网地址"""
        self.cpolar_public_url = url
        self.cpolar_url_var.set(url)
        self.status_var.set(f"cpolar已启动，公网地址: {url}")
    
    def cpolar_stopped(self):
        """处理cpolar停止事件"""
        if self.cpolar_running:
            self.cpolar_running = False
            self.start_cpolar_button.config(state=tk.NORMAL)
            self.stop_cpolar_button.config(state=tk.DISABLED)
            self.cpolar_url_var.set("未启动")
            self.status_var.set("cpolar已停止")
    
    def stop_cpolar(self):
        """停止cpolar内网穿透"""
        if not self.cpolar_running:
            return
        
        try:
            # 尝试终止cpolar进程
            subprocess.run(['cpolar', 'kill'], check=True)
            self.cpolar_stopped()
        except Exception as e:
            messagebox.showerror("错误", f"停止cpolar失败: {str(e)}")
    
    def copy_url(self):
        """复制公网地址到剪贴板"""
        if self.cpolar_public_url:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.cpolar_public_url)
            self.status_var.set("公网地址已复制到剪贴板")
        else:
            messagebox.showinfo("提示", "没有可用的公网地址")