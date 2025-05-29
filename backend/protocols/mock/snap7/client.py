#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Client:
    """模拟S7客户端"""
    
    def __init__(self):
        """初始化客户端"""
        self.ip = None
        self.rack = None
        self.slot = None
        self.connected = False
        self.last_values = {}
        logger.info("创建S7模拟客户端")
    
    def set_connection_params(self, ip, rack, slot):
        """设置连接参数
        
        Args:
            ip (str): IP地址
            rack (int): 机架号
            slot (int): 槽位号
        """
        self.ip = ip
        self.rack = rack
        self.slot = slot
        logger.info(f"设置S7连接参数: IP={ip}, 机架={rack}, 槽位={slot}")
    
    def connect(self):
        """连接到PLC
        
        Returns:
            bool: 是否成功连接
        """
        time.sleep(0.5)  # 模拟连接延迟
        self.connected = True
        logger.info(f"模拟连接到S7 PLC: {self.ip}")
        return True
    
    def disconnect(self):
        """断开连接"""
        self.connected = False
        logger.info(f"断开与S7 PLC的连接: {self.ip}")
    
    def get_connected(self):
        """检查是否已连接
        
        Returns:
            bool: 是否已连接
        """
        return self.connected
    
    def db_read(self, db_number, start, size):
        """读取数据块
        
        Args:
            db_number (int): 数据块号
            start (int): 起始地址
            size (int): 读取大小
            
        Returns:
            bytearray: 读取的数据
        """
        logger.info(f"模拟读取DB{db_number}.{start} (大小: {size})")
        key = f"DB{db_number}.{start}.{size}"
        
        if key in self.last_values and random.random() > 0.2:
            # 80%概率返回上次的值
            return self.last_values[key]
        
        # 生成随机数据
        data = bytearray(size)
        for i in range(size):
            data[i] = random.randint(0, 255)
        
        # 存储数据以供下次使用
        self.last_values[key] = data
        
        return data
    
    def db_write(self, db_number, start, data):
        """写入数据块
        
        Args:
            db_number (int): 数据块号
            start (int): 起始地址
            data (bytearray): 要写入的数据
        """
        logger.info(f"模拟写入DB{db_number}.{start} (大小: {len(data)})")
        key = f"DB{db_number}.{start}.{len(data)}"
        self.last_values[key] = data
    
    def read_area(self, area, dbnumber, start, size):
        """读取区域
        
        Args:
            area (int): 区域类型
            dbnumber (int): 数据块号
            start (int): 起始地址
            size (int): 读取大小
            
        Returns:
            bytearray: 读取的数据
        """
        logger.info(f"模拟读取区域 {area} (DB: {dbnumber}, 起始: {start}, 大小: {size})")
        key = f"AREA{area}.{dbnumber}.{start}.{size}"
        
        if key in self.last_values and random.random() > 0.2:
            # 80%概率返回上次的值
            return self.last_values[key]
        
        # 生成随机数据
        data = bytearray(size)
        for i in range(size):
            data[i] = random.randint(0, 255)
        
        # 存储数据以供下次使用
        self.last_values[key] = data
        
        return data
    
    def write_area(self, area, dbnumber, start, data):
        """写入区域
        
        Args:
            area (int): 区域类型
            dbnumber (int): 数据块号
            start (int): 起始地址
            data (bytearray): 要写入的数据
        """
        logger.info(f"模拟写入区域 {area} (DB: {dbnumber}, 起始: {start}, 大小: {len(data)})")
        key = f"AREA{area}.{dbnumber}.{start}.{len(data)}"
        self.last_values[key] = data 