#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import random
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class S7Protocol:
    """模拟S7协议实现"""
    
    def __init__(self, ip, rack=0, slot=1, timeout=5, pdu_size=480):
        """初始化S7协议处理器。
        
        Args:
            ip (str): PLC的IP地址
            rack (int): 机架号 (默认: 0)
            slot (int): 槽位号 (默认: 1)
            timeout (int): 连接超时时间，单位秒 (默认: 5)
            pdu_size (int): PDU大小 (默认: 480)
        """
        self.ip = ip
        self.rack = rack
        self.slot = slot
        self.timeout = timeout
        self.pdu_size = int(pdu_size)
        self.client = None
        self.connected = False
        self.last_values = {}
    
    def connect(self):
        """连接到S7 PLC。"""
        try:
            # 模拟连接延迟
            time.sleep(0.2)
            self.connected = True
            return True
        except Exception as e:
            logger.error(f"连接S7 PLC失败: {str(e)}")
            return False
    
    def disconnect(self):
        """断开与S7 PLC的连接。"""
        if self.connected:
            self.connected = False
            return True
        return True
    
    def read_variable(self, variable):
        """从PLC读取变量。
        
        Args:
            variable (dict): 包含以下键的变量信息：
                - data_type: 数据类型 (BOOL, BYTE, WORD, DWORD, INT, DINT, REAL, STRING)
                - address: S7格式的地址 (例如，DB1.DBX0.0, M10.0, I0.1, Q0.1)
        
        Returns:
            tuple: (value, status) 
                - value: 读取的值
                - status: 如果成功则为True，否则为False
        """
        if not self.connected:
            return None, False
        
        try:
            data_type = variable.get('data_type')
            address = variable.get('address')
            
            if not data_type or not address:
                return None, False
            
            # 生成唯一键
            key = f"{data_type}_{address}"
            
            # 如果有上次的值且随机数大于0.2，则返回上次的值（80%概率）
            if key in self.last_values and random.random() > 0.2:
                return self.last_values[key], True
            
            # 根据数据类型生成随机值
            value = None
            if data_type == 'BOOL':
                value = random.choice([True, False])
            elif data_type in ['BYTE', 'WORD', 'INT']:
                value = random.randint(0, 32767)
            elif data_type in ['DWORD', 'DINT']:
                value = random.randint(-2147483648, 2147483647)
            elif data_type == 'REAL':
                value = round(random.uniform(0, 100), 2)
            elif data_type == 'STRING':
                sample_strings = ["正常", "运行中", "已停止", "故障", "待机", "维护中"]
                value = random.choice(sample_strings)
            else:
                value = 0
            
            # 存储值以供下次使用
            self.last_values[key] = value
            
            return value, True
                
        except Exception as e:
            logger.error(f"读取变量时出错: {str(e)}")
            return None, False
    
    def write_variable(self, variable, value):
        """向PLC中的变量写入值。
        
        Args:
            variable (dict): 包含以下键的变量信息：
                - data_type: 数据类型 (BOOL, BYTE, WORD, DWORD, INT, DINT, REAL, STRING)
                - address: S7格式的地址 (例如，DB1.DBX0.0, M10.0, Q0.1)
            value: 要写入的值
        
        Returns:
            bool: 如果成功则为True，否则为False
        """
        if not self.connected:
            return False
        
        try:
            data_type = variable.get('data_type')
            address = variable.get('address')
            
            if not data_type or not address:
                return False
            
            # 生成唯一键
            key = f"{data_type}_{address}"
            
            # 存储值
            self.last_values[key] = value
            
            return True
                
        except Exception as e:
            logger.error(f"写入变量时出错: {str(e)}")
            return False 