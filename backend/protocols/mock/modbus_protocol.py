#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import random
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class ModbusProtocol:
    """模拟Modbus协议实现"""
    
    def __init__(self, settings):
        """初始化Modbus协议处理器。
        
        Args:
            settings (dict): 连接设置
        """
        self.settings = settings
        self.connected = False
        self.last_values = {}
        
        # 记录设置
        if self.settings.get('type') == 'TCP':
            logger.info(f"创建Modbus TCP模拟协议实例，IP={settings.get('ip', '127.0.0.1')}:{settings.get('port', 502)}")
        else:
            logger.info(f"创建Modbus RTU模拟协议实例，端口={settings.get('port', 'COM1')}")
    
    def connect(self):
        """连接到Modbus设备。"""
        try:
            # 模拟连接延迟
            time.sleep(0.2)
            self.connected = True
            
            if self.settings.get('type') == 'TCP':
                logger.info(f"连接到Modbus TCP设备，IP={self.settings.get('ip', '127.0.0.1')}:{self.settings.get('port', 502)}")
            else:
                logger.info(f"连接到Modbus RTU设备，端口={self.settings.get('port', 'COM1')}")
            
            return True
        except Exception as e:
            logger.error(f"连接Modbus设备失败: {str(e)}")
            return False
    
    def disconnect(self):
        """断开与Modbus设备的连接。"""
        if self.connected:
            self.connected = False
            logger.info("断开与Modbus设备的连接")
            return True
        return True
    
    def read_variable(self, variable):
        """从Modbus设备读取变量。
        
        Args:
            variable (dict): 包含以下键的变量信息：
                - data_type: 数据类型 (BOOL, BYTE, WORD, DWORD, INT, DINT, REAL, STRING)
                - address: Modbus地址 (例如，40001, 10001, 30001, 00001)
                - size: 要读取的寄存器数量（对于多寄存器数据类型）
        
        Returns:
            tuple: (value, status)
                - value: 读取的值
                - status: 如果成功则为True，否则为False
        """
        if not self.connected:
            logger.error("无法读取变量: 未连接到Modbus设备")
            return None, False
        
        try:
            data_type = variable.get('data_type')
            address = variable.get('address')
            
            if not data_type or not address:
                logger.error("缺少数据类型或地址")
                return None, False
            
            # 转换字符串地址为整数（如果需要）
            if isinstance(address, str):
                try:
                    address = int(address)
                except ValueError:
                    logger.error(f"无效的地址格式: {address}")
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
        """向Modbus设备中的变量写入值。
        
        Args:
            variable (dict): 包含以下键的变量信息：
                - data_type: 数据类型 (BOOL, BYTE, WORD, DWORD, INT, DINT, REAL, STRING)
                - address: Modbus地址 (例如，40001, 10001, 30001, 00001)
            value: 要写入的值
        
        Returns:
            bool: 如果成功则为True，否则为False
        """
        if not self.connected:
            logger.error("无法写入变量: 未连接到Modbus设备")
            return False
        
        try:
            data_type = variable.get('data_type')
            address = variable.get('address')
            
            if not data_type or not address:
                logger.error("缺少数据类型或地址")
                return False
            
            # 转换字符串地址为整数（如果需要）
            if isinstance(address, str):
                try:
                    address = int(address)
                except ValueError:
                    logger.error(f"无效的地址格式: {address}")
                    return False
            
            # 生成唯一键
            key = f"{data_type}_{address}"
            
            # 存储值
            self.last_values[key] = value
            
            logger.info(f"写入变量 {address} = {value}")
            return True
                
        except Exception as e:
            logger.error(f"写入变量时出错: {str(e)}")
            return False 