from client import FileTransferGUI
from server import ServerManager

def main():
    # 创建服务器管理器
    server_manager = ServerManager()
    
    # 创建Tkinter根窗口
    root = None
    try:
        import tkinter as tk
        root = tk.Tk()
    except ImportError:
        print("错误: 无法导入Tkinter。请确保您的Python环境支持GUI。")
        return
    
    # 创建文件传输应用GUI
    app = FileTransferGUI(root, server_manager)
    
    # 运行应用
    app.run()

if __name__ == "__main__":
    main()
