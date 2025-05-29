#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
修复Python文件中的空字节问题
"""

import os

def fix_file(file_path):
    """修复文件中的空字节问题
    
    Args:
        file_path: 文件路径
    """
    try:
        # 读取文件内容
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # 检查是否包含空字节
        if b'\x00' in content:
            # 移除空字节
            content = content.replace(b'\x00', b'')
            
            # 写回文件
            with open(file_path, 'wb') as f:
                f.write(content)
            
            print(f"已修复文件: {file_path}")
            return True
        else:
            # 文件没有空字节
            print(f"文件正常: {file_path}")
            return False
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {str(e)}")
        return False

def fix_directory(directory):
    """递归修复目录中的所有Python文件
    
    Args:
        directory: 目录路径
    """
    fixed_count = 0
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if fix_file(file_path):
                    fixed_count += 1
    
    return fixed_count

if __name__ == "__main__":
    # 修复frontend目录下的所有Python文件
    fixed_count = fix_directory('frontend')
    
    print(f"共修复了 {fixed_count} 个文件") 