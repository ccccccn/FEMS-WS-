#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 定义Endian类
class Endian:
    """用于指定字节序和字序的枚举类"""
    
    # 字节序 (Byte order)
    Big = ">"    # 大端序，最高有效字节在前
    Little = "<" # 小端序，最低有效字节在前
    
    # 字序 (Word order)
    Auto = "@"   # 系统默认
    Native = "="  # 本机字节序

# Modbus协议常量
class ModbusStatus:
    """Modbus状态码"""
    
    # 异常码
    ILLEGAL_FUNCTION = 0x01
    ILLEGAL_ADDRESS = 0x02
    ILLEGAL_VALUE = 0x03
    SLAVE_FAILURE = 0x04
    ACKNOWLEDGE = 0x05
    SLAVE_BUSY = 0x06
    MEMORY_PARITY_ERROR = 0x08
    GATEWAY_PATH_UNAVAILABLE = 0x0A
    GATEWAY_NO_RESPONSE = 0x0B

# 功能码
class ModbusFunctionCode:
    """Modbus功能码"""
    
    READ_COILS = 0x01
    READ_DISCRETE_INPUTS = 0x02
    READ_HOLDING_REGISTERS = 0x03
    READ_INPUT_REGISTERS = 0x04
    WRITE_SINGLE_COIL = 0x05
    WRITE_SINGLE_REGISTER = 0x06
    READ_EXCEPTION_STATUS = 0x07
    DIAGNOSTICS = 0x08
    WRITE_MULTIPLE_COILS = 0x0F
    WRITE_MULTIPLE_REGISTERS = 0x10
    REPORT_SLAVE_ID = 0x11
    READ_FILE_RECORD = 0x14
    WRITE_FILE_RECORD = 0x15
    MASK_WRITE_REGISTER = 0x16
    READ_WRITE_MULTIPLE_REGISTERS = 0x17
    READ_FIFO_QUEUE = 0x18
    ENCAPSULATED_INTERFACE_TRANSPORT = 0x2B 