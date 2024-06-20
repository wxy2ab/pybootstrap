from core import service_init
import socket
from core import logger

import re
import platform

def is_wsl():
    # 检查操作系统平台
    if platform.system().lower() != 'linux':
        return False
    # 尝试读取/proc/version文件
    try:
        with open('/proc/version', 'r') as f:
            content = f.read().lower()
        # 检查文件内容中是否包含'microsoft'字样
        return 'microsoft' in content
    except FileNotFoundError:
        return False
    
def is_socket_connected(host, port):
    try:
        # 创建一个 socket 对象并尝试连接
        with socket.create_connection((host, port), timeout=5) as sock:
            return True
    except (socket.timeout, ConnectionRefusedError):
        return False

@service_init
def check_proxy_running():
    # 要检查的地址和端口
    host_to_check = ''
    host_to_check_wsl = '192.168.50.104'
    #host_to_check_linux = '192.168.50.104'
    host_to_check_linux = '127.0.0.1'
    if is_wsl():
        host_to_check = host_to_check_wsl
    else:
        host_to_check = host_to_check_linux
    
    from core import Config
    config = Config()
    if config.has_key("proxy_host"):
        host_to_check = config.get("proxy_host")

    port_to_check = 10808
    if config.has_key("proxy_port"):
        port_to_check = int(config.get("proxy_port"))
    
    try:
        if is_socket_connected(host_to_check, port_to_check):
            import os
            os.environ["http_proxy"]  = f"socks5://{host_to_check}:{port_to_check}"
            os.environ["https_proxy"] = f"socks5://{host_to_check}:{port_to_check}"
            logger.info("连接到代理")
        else:
            logger.warning("没有代理服务器")
    except Exception as e:
        host_to_check = "127.0.0.1"
        import os
        os.environ["http_proxy"]  = f"socks5://{host_to_check}:10808"
        os.environ["https_proxy"] = f"socks5://{host_to_check}:10808"
        logger.info("连接到代理")
