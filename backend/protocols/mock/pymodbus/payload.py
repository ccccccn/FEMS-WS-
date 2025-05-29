#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct
import random

class BinaryPayloadDecoder:
    """用于解码二进制负载的类"""
    
    def __init__(self, payload, byteorder='>', wordorder='>'):
        """初始化解码器
        
        Args:
            payload (bytes or list): 要解码的数据
            byteorder (str): 字节序 ('>' 大端, '<' 小端)
            wordorder (str): 字序 ('>' 大端, '<' 小端)
        """
        self.payload = payload
        self.byteorder = byteorder
        self.wordorder = wordorder
        self.pointer = 0
    
    @classmethod
    def fromRegisters(cls, registers, byteorder='>', wordorder='>'):
        """从寄存器列表创建解码器
        
        Args:
            registers (list): 寄存器列表
            byteorder (str): 字节序
            wordorder (str): 字序
            
        Returns:
            BinaryPayloadDecoder: 解码器实例
        """
        # 模拟实现，实际上只是存储寄存器列表
        return cls(registers, byteorder, wordorder)
    
    @classmethod
    def fromCoils(cls, coils, byteorder='>', wordorder='>'):
        """从线圈列表创建解码器
        
        Args:
            coils (list): 线圈列表
            byteorder (str): 字节序
            wordorder (str): 字序
            
        Returns:
            BinaryPayloadDecoder: 解码器实例
        """
        # 模拟实现，实际上只是存储线圈列表
        return cls(coils, byteorder, wordorder)
    
    def decode_8bit_uint(self):
        """解码8位无符号整数
        
        Returns:
            int: 8位无符号整数
        """
        # 模拟实现，随机生成值
        return random.randint(0, 255)
    
    def decode_16bit_uint(self):
        """解码16位无符号整数
        
        Returns:
            int: 16位无符号整数
        """
        # 如果有寄存器，返回第一个寄存器值
        if isinstance(self.payload, list) and len(self.payload) > 0:
            return self.payload[0]
        return random.randint(0, 65535)
    
    def decode_16bit_int(self):
        """解码16位有符号整数
        
        Returns:
            int: 16位有符号整数
        """
        # 如果有寄存器，返回第一个寄存器值（转换为有符号）
        if isinstance(self.payload, list) and len(self.payload) > 0:
            value = self.payload[0]
            # 转换为有符号
            if value > 32767:
                value -= 65536
            return value
        return random.randint(-32768, 32767)
    
    def decode_32bit_uint(self):
        """解码32位无符号整数
        
        Returns:
            int: 32位无符号整数
        """
        # 如果有足够的寄存器，组合它们
        if isinstance(self.payload, list) and len(self.payload) >= 2:
            if self.wordorder == '>':
                return (self.payload[0] << 16) | self.payload[1]
            else:
                return (self.payload[1] << 16) | self.payload[0]
        return random.randint(0, 4294967295)
    
    def decode_32bit_int(self):
        """解码32位有符号整数
        
        Returns:
            int: 32位有符号整数
        """
        value = self.decode_32bit_uint()
        # 转换为有符号
        if value > 2147483647:
            value -= 4294967296
        return value
    
    def decode_32bit_float(self):
        """解码32位浮点数
        
        Returns:
            float: 32位浮点数
        """
        # 模拟实现，随机生成浮点数
        return random.uniform(0, 100)
    
    def decode_64bit_uint(self):
        """解码64位无符号整数
        
        Returns:
            int: 64位无符号整数
        """
        # 模拟实现，随机生成值
        return random.randint(0, 18446744073709551615)
    
    def decode_64bit_int(self):
        """解码64位有符号整数
        
        Returns:
            int: 64位有符号整数
        """
        # 模拟实现，随机生成值
        return random.randint(-9223372036854775808, 9223372036854775807)
    
    def decode_64bit_float(self):
        """解码64位浮点数
        
        Returns:
            float: 64位浮点数
        """
        # 模拟实现，随机生成浮点数
        return random.uniform(0, 1000)
    
    def decode_string(self, size=None):
        """解码字符串
        
        Args:
            size (int): 字符串长度
            
        Returns:
            str: 字符串
        """
        # 模拟实现，随机生成字符串
        sample_strings = ["正常", "运行中", "已停止", "故障", "待机", "维护中"]
        return random.choice(sample_strings)
    
    def decode_bits(self):
        """解码位
        
        Returns:
            list: 位列表
        """
        # 模拟实现，随机生成位列表
        return [random.choice([True, False]) for _ in range(8)]

class BinaryPayloadBuilder:
    """用于构建二进制负载的类"""
    
    def __init__(self, byteorder='>', wordorder='>'):
        """初始化构建器
        
        Args:
            byteorder (str): 字节序 ('>' 大端, '<' 小端)
            wordorder (str): 字序 ('>' 大端, '<' 小端)
        """
        self.byteorder = byteorder
        self.wordorder = wordorder
        self.payload = []
    
    def add_8bit_uint(self, value):
        """添加8位无符号整数
        
        Args:
            value (int): 8位无符号整数
            
        Returns:
            BinaryPayloadBuilder: 自身
        """
        self.payload.append(value & 0xFF)
        return self
    
    def add_16bit_uint(self, value):
        """添加16位无符号整数
        
        Args:
            value (int): 16位无符号整数
            
        Returns:
            BinaryPayloadBuilder: 自身
        """
        self.payload.append(value & 0xFFFF)
        return self
    
    def add_16bit_int(self, value):
        """添加16位有符号整数
        
        Args:
            value (int): 16位有符号整数
            
        Returns:
            BinaryPayloadBuilder: 自身
        """
        # 转换为无符号
        if value < 0:
            value += 65536
        self.payload.append(value & 0xFFFF)
        return self
    
    def add_32bit_uint(self, value):
        """添加32位无符号整数
        
        Args:
            value (int): 32位无符号整数
            
        Returns:
            BinaryPayloadBuilder: 自身
        """
        if self.wordorder == '>':
            self.payload.append((value >> 16) & 0xFFFF)
            self.payload.append(value & 0xFFFF)
        else:
            self.payload.append(value & 0xFFFF)
            self.payload.append((value >> 16) & 0xFFFF)
        return self
    
    def add_32bit_int(self, value):
        """添加32位有符号整数
        
        Args:
            value (int): 32位有符号整数
            
        Returns:
            BinaryPayloadBuilder: 自身
        """
        # 转换为无符号
        if value < 0:
            value += 4294967296
        return self.add_32bit_uint(value)
    
    def add_32bit_float(self, value):
        """添加32位浮点数
        
        Args:
            value (float): 32位浮点数
            
        Returns:
            BinaryPayloadBuilder: 自身
        """
        # 模拟实现，只存储整数部分
        self.add_32bit_uint(int(value))
        return self
    
    def add_64bit_uint(self, value):
        """添加64位无符号整数
        
        Args:
            value (int): 64位无符号整数
            
        Returns:
            BinaryPayloadBuilder: 自身
        """
        if self.wordorder == '>':
            self.payload.append((value >> 48) & 0xFFFF)
            self.payload.append((value >> 32) & 0xFFFF)
            self.payload.append((value >> 16) & 0xFFFF)
            self.payload.append(value & 0xFFFF)
        else:
            self.payload.append(value & 0xFFFF)
            self.payload.append((value >> 16) & 0xFFFF)
            self.payload.append((value >> 32) & 0xFFFF)
            self.payload.append((value >> 48) & 0xFFFF)
        return self
    
    def add_64bit_int(self, value):
        """添加64位有符号整数
        
        Args:
            value (int): 64位有符号整数
            
        Returns:
            BinaryPayloadBuilder: 自身
        """
        # 转换为无符号
        if value < 0:
            value += 18446744073709551616
        return self.add_64bit_uint(value)
    
    def add_64bit_float(self, value):
        """添加64位浮点数
        
        Args:
            value (float): 64位浮点数
            
        Returns:
            BinaryPayloadBuilder: 自身
        """
        # 模拟实现，只存储整数部分
        self.add_64bit_uint(int(value))
        return self
    
    def add_string(self, value):
        """添加字符串
        
        Args:
            value (str): 字符串
            
        Returns:
            BinaryPayloadBuilder: 自身
        """
        # 模拟实现，每个字符占一个寄存器
        for c in value:
            self.payload.append(ord(c))
        return self
    
    def build(self):
        """构建负载
        
        Returns:
            list: 寄存器列表
        """
        return self.payload 