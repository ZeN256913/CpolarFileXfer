# CpolarFileXfer - 安全高效的跨平台文件传输工具

![GitHub release](https://img.shields.io/github/v/release/Zen256913/CpolarFileXfer)
![GitHub license](https://img.shields.io/github/license/Zen256913/CpolarFileXfer)
![GitHub stars](https://img.shields.io/github/stars/Zen256913/CpolarFileXfer)
![GitHub forks](https://img.shields.io/github/forks/Zen256913/CpolarFileXfer)

CpolarFileXfer 是一个基于 Flask 和 Tkinter 的跨平台文件传输工具，支持局域网和公网文件共享，提供简洁美观的用户界面和安全可靠的传输体验。

## 主要功能

- **跨平台支持**：Windows、macOS、Linux 全平台兼容
- **局域网传输**：高速稳定的本地网络文件共享
- **公网访问**：集成 cpolar 实现外网穿透，随时随地访问文件
- **简洁界面**：美观易用的图形界面，操作简单直观
- **安全传输**：支持文件加密，保护隐私安全
- **多文件管理**：支持批量上传、下载和删除文件

## 技术栈

- **前端**：HTML5、CSS3、JavaScript、Tailwind CSS
- **后端**：Python Flask
- **GUI**：Python Tkinter
- **网络**：Socket、HTTP/HTTPS
- **部署**：cpolar（外网穿透）

## 安装指南

### 依赖环境

- Python 3.8+
- Flask 2.0+
- Tkinter (Python GUI 库)
- cpolar (可选，用于外网访问)

### 安装步骤

1. 克隆项目到本地：

```bash
git clone https://github.com/Zen256913/CpolarFileXfer.git
cd CpolarFileXfer
