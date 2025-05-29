#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import logging

logger = logging.getLogger(__name__)

class ConfigService:
    """Service for managing application configuration."""
    
    def __init__(self, config_dir="config"):
        """Initialize the configuration service.
        
        Args:
            config_dir (str): Configuration directory
        """
        self.config_dir = config_dir
        self.config = {}
        self.config_file = None
        
        # Load default configuration
        self.load_default_config()
    
    def load_default_config(self):
        """Load the default configuration."""
        default_config_file = os.path.join(self.config_dir, "default.json")
        if os.path.exists(default_config_file):
            self.load_config(default_config_file)
        else:
            logger.warning(f"Default configuration file not found: {default_config_file}")
            self.config = {}
    
    def load_config(self, config_file):
        """Load configuration from a file.
        
        Args:
            config_file (str): Configuration file path
        
        Returns:
            bool: True if successful
        """
        try:
            # Check if file exists
            if not os.path.exists(config_file):
                logger.error(f"Configuration file not found: {config_file}")
                return False
            
            # Load configuration
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            self.config_file = config_file
            logger.info(f"Configuration loaded from {config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            return False
    
    def save_config(self, config_file=None):
        """Save configuration to a file.
        
        Args:
            config_file (str, optional): Configuration file path.
                If None, use the last loaded or saved file.
        
        Returns:
            bool: True if successful
        """
        try:
            # Use provided file or last loaded/saved file
            save_file = config_file or self.config_file
            
            # If no file specified, use default
            if not save_file:
                save_file = os.path.join(self.config_dir, "user.json")
            
            # Create directory if it doesn't exist
            save_dir = os.path.dirname(save_file)
            if save_dir and not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            # Save configuration
            with open(save_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            self.config_file = save_file
            logger.info(f"Configuration saved to {save_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            return False
    
    def get(self, key, default=None):
        """Get a configuration value.
        
        Args:
            key (str): Configuration key in dot notation (e.g., "protocols.S7.enabled")
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        try:
            # Split key into parts
            parts = key.split('.')
            
            # Navigate through config
            value = self.config
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return default
            
            return value
            
        except Exception as e:
            logger.error(f"Error getting configuration value for {key}: {str(e)}")
            return default
    
    def set(self, key, value):
        """Set a configuration value.
        
        Args:
            key (str): Configuration key in dot notation (e.g., "protocols.S7.enabled")
            value: Value to set
        
        Returns:
            bool: True if successful
        """
        try:
            # Split key into parts
            parts = key.split('.')
            
            # Navigate through config
            config = self.config
            for i, part in enumerate(parts[:-1]):
                # Create nested dictionaries if they don't exist
                if part not in config:
                    config[part] = {}
                
                # Move to next level
                config = config[part]
            
            # Set value
            config[parts[-1]] = value
            return True
            
        except Exception as e:
            logger.error(f"Error setting configuration value for {key}: {str(e)}")
            return False
    
    def get_protocol_settings(self, protocol_type):
        """Get default settings for a protocol.
        
        Args:
            protocol_type (str): Protocol type (S7, Modbus, CAN, GOOSE)
        
        Returns:
            dict: Protocol settings or empty dict if not found
        """
        return self.get(f"protocols.{protocol_type}.default_settings", {})
    
    def get_device_settings(self, device_id):
        """Get settings for a device.
        
        Args:
            device_id (str): Device ID
        
        Returns:
            dict: Device settings or None if not found
        """
        # Find device in the devices list
        devices = self.get("devices", [])
        for device in devices:
            if device.get("id") == device_id:
                return device
        
        return None
    
    def get_all_devices(self):
        """Get all configured devices.
        
        Returns:
            list: List of device configurations
        """
        return self.get("devices", [])
    
    def add_device(self, device_config):
        """Add or update a device configuration.
        
        Args:
            device_config (dict): Device configuration
        
        Returns:
            bool: True if successful
        """
        try:
            # Get devices list
            devices = self.get("devices", [])
            
            # Check if device already exists
            for i, device in enumerate(devices):
                if device.get("id") == device_config.get("id"):
                    # Update existing device
                    devices[i] = device_config
                    self.set("devices", devices)
                    return True
            
            # Add new device
            devices.append(device_config)
            self.set("devices", devices)
            return True
            
        except Exception as e:
            logger.error(f"Error adding device: {str(e)}")
            return False
    
    def remove_device(self, device_id):
        """Remove a device configuration.
        
        Args:
            device_id (str): Device ID
        
        Returns:
            bool: True if successful
        """
        try:
            # Get devices list
            devices = self.get("devices", [])
            
            # Find and remove device
            for i, device in enumerate(devices):
                if device.get("id") == device_id:
                    devices.pop(i)
                    self.set("devices", devices)
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error removing device: {str(e)}")
            return False
    
    def get_acquisition_settings(self):
        """Get global acquisition settings.
        
        Returns:
            dict: Acquisition settings
        """
        return self.get("acquisition", {
            "update_rate": 1.0,
            "logging_enabled": False,
            "logging_interval": 60,
            "storage_location": "logs",
            "storage_format": "json"
        })
    
    def set_acquisition_settings(self, settings):
        """Set global acquisition settings.
        
        Args:
            settings (dict): Acquisition settings
        
        Returns:
            bool: True if successful
        """
        return self.set("acquisition", settings)
    
    def get_all_variables(self):
        """Get all configured variables.
        
        Returns:
            list: List of variable configurations
        """
        return self.get("variables", [])
    
    def get_variable_settings(self, variable_id):
        """Get settings for a specific variable.
        
        Args:
            variable_id (str): Variable ID
        
        Returns:
            dict: Variable settings or None if not found
        """
        variables = self.get("variables", [])
        for variable in variables:
            if variable.get("id") == variable_id:
                return variable
        
        return None
    
    def add_variable(self, variable_config):
        """Add or update a variable configuration.
        
        Args:
            variable_config (dict): Variable configuration
        
        Returns:
            bool: True if successful
        """
        try:
            # Get variables list
            variables = self.get("variables", [])
            
            # Check if variable already exists
            for i, variable in enumerate(variables):
                if variable.get("id") == variable_config.get("id"):
                    # Update existing variable
                    variables[i] = variable_config
                    self.set("variables", variables)
                    return True
            
            # Add new variable
            variables.append(variable_config)
            self.set("variables", variables)
            return True
            
        except Exception as e:
            logger.error(f"Error adding variable: {str(e)}")
            return False
    
    def remove_variable(self, variable_id):
        """Remove a variable configuration.
        
        Args:
            variable_id (str): Variable ID
        
        Returns:
            bool: True if successful
        """
        try:
            # Get variables list
            variables = self.get("variables", [])
            
            # Find and remove variable
            for i, variable in enumerate(variables):
                if variable.get("id") == variable_id:
                    variables.pop(i)
                    self.set("variables", variables)
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error removing variable: {str(e)}")
            return False
    
    def update_variable_acquisition_settings(self, variable_id, collection_frequency=None, 
                                           storage_frequency=None, storage_enabled=None):
        """Update acquisition settings for a specific variable.
        
        Args:
            variable_id (str): Variable ID
            collection_frequency (float, optional): Collection frequency in seconds
            storage_frequency (float, optional): Storage frequency in seconds
            storage_enabled (bool, optional): Whether to store this variable's data
        
        Returns:
            bool: True if successful
        """
        variables = self.get("variables", [])
        updated = False
        
        for i, variable in enumerate(variables):
            if variable.get("id") == variable_id:
                # Update settings
                if collection_frequency is not None:
                    variable["collection_frequency"] = float(collection_frequency)
                
                if storage_frequency is not None:
                    variable["storage_frequency"] = float(storage_frequency)
                
                if storage_enabled is not None:
                    variable["storage_enabled"] = bool(storage_enabled)
                
                # Update variable in list
                variables[i] = variable
                updated = True
                break
        
        if updated:
            # Save updated variables
            self.set("variables", variables)
            logger.info(f"Updated acquisition settings for variable {variable_id}")
            return True
        else:
            logger.warning(f"Variable with ID {variable_id} not found")
            return False
    
    def get_storage_settings(self):
        """Get global storage settings.
        
        Returns:
            dict: Storage settings
        """
        return self.get("storage", {
            "location": "logs",
            "format": "json"
        })
    
    def set_storage_settings(self, location=None, format_type=None):
        """Set global storage settings.
        
        Args:
            location (str, optional): Storage location
            format_type (str, optional): Storage format (json, csv)
        
        Returns:
            bool: True if successful
        """
        storage_settings = self.get_storage_settings()
        
        if location is not None:
            storage_settings["location"] = location
        
        if format_type is not None:
            storage_settings["format"] = format_type
        
        return self.set("storage", storage_settings)

# Create a singleton instance
config_service = ConfigService() 