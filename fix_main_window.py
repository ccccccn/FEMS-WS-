#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
修复main_window.py文件中的空字节问题
"""

def fix_file():
    """修复文件中的空字节问题"""
    file_path = 'frontend/views/main_window.py'
    
    try:
        # 读取文件内容
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # 移除空字节
        content = content.replace(b'\x00', b'')
        
        # 写回文件
        with open(file_path, 'wb') as f:
            f.write(content)
        
        print(f"已修复文件: {file_path}")
        return True
    except Exception as e:
        print(f"修复文件时出错: {str(e)}")
        return False

if __name__ == "__main__":
    fix_file() 