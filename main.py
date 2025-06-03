#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
主程序入口文件
作者: zhongqi.wang
"""

import sys
import os
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from frontend.views.main_window import MainWindow
from backend.services.project_manager import ProjectManager

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """
    主程序入口函数
    初始化应用程序并启动主窗口
    """
    try:
        # 创建QApplication实例
        app = QApplication(sys.argv)
        
        # 设置应用程序属性
        app.setAttribute(Qt.AA_EnableHighDpiScaling)  # 启用高DPI缩放
        app.setAttribute(Qt.AA_UseHighDpiPixmaps)     # 使用高DPI图标
        
        # 设置样式表
        with open('resources/styles/dark.qss', 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())
        
        # 创建项目管理器
        project_manager = ProjectManager()
        
        # 创建并显示主窗口
        main_window = MainWindow(project_manager)
        main_window.show()
        
        # 进入应用程序主循环
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"程序启动失败: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main() 