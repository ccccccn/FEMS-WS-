#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
修复variable_view.py文件中的缩进问题
"""

def fix_indent_issue():
    """修复variable_view.py文件中的缩进问题"""
    file_path = 'frontend/views/variable_view.py'
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.readlines()
    
    # 修复edit_variable_wrapper方法
    edit_wrapper_fixed = fix_method(content, 'edit_variable_wrapper')
    
    # 修复delete_variable_wrapper方法
    delete_wrapper_fixed = fix_method(content, 'delete_variable_wrapper')
    
    if edit_wrapper_fixed or delete_wrapper_fixed:
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(content)
        
        print(f"已修复 {file_path} 中的缩进问题")
        return True
    else:
        print(f"未找到需要修复的方法或方法已正确缩进")
        return False

def fix_method(content, method_name):
    """修复指定方法的缩进问题"""
    in_method = False
    method_start = -1
    method_end = -1
    
    # 查找方法
    for i, line in enumerate(content):
        if f'def {method_name}' in line:
            in_method = True
            method_start = i
        elif in_method and line.strip() == '' and i > method_start + 3:  # 确保不会过早结束
            method_end = i
            break
    
    if method_start != -1 and method_end != -1:
        # 提取方法体
        method_body = content[method_start:method_end]
        
        # 检查是否存在缩进问题
        has_indent_issue = False
        for line in method_body:
            if 'selected_indexes' in line and not line.startswith('        '):
                has_indent_issue = True
                break
        
        if has_indent_issue:
            # 创建正确缩进的方法体
            if method_name == 'edit_variable_wrapper':
                correct_method = [
                    '    def edit_variable_wrapper(self):\n',
                    '        """Wrapper method for edit_variable_btn.clicked signal to prevent boolean value being passed to edit_variable method."""\n',
                    '        selected_indexes = self.variable_table.selectionModel().selectedRows()\n',
                    '        \n',
                    '        if selected_indexes:\n',
                    '            row = selected_indexes[0].row()\n',
                    '            variable = self.variable_model.get_variable(row)\n',
                    '            \n',
                    '            if variable:\n',
                    '                self.edit_variable(variable)\n',
                    '    \n'
                ]
            else:  # delete_variable_wrapper
                correct_method = [
                    '    def delete_variable_wrapper(self):\n',
                    '        """Wrapper method for delete_variable_btn.clicked signal to prevent boolean value being passed to delete_variable method."""\n',
                    '        selected_indexes = self.variable_table.selectionModel().selectedRows()\n',
                    '        \n',
                    '        if selected_indexes:\n',
                    '            row = selected_indexes[0].row()\n',
                    '            variable = self.variable_model.get_variable(row)\n',
                    '            \n',
                    '            if variable:\n',
                    '                self.delete_variable(variable)\n',
                    '    \n'
                ]
            
            # 替换内容
            content[method_start:method_end] = correct_method
            print(f"已修复 {method_name} 方法")
            return True
        else:
            print(f"{method_name} 方法缩进正确，无需修复")
            return False
    else:
        print(f"未找到 {method_name} 方法")
        return False

if __name__ == "__main__":
    fix_indent_issue() 