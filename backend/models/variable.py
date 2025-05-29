#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class Variable:
    """Model class for variables in the data acquisition system."""
    
    def __init__(self, variable_id, name, data_type, address, protocol_type, device_id, description=""):
        """Initialize a variable.
        
        Args:
            variable_id (str): Unique identifier for the variable
            name (str): Variable name
            data_type (str): Data type (BOOL, BYTE, WORD, DWORD, INT, DINT, REAL, STRING)
            address (str): Address in protocol-specific format
            protocol_type (str): Protocol type (S7, Modbus, CAN, GOOSE)
            device_id (str): Device identifier
            description (str): Optional description
        """
        self.id = variable_id
        self.name = name
        self.data_type = data_type
        self.address = address
        self.protocol_type = protocol_type
        self.device_id = device_id
        self.description = description
        
        # Value properties
        self.value = None
        self.quality = "Unknown"
        self.timestamp = None
        self.status = "未知"
        
        # Threshold settings
        self.thresholds_enabled = False
        self.warning_low = None
        self.warning_high = None
        self.alarm_low = None
        self.alarm_high = None
        
        # Acquisition and storage settings
        self.collection_frequency = 1.0  # Default collection frequency in seconds
        self.storage_frequency = 60.0    # Default storage frequency in seconds
        self.storage_enabled = True      # Whether to store this variable's data
        self.last_collection_time = 0    # Last time this variable was collected
        self.last_storage_time = 0       # Last time this variable was stored
    
    def to_dict(self):
        """Convert variable to dictionary.
        
        Returns:
            dict: Variable as dictionary
        """
        return {
            'id': self.id,
            'name': self.name,
            'data_type': self.data_type,
            'address': self.address,
            'protocol_type': self.protocol_type,
            'device_id': self.device_id,
            'description': self.description,
            'value': self.value,
            'quality': self.quality,
            'timestamp': self.timestamp,
            'status': self.status,
            'thresholds_enabled': self.thresholds_enabled,
            'warning_low': self.warning_low,
            'warning_high': self.warning_high,
            'alarm_low': self.alarm_low,
            'alarm_high': self.alarm_high,
            'collection_frequency': self.collection_frequency,
            'storage_frequency': self.storage_frequency,
            'storage_enabled': self.storage_enabled
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create variable from dictionary.
        
        Args:
            data (dict): Variable data
        
        Returns:
            Variable: New variable instance
        """
        variable = cls(
            data.get('id', ''),
            data.get('name', ''),
            data.get('data_type', ''),
            data.get('address', ''),
            data.get('protocol_type', ''),
            data.get('device_id', ''),
            data.get('description', '')
        )
        
        # Set optional properties if available
        if 'value' in data:
            variable.value = data['value']
        
        if 'quality' in data:
            variable.quality = data['quality']
        
        if 'timestamp' in data:
            variable.timestamp = data['timestamp']
        
        if 'status' in data:
            variable.status = data['status']
        
        if 'thresholds_enabled' in data:
            variable.thresholds_enabled = data['thresholds_enabled']
        
        if 'warning_low' in data:
            variable.warning_low = data['warning_low']
        
        if 'warning_high' in data:
            variable.warning_high = data['warning_high']
        
        if 'alarm_low' in data:
            variable.alarm_low = data['alarm_low']
        
        if 'alarm_high' in data:
            variable.alarm_high = data['alarm_high']
            
        # Set acquisition and storage settings if available
        if 'collection_frequency' in data:
            variable.collection_frequency = float(data['collection_frequency'])
            
        if 'storage_frequency' in data:
            variable.storage_frequency = float(data['storage_frequency'])
            
        if 'storage_enabled' in data:
            variable.storage_enabled = bool(data['storage_enabled'])
        
        return variable
    
    def set_value(self, value, quality="Good"):
        """Set the current value of the variable.
        
        Args:
            value: The new value
            quality (str): Quality indicator (Good, Bad, Uncertain)
        
        Returns:
            str: Variable status after update
        """
        self.value = value
        self.quality = quality
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        # Update status based on thresholds if enabled
        if self.thresholds_enabled and quality == "Good" and value is not None:
            self._update_status()
        else:
            self.status = "正常" if quality == "Good" else "错误"
        
        return self.status
    
    def _update_status(self):
        """Update status based on current value and thresholds."""
        if not self.thresholds_enabled or self.value is None:
            self.status = "正常"
            return
        
        try:
            # Convert value to number for comparison
            if isinstance(self.value, bool):
                value = 1 if self.value else 0
            else:
                value = float(self.value)
            
            # Check alarms first (higher priority)
            if self.alarm_low is not None and value <= self.alarm_low:
                self.status = "报警"
                return
            
            if self.alarm_high is not None and value >= self.alarm_high:
                self.status = "报警"
                return
            
            # Check warnings
            if self.warning_low is not None and value <= self.warning_low:
                self.status = "警告"
                return
            
            if self.warning_high is not None and value >= self.warning_high:
                self.status = "警告"
                return
            
            # If no thresholds exceeded
            self.status = "正常"
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Error updating status for variable {self.name}: {str(e)}")
            self.status = "正常"
    
    def set_thresholds(self, enabled=True, warning_low=None, warning_high=None, alarm_low=None, alarm_high=None):
        """Set threshold values for the variable.
        
        Args:
            enabled (bool): Enable or disable thresholds
            warning_low: Low warning threshold
            warning_high: High warning threshold
            alarm_low: Low alarm threshold
            alarm_high: High alarm threshold
        """
        self.thresholds_enabled = enabled
        
        if warning_low is not None:
            self.warning_low = float(warning_low)
        
        if warning_high is not None:
            self.warning_high = float(warning_high)
        
        if alarm_low is not None:
            self.alarm_low = float(alarm_low)
            
        if alarm_high is not None:
            self.alarm_high = float(alarm_high)
            
    def set_acquisition_settings(self, collection_frequency=None, storage_frequency=None, storage_enabled=None):
        """Set acquisition and storage settings for the variable.
        
        Args:
            collection_frequency (float): Collection frequency in seconds
            storage_frequency (float): Storage frequency in seconds
            storage_enabled (bool): Whether to store this variable's data
        """
        if collection_frequency is not None:
            self.collection_frequency = max(0.1, float(collection_frequency))
            
        if storage_frequency is not None:
            self.storage_frequency = max(1.0, float(storage_frequency))
            
        if storage_enabled is not None:
            self.storage_enabled = bool(storage_enabled)
            
        logger.info(f"Updated acquisition settings for variable {self.name}: "
                   f"collection_freq={self.collection_frequency}s, "
                   f"storage_freq={self.storage_frequency}s, "
                   f"storage_enabled={self.storage_enabled}")
    
    def __str__(self):
        """String representation of the variable."""
        return f"Variable({self.id}, {self.name}, {self.protocol_type})"

class VariableManager:
    """Manager class for variables."""
    
    def __init__(self):
        """Initialize variable manager."""
        self.variables = {}
    
    def add_variable(self, variable):
        """Add a variable.
        
        Args:
            variable (Variable): Variable to add
        
        Returns:
            bool: True if successful, False if variable ID already exists
        """
        if variable.id in self.variables:
            logger.warning(f"Variable with ID {variable.id} already exists")
            return False
        
        self.variables[variable.id] = variable
        return True
    
    def get_variable(self, variable_id):
        """Get a variable by ID.
        
        Args:
            variable_id (str): Variable ID
        
        Returns:
            Variable: Variable or None if not found
        """
        return self.variables.get(variable_id)
    
    def update_variable(self, variable_id, data):
        """Update a variable.
        
        Args:
            variable_id (str): Variable ID
            data (dict): Updated variable data
        
        Returns:
            bool: True if successful, False if variable not found
        """
        if variable_id not in self.variables:
            logger.warning(f"Variable with ID {variable_id} not found")
            return False
        
        variable = self.variables[variable_id]
        
        # Update properties
        for key, value in data.items():
            if hasattr(variable, key):
                setattr(variable, key, value)
        
        return True
    
    def remove_variable(self, variable_id):
        """Remove a variable.
        
        Args:
            variable_id (str): Variable ID
        
        Returns:
            bool: True if successful, False if variable not found
        """
        if variable_id not in self.variables:
            logger.warning(f"Variable with ID {variable_id} not found")
            return False
        
        del self.variables[variable_id]
        return True
    
    def get_all_variables(self):
        """Get all variables.
        
        Returns:
            list: List of all variables
        """
        return list(self.variables.values())
    
    def get_variables_by_protocol(self, protocol_type):
        """Get variables by protocol type.
        
        Args:
            protocol_type (str): Protocol type
        
        Returns:
            list: List of variables using the specified protocol
        """
        return [var for var in self.variables.values() if var.protocol_type == protocol_type]
    
    def get_variables_by_device(self, device_id):
        """Get variables by device ID.
        
        Args:
            device_id (str): Device ID
        
        Returns:
            list: List of variables for the specified device
        """
        return [var for var in self.variables.values() if var.device_id == device_id]
    
    def to_dict(self):
        """Convert all variables to a dictionary.
        
        Returns:
            dict: Dictionary of variables
        """
        return {var_id: var.to_dict() for var_id, var in self.variables.items()}
    
    def from_dict(self, data):
        """Load variables from a dictionary.
        
        Args:
            data (dict): Dictionary of variables
        """
        self.variables = {}
        for var_id, var_data in data.items():
            self.variables[var_id] = Variable.from_dict(var_data)
    
    def clear(self):
        """Clear all variables."""
        self.variables = {} 