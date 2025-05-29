#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
启动脚本，使用模拟协议模式运行应用程序
"""

import os
import sys
import subprocess

if __name__ == "__main__":
    # 设置环境变量，启用模拟协议模式
    os.environ["USE_MOCK_PROTOCOLS"] = "1"
    
    print("启动应用程序，使用模拟协议模式...")
    
    # 运行主程序
    try:
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n程序已终止")
    except Exception as e:
        print(f"启动失败: {str(e)}") 