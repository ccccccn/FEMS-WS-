#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import time

class ModbusTcpClient:
    """模拟Modbus TCP客户端"""
    
    def __init__(self, host='localhost', port=502, **kwargs):
        """初始化客户端
        
        Args:
            host (str): 主机地址
            port (int): 端口号
            **kwargs: 其他参数
        """
        self.host = host
        self.port = port
        self.connected = False
        self.last_values = {}
    
    def connect(self):
        """连接到服务器
        
        Returns:
            bool: 是否成功连接
        """
        time.sleep(0.5)  # 模拟连接延迟
        self.connected = True
        return True
    
    def close(self):
        """关闭连接"""
        self.connected = False
    
    def is_socket_open(self):
        """检查连接是否打开
        
        Returns:
            bool: 连接是否打开
        """
        return self.connected
    
    def read_coils(self, address, count=1, unit=1):
        """读取线圈
        
        Args:
            address (int): 起始地址
            count (int): 数量
            unit (int): 从站地址
        
        Returns:
            ModbusResponse: 响应对象
        """
        return self._create_response('coils', address, count)
    
    def read_discrete_inputs(self, address, count=1, unit=1):
        """读取离散输入
        
        Args:
            address (int): 起始地址
            count (int): 数量
            unit (int): 从站地址
        
        Returns:
            ModbusResponse: 响应对象
        """
        return self._create_response('discrete_inputs', address, count)
    
    def read_holding_registers(self, address, count=1, unit=1):
        """读取保持寄存器
        
        Args:
            address (int): 起始地址
            count (int): 数量
            unit (int): 从站地址
        
        Returns:
            ModbusResponse: 响应对象
        """
        return self._create_response('holding_registers', address, count)
    
    def read_input_registers(self, address, count=1, unit=1):
        """读取输入寄存器
        
        Args:
            address (int): 起始地址
            count (int): 数量
            unit (int): 从站地址
        
        Returns:
            ModbusResponse: 响应对象
        """
        return self._create_response('input_registers', address, count)
    
    def write_coil(self, address, value, unit=1):
        """写入线圈
        
        Args:
            address (int): 地址
            value (bool): 值
            unit (int): 从站地址
        
        Returns:
            ModbusResponse: 响应对象
        """
        key = f"coils_{address}_1_{unit}"
        self.last_values[key] = [value]
        return ModbusResponse(True)
    
    def write_register(self, address, value, unit=1):
        """写入寄存器
        
        Args:
            address (int): 地址
            value (int): 值
            unit (int): 从站地址
        
        Returns:
            ModbusResponse: 响应对象
        """
        key = f"holding_registers_{address}_1_{unit}"
        self.last_values[key] = [value]
        return ModbusResponse(True)
    
    def write_registers(self, address, values, unit=1):
        """写入多个寄存器
        
        Args:
            address (int): 起始地址
            values (list): 值列表
            unit (int): 从站地址
        
        Returns:
            ModbusResponse: 响应对象
        """
        key = f"holding_registers_{address}_{len(values)}_{unit}"
        self.last_values[key] = values
        return ModbusResponse(True)
    
    def write_coils(self, address, values, unit=1):
        """写入多个线圈
        
        Args:
            address (int): 起始地址
            values (list): 值列表
            unit (int): 从站地址
        
        Returns:
            ModbusResponse: 响应对象
        """
        key = f"coils_{address}_{len(values)}_{unit}"
        self.last_values[key] = values
        return ModbusResponse(True)
    
    def _create_response(self, register_type, address, count, unit=1):
        """创建响应对象
        
        Args:
            register_type (str): 寄存器类型
            address (int): 起始地址
            count (int): 数量
            unit (int): 从站地址
        
        Returns:
            ModbusResponse: 响应对象
        """
        key = f"{register_type}_{address}_{count}_{unit}"
        
        if key in self.last_values and random.random() > 0.1:
            # 返回上次的值，但有10%的概率生成新值
            values = self.last_values[key]
        else:
            # 生成新的随机值
            if register_type in ['coils', 'discrete_inputs']:
                values = [random.choice([True, False]) for _ in range(count)]
            else:
                values = [random.randint(0, 65535) for _ in range(count)]
            
            # 存储值以供下次使用
            self.last_values[key] = values
        
        return ModbusResponse(values)

class ModbusResponse:
    """模拟Modbus响应"""
    
    def __init__(self, values, isError=False):
        """初始化响应
        
        Args:
            values (list): 值列表
            isError (bool): 是否为错误响应
        """
        self.values = values if isinstance(values, list) else [values]
        self.isError = isError
        
        # 模拟偶尔的通信问题
        if random.random() < 0.02:
            self.isError = True
    
    def getBit(self, index):
        """获取位值
        
        Args:
            index (int): 索引
        
        Returns:
            bool: 位值
        """
        if self.isError or index >= len(self.values):
            return False
        return bool(self.values[index])
    
    def getByte(self, index):
        """获取字节值
        
        Args:
            index (int): 索引
        
        Returns:
            int: 字节值
        """
        if self.isError or index >= len(self.values):
            return 0
        return self.values[index] & 0xFF
    
    def getRegister(self, index):
        """获取寄存器值
        
        Args:
            index (int): 索引
        
        Returns:
            int: 寄存器值
        """
        if self.isError or index >= len(self.values):
            return 0
        return self.values[index]
    
    def getRegisters(self):
        """获取所有寄存器值
        
        Returns:
            list: 寄存器值列表
        """
        if self.isError:
            return []
        return self.values
    
    def registers(self):
        """获取所有寄存器值
        
        Returns:
            list: 寄存器值列表
        """
        return self.getRegisters()
    
    def bits(self):
        """获取所有位值
        
        Returns:
            list: 位值列表
        """
        if self.isError:
            return []
        return self.values 