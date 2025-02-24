# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: run_server.py
 @DateTime: 2025-02-07 9:00
 @SoftWare: PyCharm
"""
import uvicorn
import sys
import signal
from django.core.management import call_command

def handle_shutdown(signal, frame):
    print("Shutting down gracefully...")
    # 在这里可以执行一些清理操作，例如关闭数据库连接等
    sys.exit(0)

if __name__ == "__main__":
    # 注册信号处理函数
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    # 启动 Uvicorn
    uvicorn.run("taosPro.asgi:application", host="192.168.102.75", port=10000, reload=True)