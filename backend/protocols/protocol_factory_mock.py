#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from .mock.s7_protocol import S7Protocol
from .mock.modbus_protocol import ModbusProtocol

logger = logging.getLogger(__name__)

# Protocol instances
_protocols = {}

def get_protocol(protocol_type, settings):
    """获取协议实例。
    
    Args:
        protocol_type (str): 协议类型 (S7, Modbus, CAN, GOOSE)
        settings (dict): 协议设置
    
    Returns:
        object: 协议实例，如果不可用则为None
    """
    global _protocols
    
    # 从协议类型和设置创建键
    key = f"{protocol_type}_{hash(frozenset(settings.items()))}"
    
    # 如果可用，返回现有实例
    if key in _protocols:
        return _protocols[key]
    
    # 创建新实例
    try:
        if protocol_type == "S7":
            if 'ip' in settings:
                protocol = S7Protocol(
                    settings.get('ip', '127.0.0.1'),
                    settings.get('rack', 0),
                    settings.get('slot', 1),
                    settings.get('timeout', 5),
                    settings.get('pdu_size', 480)
                )
            else:
                protocol = S7Protocol('127.0.0.1')
        elif protocol_type == "Modbus":
            protocol = ModbusProtocol(settings)
        elif protocol_type == "CAN":
            # 模拟CAN协议
            from .mock.modbus_protocol import ModbusProtocol
            protocol = ModbusProtocol(settings)  # 使用Modbus协议模拟CAN
        elif protocol_type == "GOOSE":
            # 模拟GOOSE协议
            from .mock.modbus_protocol import ModbusProtocol
            protocol = ModbusProtocol(settings)  # 使用Modbus协议模拟GOOSE
        else:
            logger.error(f"未知协议类型: {protocol_type}")
            return None
        
        # 存储实例
        _protocols[key] = protocol
        
        # 自动连接
        protocol.connect()
        
        return protocol
        
    except Exception as e:
        logger.error(f"创建协议实例时出错: {str(e)}")
        return None

def connect_all():
    """连接所有协议实例。
    
    Returns:
        dict: 连接结果字典
    """
    results = {}
    
    for key, protocol in _protocols.items():
        try:
            results[key] = protocol.connect()
        except Exception as e:
            logger.error(f"连接协议 {key} 时出错: {str(e)}")
            results[key] = False
    
    return results

def disconnect_all():
    """断开所有协议实例的连接。
    
    Returns:
        dict: 断开连接结果字典
    """
    results = {}
    
    for key, protocol in _protocols.items():
        try:
            results[key] = protocol.disconnect()
        except Exception as e:
            logger.error(f"断开协议 {key} 连接时出错: {str(e)}")
            results[key] = False
    
    return results 