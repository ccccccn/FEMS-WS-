#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 区域类型
areas = type('Areas', (), {
    'PE': 0x81,  # 输入区
    'PA': 0x82,  # 输出区
    'MK': 0x83,  # 内存区
    'DB': 0x84,  # 数据块
    'CT': 0x1C,  # 计数器
    'TM': 0x1D   # 定时器
})() 