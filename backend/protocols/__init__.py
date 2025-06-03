#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from importlib import import_module
import os

logger = logging.getLogger(__name__)

# 默认使用模拟协议工厂
from .protocol_factory_mock import get_protocol, connect_all, disconnect_all

# 如果环境变量设置为使用实际协议，则尝试导入实际协议工厂
if os.environ.get('USE_MOCK_PROTOCOLS') != '1':
    try:
        from .protocol_factory import get_protocol, connect_all, disconnect_all
    except ImportError:
        logger.warning("实际协议工厂不可用，使用模拟协议工厂")

class ProtocolFactory:
    """Factory for creating and managing protocol instances."""
    
    # Supported protocols
    PROTOCOLS = {
        'S7': {
            'module': 'backend.protocols.s7_protocol',
            'class': 'S7Protocol'
        },
        'Modbus': {
            'module': 'backend.protocols.modbus_protocol',
            'class': 'ModbusProtocol'
        },
        'CAN': {
            'module': 'backend.protocols.can_protocol',
            'class': 'CANProtocol'
        },
        'GOOSE': {
            'module': 'backend.protocols.goose_protocol',
            'class': 'GOOSEProtocol'
        }
    }
    
    def __init__(self):
        """Initialize the protocol factory."""
        self.instances = {}
    
    def get_protocol(self, protocol_type, settings):
        """Get or create a protocol instance.
        
        Args:
            protocol_type (str): Protocol type (S7, Modbus, CAN, GOOSE)
            settings (dict): Protocol settings
        
        Returns:
            object: Protocol instance or None if not supported
        """
        # Check if protocol is supported
        if protocol_type not in self.PROTOCOLS:
            logger.error(f"Unsupported protocol: {protocol_type}")
            return None
        
        # Create identifier from protocol type and key settings
        identifier = self._create_identifier(protocol_type, settings)
        
        # Check if instance already exists
        if identifier in self.instances:
            logger.debug(f"Using existing protocol instance: {identifier}")
            return self.instances[identifier]
        
        # Create new instance
        try:
            # Import module
            module_name = self.PROTOCOLS[protocol_type]['module']
            class_name = self.PROTOCOLS[protocol_type]['class']
            
            module = import_module(module_name)
            protocol_class = getattr(module, class_name)
            
            # Create instance
            if protocol_type == 'S7':
                instance = protocol_class(
                    settings.get('ip', '127.0.0.1'),
                    settings.get('rack', 0),
                    settings.get('slot', 1),
                    settings.get('timeout', 5),
                    settings.get('pdu_size', 480)
                )
            else:
                instance = protocol_class(settings)
            
            # Store instance
            self.instances[identifier] = instance
            logger.info(f"Created new protocol instance: {identifier}")
            
            return instance
            
        except Exception as e:
            logger.error(f"Error creating protocol instance: {str(e)}")
            return None
    
    def connect_all(self):
        """Connect all protocol instances."""
        results = {}
        
        for identifier, instance in self.instances.items():
            try:
                results[identifier] = instance.connect()
            except Exception as e:
                logger.error(f"Error connecting {identifier}: {str(e)}")
                results[identifier] = False
        
        return results
    
    def disconnect_all(self):
        """Disconnect all protocol instances."""
        results = {}
        
        for identifier, instance in self.instances.items():
            try:
                results[identifier] = instance.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting {identifier}: {str(e)}")
                results[identifier] = False
        
        return results
    
    def _create_identifier(self, protocol_type, settings):
        """Create a unique identifier for a protocol instance.
        
        Args:
            protocol_type (str): Protocol type (S7, Modbus, CAN, GOOSE)
            settings (dict): Protocol settings
        
        Returns:
            str: Unique identifier
        """
        if protocol_type == 'S7':
            ip = settings.get('ip', '127.0.0.1')
            rack = settings.get('rack', 0)
            slot = settings.get('slot', 1)
            return f"S7_{ip}_{rack}_{slot}"
        
        elif protocol_type == 'Modbus':
            if settings.get('type') == 'TCP':
                ip = settings.get('ip', '127.0.0.1')
                port = settings.get('port', 502)
                return f"Modbus_TCP_{ip}_{port}"
            else:
                port = settings.get('port', 'COM1')
                return f"Modbus_RTU_{port}"
        
        elif protocol_type == 'CAN':
            interface = settings.get('interface', 'can0')
            return f"CAN_{interface}"
        
        elif protocol_type == 'GOOSE':
            interface = settings.get('interface', 'eth0')
            appid = settings.get('appid', '0x1000')
            return f"GOOSE_{interface}_{appid}"
        
        else:
            return f"{protocol_type}_{id(settings)}"

# Create a singleton instance
protocol_factory = ProtocolFactory() 

# Protocol implementations 