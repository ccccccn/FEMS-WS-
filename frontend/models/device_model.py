#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import uuid
import re
from datetime import datetime

logger = logging.getLogger(__name__)

# Define supported device types
DEVICE_TYPES = [
    "S7-1200", "S7-1500", "S7-300", "S7-400",  # Siemens S7 PLCs
    "Modbus TCP", "Modbus RTU",                # Modbus devices
    "CAN",                                     # CAN bus
    "GOOSE", "MMS",                            # IEC 61850
    "OPC UA", "OPC DA",                        # OPC
    "Custom"                                   # Custom device types
]

class Device:
    """Represents a physical device in the system."""
    
    def __init__(self, name="", device_type="", ip_address="", port=0, description="", device_id=None):
        self.device_id = device_id or str(uuid.uuid4())
        self.name = name
        self.device_type = self._validate_device_type(device_type)
        self.ip_address = ip_address
        self.port = port
        self.description = description
        self.is_connected = False
        self.connection_settings = {}  # Protocol-specific settings
        self.variables = []
        self.connection_status = "未连接"  # 未连接, 连接中, 已连接, 连接错误
        self.connection_error = ""
        self.last_connection_attempt = None
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
    
    def _validate_device_type(self, device_type):
        """Validate and normalize device type."""
        if not device_type:
            return "Custom"
        
        # Try exact match first
        for valid_type in DEVICE_TYPES:
            if device_type.lower() == valid_type.lower():
                return valid_type
        
        # Try partial match
        for valid_type in DEVICE_TYPES:
            if valid_type.lower() in device_type.lower():
                return valid_type
        
        # Default to custom if no match
        return "Custom"
    
    def add_variable(self, variable):
        """Add a variable to the device."""
        # Ensure variable has a unique name within this device
        existing_names = [var.name for var in self.variables]
        if variable.name in existing_names:
            # Add a suffix to make the name unique
            base_name = variable.name
            counter = 1
            while f"{base_name}_{counter}" in existing_names:
                counter += 1
            variable.name = f"{base_name}_{counter}"
            logger.info(f"Renamed variable to ensure uniqueness: {variable.name}")
        
        self.variables.append(variable)
        self.updated_at = datetime.now().isoformat()
        return True
    
    def update_variable(self, variable):
        """Update an existing variable in the device.
        
        Args:
            variable (Variable): Variable to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        for i, var in enumerate(self.variables):
            if var.variable_id == variable.variable_id:
                self.variables[i] = variable
                self.updated_at = datetime.now().isoformat()
                return True
        
        # 如果找不到匹配的变量ID，尝试按名称匹配
        for i, var in enumerate(self.variables):
            if var.name == variable.name:
                self.variables[i] = variable
                self.updated_at = datetime.now().isoformat()
                logger.info(f"已通过名称匹配更新变量: {variable.name}")
                return True
        
        logger.warning(f"无法更新变量，找不到匹配的ID或名称: {variable.variable_id}, {variable.name}")
        return False
    
    def remove_variable(self, variable):
        """Remove a variable from the device.
        
        Args:
            variable (Variable): Variable to remove
            
        Returns:
            bool: True if successful, False otherwise
        """
        # 首先尝试通过ID匹配
        for i, var in enumerate(self.variables):
            if var.variable_id == variable.variable_id:
                self.variables.pop(i)
                self.updated_at = datetime.now().isoformat()
                return True
        
        # 如果找不到匹配的变量ID，尝试按名称匹配
        for i, var in enumerate(self.variables):
            if var.name == variable.name:
                self.variables.pop(i)
                self.updated_at = datetime.now().isoformat()
                logger.info(f"已通过名称匹配删除变量: {variable.name}")
                return True
        
        logger.warning(f"无法删除变量，找不到匹配的ID或名称: {variable.variable_id}, {variable.name}")
        return False
    
    def get_variable(self, variable_id):
        """Get a variable by its ID."""
        for variable in self.variables:
            if variable.variable_id == variable_id:
                return variable
        return None
    
    def update_connection_setting(self, key, value):
        """Update a connection setting."""
        self.connection_settings[key] = value
        self.updated_at = datetime.now().isoformat()
    
    def validate_ip_address(self, ip_address):
        """Validate IP address format."""
        ip_pattern = r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        return bool(re.match(ip_pattern, ip_address))
    
    def update_connection_status(self, is_connected, error_message=""):
        """Update the connection status of the device."""
        self.is_connected = is_connected
        self.last_connection_attempt = datetime.now().isoformat()
        
        if is_connected:
            self.connection_status = "已连接"
            self.connection_error = ""
        else:
            self.connection_status = "连接错误" if error_message else "未连接"
            self.connection_error = error_message
        
        self.updated_at = datetime.now().isoformat()
        
        # Return the new status for event handling
        return self.connection_status
    
    def set_s7_settings(self, rack=0, slot=1, db_number=None):
        """Set Siemens S7 specific connection settings."""
        # Validate rack and slot
        try:
            rack = int(rack)
            slot = int(slot)
            if rack < 0 or slot < 0:
                raise ValueError("Rack and slot must be non-negative integers")
        except (ValueError, TypeError):
            rack = 0
            slot = 1
            logger.warning("Invalid rack or slot value, using defaults (0, 1)")
        
        self.connection_settings.update({
            "rack": rack,
            "slot": slot,
            "db_number": db_number
        })
        self.updated_at = datetime.now().isoformat()
    
    def set_modbus_settings(self, modbus_type="TCP", unit_id=1):
        """Set Modbus specific connection settings."""
        # Validate unit ID
        try:
            unit_id = int(unit_id)
            if unit_id < 0 or unit_id > 255:
                raise ValueError("Unit ID must be between 0 and 255")
        except (ValueError, TypeError):
            unit_id = 1
            logger.warning("Invalid unit ID, using default (1)")
        
        # Normalize Modbus type
        if modbus_type.upper() not in ["TCP", "RTU"]:
            modbus_type = "TCP"
            logger.warning("Invalid Modbus type, using TCP")
        
        self.connection_settings.update({
            "modbus_type": modbus_type.upper(),
            "unit_id": unit_id
        })
        self.updated_at = datetime.now().isoformat()
    
    def set_can_settings(self, interface="can0", bitrate=500000):
        """Set CAN specific connection settings."""
        # Validate bitrate
        try:
            bitrate = int(bitrate)
            if bitrate <= 0:
                raise ValueError("Bitrate must be positive")
        except (ValueError, TypeError):
            bitrate = 500000
            logger.warning("Invalid bitrate, using default (500000)")
        
        self.connection_settings.update({
            "interface": interface,
            "bitrate": bitrate
        })
        self.updated_at = datetime.now().isoformat()
    
    def set_goose_settings(self, interface="eth0", appid=None, mac=None):
        """Set GOOSE specific connection settings."""
        # Validate MAC address if provided
        if mac and not re.match(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$", mac):
            mac = None
            logger.warning("Invalid MAC address format")
        
        # Validate AppID if provided
        if appid:
            try:
                appid = int(appid)
                if appid < 0 or appid > 65535:
                    raise ValueError("AppID must be between 0 and 65535")
            except (ValueError, TypeError):
                appid = None
                logger.warning("Invalid AppID, must be between 0 and 65535")
        
        self.connection_settings.update({
            "interface": interface,
            "appid": appid,
            "mac": mac
        })
        self.updated_at = datetime.now().isoformat()
    
    def get_connection_info(self):
        """Get formatted connection information."""
        if self.device_type.startswith("S7"):
            rack = self.connection_settings.get("rack", 0)
            slot = self.connection_settings.get("slot", 1)
            return f"{self.ip_address}:{self.port} (Rack: {rack}, Slot: {slot})"
        elif self.device_type.startswith("Modbus"):
            modbus_type = self.connection_settings.get("modbus_type", "TCP")
            unit_id = self.connection_settings.get("unit_id", 1)
            return f"{self.ip_address}:{self.port} (Unit ID: {unit_id})"
        elif self.device_type == "CAN":
            interface = self.connection_settings.get("interface", "can0")
            bitrate = self.connection_settings.get("bitrate", 500000)
            return f"Interface: {interface} (Bitrate: {bitrate})"
        elif self.device_type in ["GOOSE", "MMS"]:
            interface = self.connection_settings.get("interface", "eth0")
            appid = self.connection_settings.get("appid", "N/A")
            return f"Interface: {interface} (AppID: {appid})"
        else:
            return f"{self.ip_address}:{self.port}"
    
    def to_dict(self):
        """Convert device to a dictionary."""
        return {
            "device_id": self.device_id,
            "name": self.name,
            "device_type": self.device_type,
            "ip_address": self.ip_address,
            "port": self.port,
            "description": self.description,
            "is_connected": self.is_connected,
            "connection_status": self.connection_status,
            "connection_error": self.connection_error,
            "last_connection_attempt": self.last_connection_attempt,
            "connection_settings": self.connection_settings,
            "variables": [variable.to_dict() for variable in self.variables],
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a device from a dictionary."""
        from frontend.models.variable_model import Variable
        
        device = cls(
            name=data.get("name", ""),
            device_type=data.get("device_type", ""),
            ip_address=data.get("ip_address", ""),
            port=data.get("port", 0),
            description=data.get("description", ""),
            device_id=data.get("device_id")
        )
        device.is_connected = data.get("is_connected", False)
        device.connection_status = data.get("connection_status", "未连接")
        device.connection_error = data.get("connection_error", "")
        device.last_connection_attempt = data.get("last_connection_attempt")
        device.connection_settings = data.get("connection_settings", {})
        device.created_at = data.get("created_at", device.created_at)
        device.updated_at = data.get("updated_at", device.updated_at)
        
        # Add variables
        for variable_data in data.get("variables", []):
            variable = Variable.from_dict(variable_data)
            device.variables.append(variable)
        
        return device 