# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: 数据交换类.py
 @DateTime: 2024/9/12 10:15
 @SoftWare: PyCharm
"""


import ssl

def comparable(num1, num2):
    if num1 >= 0 and num2 >= 0:
        # 同为正数，保持不变
        return num1, num2
    elif num1 < 0 and num2 < 0:
        # 同为负数，交换位置
        return num2, num1
    else:
        # 异号，比较绝对值
        return (num1, num2) if abs(num1) > abs(num2) else (num2, num1)