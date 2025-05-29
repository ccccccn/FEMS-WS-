#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import uuid
from datetime import datetime
import numbers

logger = logging.getLogger(__name__)

class Threshold:
    """Represents threshold settings for a variable."""
    
    def __init__(self, 
                 enabled=False, 
                 warning_low=None, 
                 warning_high=None, 
                 alarm_low=None, 
                 alarm_high=None):
        self.enabled = enabled
        self.warning_low = warning_low
        self.warning_high = warning_high
        self.alarm_low = alarm_low
        self.alarm_high = alarm_high
        self.validate_thresholds()
    
    def validate_thresholds(self):
        """Validate threshold values to ensure they make logical sense."""
        # Convert string values to numbers if possible
        for attr in ['warning_low', 'warning_high', 'alarm_low', 'alarm_high']:
            value = getattr(self, attr)
            if isinstance(value, str) and value.strip():
                try:
                    setattr(self, attr, float(value))
                except ValueError:
                    setattr(self, attr, None)
                    logger.warning(f"Invalid threshold value for {attr}: {value}")
        
        # Skip validation if thresholds not enabled
        if not self.enabled:
            return True
            
        # Ensure alarm thresholds are outside warning thresholds
        if self.alarm_low is not None and self.warning_low is not None:
            if self.alarm_low > self.warning_low:
                logger.warning("Alarm low threshold should be lower than warning low threshold")
                self.alarm_low = self.warning_low
        
        if self.alarm_high is not None and self.warning_high is not None:
            if self.alarm_high < self.warning_high:
                logger.warning("Alarm high threshold should be higher than warning high threshold")
                self.alarm_high = self.warning_high
        
        # Ensure low thresholds are lower than high thresholds
        if self.warning_low is not None and self.warning_high is not None:
            if self.warning_low > self.warning_high:
                logger.warning("Warning low threshold should be lower than warning high threshold")
                # Swap values
                self.warning_low, self.warning_high = self.warning_high, self.warning_low
        
        if self.alarm_low is not None and self.alarm_high is not None:
            if self.alarm_low > self.alarm_high:
                logger.warning("Alarm low threshold should be lower than alarm high threshold")
                # Swap values
                self.alarm_low, self.alarm_high = self.alarm_high, self.alarm_low
                
        return True
    
    def check_value(self, value):
        """Check if a value is within thresholds and return status."""
        if not self.enabled:
            return "正常"
            
        # Ensure value is numeric
        if not isinstance(value, numbers.Number):
            try:
                value = float(value)
            except (ValueError, TypeError):
                return "正常"  # Non-numeric values don't trigger thresholds
        
        # Check alarms first (more severe)
        if self.alarm_low is not None and value <= self.alarm_low:
            return "报警"
        if self.alarm_high is not None and value >= self.alarm_high:
            return "报警"
        
        # Then check warnings
        if self.warning_low is not None and value <= self.warning_low:
            return "警告"
        if self.warning_high is not None and value >= self.warning_high:
            return "警告"
        
        return "正常"
    
    def to_dict(self):
        """Convert threshold to a dictionary."""
        return {
            "enabled": self.enabled,
            "warning_low": self.warning_low,
            "warning_high": self.warning_high,
            "alarm_low": self.alarm_low,
            "alarm_high": self.alarm_high
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a threshold from a dictionary."""
        return cls(
            enabled=data.get("enabled", False),
            warning_low=data.get("warning_low"),
            warning_high=data.get("warning_high"),
            alarm_low=data.get("alarm_low"),
            alarm_high=data.get("alarm_high")
        )

class Variable:
    """Represents a variable in the data acquisition system."""
    
    def __init__(self, 
                 name="", 
                 data_type="", 
                 address="", 
                 description="", 
                 variable_id=None):
        self.variable_id = variable_id or str(uuid.uuid4())
        self.name = name
        self.data_type = data_type
        self.address = address
        self.description = description
        self.current_value = None
        self.quality = "未知"
        self.status = "正常"
        self.last_updated = None
        self.threshold = Threshold()
        self.history = []  # For storing recent values
        self.history_max_points = 100
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.units = ""  # Add units for display
        self.api_endpoint = None  # API endpoint for real-time data
        self.polling_interval = 1000  # Default polling interval in ms
    
        # 添加数据采集和存储设置
        self.collection_frequency = 1.0  # 默认采集频率，单位秒
        self.storage_frequency = 60.0    # 默认存储频率，单位秒
        self.storage_enabled = True      # 是否启用数据存储
        self.last_collection_time = 0    # 上次采集时间
        self.last_storage_time = 0       # 上次存储时间
    
    def update_value(self, value, quality="良好", timestamp=None):
        """Update the variable value and check thresholds."""
        # Try to convert string values to appropriate type
        if isinstance(value, str) and value.strip():
            try:
                if self.data_type.lower() in ["int", "integer", "word", "dword"]:
                    value = int(value)
                elif self.data_type.lower() in ["float", "real", "double"]:
                    value = float(value)
                elif self.data_type.lower() in ["bool", "boolean", "bit"]:
                    value = value.lower() in ["true", "1", "yes", "y", "on"]
            except (ValueError, TypeError):
                # Keep as string if conversion fails
                pass
                
        # Update value
        self.current_value = value
        self.quality = quality
        self.last_updated = timestamp or datetime.now().isoformat()
        
        # Check thresholds
        if isinstance(value, numbers.Number):
            self.status = self.threshold.check_value(value)
        else:
            self.status = "正常"  # Non-numeric values are always normal
        
        # Add to history if it's a numeric value
        if isinstance(value, numbers.Number):
            # Maintain history size
            if len(self.history) >= self.history_max_points:
                self.history.pop(0)
            
            # Add new point
            self.history.append({
                "value": value,
                "timestamp": self.last_updated,
                "status": self.status
            })
        
        self.updated_at = datetime.now().isoformat()
        return self.status
    
    def set_threshold(self, enabled=True, warning_low=None, warning_high=None, 
                      alarm_low=None, alarm_high=None):
        """Set threshold values for the variable."""
        self.threshold = Threshold(
            enabled=enabled,
            warning_low=warning_low,
            warning_high=warning_high,
            alarm_low=alarm_low,
            alarm_high=alarm_high
        )
        self.updated_at = datetime.now().isoformat()
        
        # Re-check current value against new thresholds
        if self.current_value is not None:
            self.status = self.threshold.check_value(self.current_value)
            
        return self.threshold
    
    def set_api_endpoint(self, endpoint, polling_interval=None):
        """Set API endpoint for real-time data updates."""
        self.api_endpoint = endpoint
        if polling_interval is not None:
            self.polling_interval = polling_interval
        self.updated_at = datetime.now().isoformat()
    
    def set_acquisition_settings(self, collection_frequency=None, storage_frequency=None, storage_enabled=None):
        """设置变量的采集和存储参数
        
        Args:
            collection_frequency (float, optional): 采集频率，单位秒
            storage_frequency (float, optional): 存储频率，单位秒
            storage_enabled (bool, optional): 是否启用数据存储
        """
        if collection_frequency is not None:
            self.collection_frequency = max(0.1, float(collection_frequency))
            
        if storage_frequency is not None:
            self.storage_frequency = max(1.0, float(storage_frequency))
            
        if storage_enabled is not None:
            self.storage_enabled = bool(storage_enabled)
            
        self.updated_at = datetime.now().isoformat()
        
        return {
            "collection_frequency": self.collection_frequency,
            "storage_frequency": self.storage_frequency,
            "storage_enabled": self.storage_enabled
        }
    
    def get_formatted_value(self):
        """Get current value with appropriate formatting based on data type."""
        if self.current_value is None:
            return "N/A"
            
        if isinstance(self.current_value, bool):
            return "ON" if self.current_value else "OFF"
        elif isinstance(self.current_value, int):
            return f"{self.current_value:,d}"
        elif isinstance(self.current_value, float):
            # Use appropriate precision
            return f"{self.current_value:.2f}"
        else:
            return str(self.current_value)
    
    def get_value_with_units(self):
        """Get formatted value with units if available."""
        formatted = self.get_formatted_value()
        if self.units and formatted != "N/A":
            return f"{formatted} {self.units}"
        return formatted
    
    def to_dict(self):
        """Convert variable to a dictionary."""
        return {
            "variable_id": self.variable_id,
            "name": self.name,
            "data_type": self.data_type,
            "address": self.address,
            "description": self.description,
            "current_value": self.current_value,
            "quality": self.quality,
            "status": self.status,
            "last_updated": self.last_updated,
            "threshold": self.threshold.to_dict(),
            "history": self.history[:20],  # Only store the most recent points
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "units": self.units,
            "api_endpoint": self.api_endpoint,
            "polling_interval": self.polling_interval,
            "collection_frequency": self.collection_frequency,
            "storage_frequency": self.storage_frequency,
            "storage_enabled": self.storage_enabled,
            "last_collection_time": self.last_collection_time,
            "last_storage_time": self.last_storage_time
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a variable from a dictionary."""
        variable = cls(
            name=data.get("name", ""),
            data_type=data.get("data_type", ""),
            address=data.get("address", ""),
            description=data.get("description", ""),
            variable_id=data.get("variable_id")
        )
        
        # Set basic properties
        if "current_value" in data:
            variable.current_value = data["current_value"]
        if "quality" in data:
            variable.quality = data["quality"]
        if "status" in data:
            variable.status = data["status"]
        if "last_updated" in data:
            variable.last_updated = data["last_updated"]
        if "created_at" in data:
            variable.created_at = data["created_at"]
        if "updated_at" in data:
            variable.updated_at = data["updated_at"]
        if "units" in data:
            variable.units = data["units"]
        if "api_endpoint" in data:
            variable.api_endpoint = data["api_endpoint"]
        if "polling_interval" in data:
            variable.polling_interval = data["polling_interval"]
        
        # Set threshold
        if "threshold" in data:
            variable.threshold = Threshold.from_dict(data["threshold"])
        
        # Set history
        if "history" in data:
            variable.history = data["history"]
            
        # 设置采集和存储参数
        if "collection_frequency" in data:
            variable.collection_frequency = float(data["collection_frequency"])
        if "storage_frequency" in data:
            variable.storage_frequency = float(data["storage_frequency"])
        if "storage_enabled" in data:
            variable.storage_enabled = bool(data["storage_enabled"])
        if "last_collection_time" in data:
            variable.last_collection_time = data["last_collection_time"]
        if "last_storage_time" in data:
            variable.last_storage_time = data["last_storage_time"]
        
        return variable 