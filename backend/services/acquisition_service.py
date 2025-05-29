#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time
import threading
import queue
from datetime import datetime
import json
import os

from backend.protocols import protocol_factory
from backend.models.variable import Variable, VariableManager

logger = logging.getLogger(__name__)

class AcquisitionService:
    """Service for managing data acquisition."""
    
    def __init__(self):
        """Initialize the acquisition service."""
        self.variable_manager = VariableManager()
        self.running = False
        self.acquisition_thread = None
        self.acquisition_queue = queue.Queue()
        self.results_queue = queue.Queue()
        
        # Settings
        self.update_rate = 1.0  # seconds - default global update rate
        self.logging_enabled = False
        self.logging_interval = 60  # seconds - default global logging interval
        self.last_log_time = 0
        
        # Storage settings
        self.storage_location = "logs"  # Default storage location
        self.storage_format = "json"    # Default storage format (json, csv, etc.)
    
    def start(self):
        """Start the acquisition service."""
        if self.running:
            logger.warning("Acquisition service is already running")
            return False
        
        # Connect to all protocols
        result = protocol_factory.connect_all()
        if not all(result.values()):
            logger.error("Failed to connect to some protocols")
            # Continue anyway, some protocols might work
        
        # Start acquisition thread
        self.running = True
        self.acquisition_thread = threading.Thread(target=self._acquisition_loop)
        self.acquisition_thread.daemon = True
        self.acquisition_thread.start()
        
        logger.info("Acquisition service started")
        return True
    
    def stop(self):
        """Stop the acquisition service."""
        if not self.running:
            logger.warning("Acquisition service is not running")
            return False
        
        # Stop acquisition thread
        self.running = False
        if self.acquisition_thread:
            self.acquisition_thread.join(timeout=5.0)
            if self.acquisition_thread.is_alive():
                logger.warning("Acquisition thread did not terminate gracefully")
        
        # Disconnect from all protocols
        protocol_factory.disconnect_all()
        
        logger.info("Acquisition service stopped")
        return True
    
    def add_variable(self, variable):
        """Add a variable to the service.
        
        Args:
            variable (Variable): Variable to add
        
        Returns:
            bool: True if successful
        """
        return self.variable_manager.add_variable(variable)
    
    def remove_variable(self, variable_id):
        """Remove a variable from the service.
        
        Args:
            variable_id (str): Variable ID
        
        Returns:
            bool: True if successful
        """
        return self.variable_manager.remove_variable(variable_id)
    
    def get_variable(self, variable_id):
        """Get a variable by ID.
        
        Args:
            variable_id (str): Variable ID
        
        Returns:
            Variable: Variable or None if not found
        """
        return self.variable_manager.get_variable(variable_id)
    
    def get_all_variables(self):
        """Get all variables.
        
        Returns:
            list: List of all variables
        """
        return self.variable_manager.get_all_variables()
    
    def read_variable(self, variable_id):
        """Read a variable's value.
        
        Args:
            variable_id (str): Variable ID
        
        Returns:
            tuple: (value, quality, timestamp, status) or (None, "Bad", None, "错误") if failed
        """
        variable = self.variable_manager.get_variable(variable_id)
        if not variable:
            logger.error(f"Variable with ID {variable_id} not found")
            return None, "Bad", None, "错误"
        
        # Queue the read request
        self.acquisition_queue.put(("read", variable))
        
        # Wait for result
        try:
            result = self.results_queue.get(timeout=5.0)
            if result[0] == variable_id:
                return result[1], result[2], result[3], result[4]
            else:
                logger.error(f"Unexpected result for variable {variable_id}: {result}")
                return None, "Bad", None, "错误"
        except queue.Empty:
            logger.error(f"Timeout waiting for read result of variable {variable_id}")
            return None, "Bad", None, "错误"
    
    def write_variable(self, variable_id, value):
        """Write a value to a variable.
        
        Args:
            variable_id (str): Variable ID
            value: Value to write
        
        Returns:
            bool: True if successful
        """
        variable = self.variable_manager.get_variable(variable_id)
        if not variable:
            logger.error(f"Variable with ID {variable_id} not found")
            return False
        
        # Queue the write request
        self.acquisition_queue.put(("write", variable, value))
        
        # Wait for result
        try:
            result = self.results_queue.get(timeout=5.0)
            if result[0] == variable_id:
                return result[1]
            else:
                logger.error(f"Unexpected result for variable {variable_id}: {result}")
                return False
        except queue.Empty:
            logger.error(f"Timeout waiting for write result of variable {variable_id}")
            return False
    
    def set_update_rate(self, rate):
        """Set the global update rate.
        
        Args:
            rate (float): Update rate in seconds
        """
        self.update_rate = max(0.1, float(rate))
        logger.info(f"Global update rate set to {self.update_rate} seconds")
    
    def set_variable_collection_frequency(self, variable_id, frequency):
        """Set collection frequency for a specific variable.
        
        Args:
            variable_id (str): Variable ID
            frequency (float): Collection frequency in seconds
            
        Returns:
            bool: True if successful
        """
        variable = self.variable_manager.get_variable(variable_id)
        if not variable:
            logger.error(f"Variable with ID {variable_id} not found")
            return False
            
        variable.set_acquisition_settings(collection_frequency=frequency)
        return True
    
    def set_variable_storage_settings(self, variable_id, storage_frequency=None, storage_enabled=None):
        """Set storage settings for a specific variable.
        
        Args:
            variable_id (str): Variable ID
            storage_frequency (float): Storage frequency in seconds
            storage_enabled (bool): Whether to store this variable's data
            
        Returns:
            bool: True if successful
        """
        variable = self.variable_manager.get_variable(variable_id)
        if not variable:
            logger.error(f"Variable with ID {variable_id} not found")
            return False
            
        variable.set_acquisition_settings(
            storage_frequency=storage_frequency,
            storage_enabled=storage_enabled
        )
        return True
    
    def set_logging(self, enabled, interval=60):
        """Configure global data logging.
        
        Args:
            enabled (bool): Enable or disable logging
            interval (int): Logging interval in seconds
        """
        self.logging_enabled = enabled
        self.logging_interval = max(1, int(interval))
        logger.info(f"Global logging {'enabled' if enabled else 'disabled'}, interval={self.logging_interval}s")
    
    def set_storage_location(self, location):
        """Set the storage location for logged data.
        
        Args:
            location (str): Directory path for storing data logs
        """
        if location:
            self.storage_location = location
            
            # Create storage directory if it doesn't exist
            if not os.path.exists(self.storage_location):
                try:
                    os.makedirs(self.storage_location)
                    logger.info(f"Created storage directory: {self.storage_location}")
                except Exception as e:
                    logger.error(f"Failed to create storage directory {self.storage_location}: {str(e)}")
                    return False
                    
            logger.info(f"Storage location set to: {self.storage_location}")
            return True
        return False
    
    def set_storage_format(self, format_type):
        """Set the storage format for logged data.
        
        Args:
            format_type (str): Storage format (json, csv)
        """
        if format_type.lower() in ["json", "csv"]:
            self.storage_format = format_type.lower()
            logger.info(f"Storage format set to: {self.storage_format}")
            return True
        else:
            logger.error(f"Unsupported storage format: {format_type}")
            return False
    
    def _acquisition_loop(self):
        """Main acquisition loop."""
        logger.info("Acquisition thread started")
        
        last_update_time = 0
        current_time = time.time() * 1000  # Current time in milliseconds
        
        while self.running:
            try:
                # Process any pending requests
                self._process_requests()
                
                # Check if it's time for the next update cycle
                current_time = time.time() * 1000
                if current_time - last_update_time >= self.update_rate * 1000:
                    # Update variables
                    self._update_all_variables(current_time)
                    last_update_time = current_time
                
                # Check if it's time to log data
                if self.logging_enabled and current_time - self.last_log_time >= self.logging_interval * 1000:
                    self._log_data(current_time)
                    self.last_log_time = current_time
                
                # Sleep briefly to avoid consuming too much CPU
                time.sleep(0.01)
                
            except Exception as e:
                logger.error(f"Error in acquisition loop: {str(e)}", exc_info=True)
                time.sleep(1)  # Sleep longer on error
    
    def _process_requests(self):
        """Process pending requests."""
        # Process up to 10 requests at a time to avoid blocking
        for _ in range(10):
            try:
                # Get request with a short timeout
                request = self.acquisition_queue.get(block=True, timeout=0.01)
                
                # Process request based on type
                if request[0] == "read":
                    self._read_variable(request[1])
                elif request[0] == "write":
                    self._write_variable(request[1], request[2])
                else:
                    logger.warning(f"Unknown request type: {request[0]}")
                
                # Mark request as done
                self.acquisition_queue.task_done()
                
            except queue.Empty:
                # No more requests
                break
            except Exception as e:
                logger.error(f"Error processing request: {str(e)}", exc_info=True)
    
    def _update_all_variables(self, current_time):
        """Update all variables based on their collection frequency."""
        for variable in self.variable_manager.get_all_variables():
            try:
                # Check if it's time to update this variable based on its collection frequency
                if current_time - variable.last_collection_time >= variable.collection_frequency * 1000:
                    self._read_variable(variable)
                    variable.last_collection_time = current_time
            except Exception as e:
                logger.error(f"Error updating variable {variable.name}: {str(e)}")
    
    def _read_variable(self, variable):
        """Read a variable's value.
        
        Args:
            variable (Variable): Variable to read
        """
        try:
            # Get protocol for variable
            protocol = self._get_protocol_for_variable(variable)
            if not protocol:
                # logger.error(f"No protocol available for variable {variable.name}")
                self.results_queue.put((variable.id, None, "Bad", None, "错误"))
                return
            
            # Prepare variable info for protocol
            var_info = {
                'address': variable.address,
                'data_type': variable.data_type
            }
            
            # Add protocol-specific parameters
            if variable.protocol_type == "S7":
                # Add DB number for S7 if address format is DB{num}.{offset}
                if isinstance(variable.address, str) and variable.address.startswith("DB"):
                    try:
                        parts = variable.address.split(".")
                        if len(parts) >= 2:
                            db_num = int(parts[0][2:])  # Extract number after "DB"
                            var_info['db_number'] = db_num
                    except (ValueError, IndexError):
                        pass
            
            elif variable.protocol_type == "Modbus":
                # Add register type for Modbus if address format is {type}:{address}
                if isinstance(variable.address, str) and ":" in variable.address:
                    try:
                        reg_type, addr = variable.address.split(":", 1)
                        var_info['register_type'] = reg_type
                        var_info['address'] = int(addr)
                    except (ValueError, IndexError):
                        pass
            
            elif variable.protocol_type == "CAN":
                # Add CAN ID for CAN if address is numeric
                try:
                    var_info['can_id'] = int(variable.address, 16 if isinstance(variable.address, str) and variable.address.startswith("0x") else 10)
                except (ValueError, TypeError):
                    pass
            
            elif variable.protocol_type == "GOOSE":
                # Add AppID for GOOSE
                if hasattr(variable, 'appid'):
                    var_info['appid'] = variable.appid
                else:
                    # Default AppID from address (if it looks like a hex string)
                    if isinstance(variable.address, str) and variable.address.startswith("0x"):
                        var_info['appid'] = variable.address
                    else:
                        var_info['appid'] = "0x1000"  # Default AppID
            
            # Read the variable
            value, quality = protocol.read_variable(var_info)
            
            # Update variable
            status = variable.set_value(value, quality)
            
            # Put result in results queue
            self.results_queue.put((variable.id, value, quality, variable.timestamp, status))
            
        except Exception as e:
            logger.error(f"Error reading variable {variable.name}: {str(e)}")
            self.results_queue.put((variable.id, None, "Bad", None, "错误"))
    
    def _write_variable(self, variable, value):
        """Write a value to a variable.
        
        Args:
            variable (Variable): Variable to write
            value: Value to write
        """
        try:
            # Get protocol for variable
            protocol = self._get_protocol_for_variable(variable)
            if not protocol:
                # TODO:No protocol available for variable
                # logger.error(f"No protocol available for variable {variable.name}")
                self.results_queue.put((variable.id, False))
                return
            
            # Prepare variable info for protocol
            var_info = {
                'address': variable.address,
                'data_type': variable.data_type,
                'value': value
            }
            
            # Add protocol-specific parameters (same as in _read_variable)
            if variable.protocol_type == "S7":
                # Add DB number for S7 if address format is DB{num}.{offset}
                if isinstance(variable.address, str) and variable.address.startswith("DB"):
                    try:
                        parts = variable.address.split(".")
                        if len(parts) >= 2:
                            db_num = int(parts[0][2:])  # Extract number after "DB"
                            var_info['db_number'] = db_num
                    except (ValueError, IndexError):
                        pass
            
            elif variable.protocol_type == "Modbus":
                # Add register type for Modbus if address format is {type}:{address}
                if isinstance(variable.address, str) and ":" in variable.address:
                    try:
                        reg_type, addr = variable.address.split(":", 1)
                        var_info['register_type'] = reg_type
                        var_info['address'] = int(addr)
                    except (ValueError, IndexError):
                        pass
            
            elif variable.protocol_type == "CAN":
                # Add CAN ID for CAN if address is numeric
                try:
                    var_info['can_id'] = int(variable.address, 16 if isinstance(variable.address, str) and variable.address.startswith("0x") else 10)
                except (ValueError, TypeError):
                    pass
            
            elif variable.protocol_type == "GOOSE":
                # Add AppID for GOOSE
                if hasattr(variable, 'appid'):
                    var_info['appid'] = variable.appid
                else:
                    # Default AppID from address (if it looks like a hex string)
                    if isinstance(variable.address, str) and variable.address.startswith("0x"):
                        var_info['appid'] = variable.address
                    else:
                        var_info['appid'] = "0x1000"  # Default AppID
            
            # Write the variable
            success = protocol.write_variable(var_info, value)
            
            # Update variable if write was successful
            if success:
                variable.set_value(value, "Good")
            
            # Put result in results queue
            self.results_queue.put((variable.id, success))
            
        except Exception as e:
            logger.error(f"Error writing variable {variable.name}: {str(e)}")
            self.results_queue.put((variable.id, False))
    
    def _get_protocol_for_variable(self, variable):
        """Get protocol instance for a variable.
        
        Args:
            variable (Variable): Variable
        
        Returns:
            object: Protocol instance or None if not available
        """
        # Get device-specific settings
        settings = self._get_device_settings(variable.device_id, variable.protocol_type)
        
        # Get protocol instance from factory
        return protocol_factory.get_protocol(variable.protocol_type, settings)
    
    def _get_device_settings(self, device_id, protocol_type):
        """Get device-specific settings.
        
        This is a placeholder implementation. In a real application,
        device settings would come from a configuration system.
        
        Args:
            device_id (str): Device ID
            protocol_type (str): Protocol type
        
        Returns:
            dict: Device settings
        """
        # Default settings based on protocol type
        if protocol_type == "S7":
            return {
                'ip': '192.168.0.1',
                'rack': 0,
                'slot': 1,
                'timeout': 5,
                'pdu_size': 480
            }
        elif protocol_type == "Modbus":
            return {
                'type': 'TCP',
                'ip': '192.168.0.1',
                'port': 502,
                'slave_id': 1,
                'timeout': 5
            }
        elif protocol_type == "CAN":
            return {
                'interface': 'can0',
                'bitrate': 500000,
                'extended': False
            }
        elif protocol_type == "GOOSE":
            return {
                'interface': 'eth0',
                'appid': '0x1000',
                'dst_mac': '01:0C:CD:01:00:00'
            }
        else:
            logger.warning(f"Unknown protocol type: {protocol_type}")
            return {}
    
    def _log_data(self, current_time):
        """Log current variable values based on their storage settings.
        
        Args:
            current_time (float): Current time in milliseconds
        """
        if not self.logging_enabled:
            return
        
        try:
            # Create storage directory if it doesn't exist
            if not os.path.exists(self.storage_location):
                os.makedirs(self.storage_location)
            
            # Create log filename with current date
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Variables to log in this cycle
            variables_to_log = {}
            
            # Check each variable to see if it should be logged
            for variable in self.variable_manager.get_all_variables():
                # Skip variables with storage disabled
                if not variable.storage_enabled:
                    continue
                    
                # Check if it's time to store this variable based on its storage frequency
                if current_time - variable.last_storage_time >= variable.storage_frequency * 1000:
                    variables_to_log[variable.id] = {
                        'id': variable.id,
                        'name': variable.name,
                        'value': variable.value,
                        'quality': variable.quality,
                        'timestamp': variable.timestamp,
                        'status': variable.status
                    }
                    variable.last_storage_time = current_time
            
            # Skip if no variables to log
            if not variables_to_log:
                return
                
            # Create log data
            log_data = {
                'timestamp': timestamp,
                'variables': variables_to_log
            }
            
            # Write log file based on format
            if self.storage_format == "json":
                log_file = os.path.join(self.storage_location, f"data_log_{timestamp}.json")
                with open(log_file, 'w') as f:
                    json.dump(log_data, f, indent=2)
            elif self.storage_format == "csv":
                log_file = os.path.join(self.storage_location, f"data_log_{timestamp}.csv")
                with open(log_file, 'w') as f:
                    # Write header
                    f.write("id,name,value,quality,timestamp,status\n")
                    # Write data for each variable
                    for var_data in variables_to_log.values():
                        f.write(f"{var_data['id']},{var_data['name']},{var_data['value']},"
                                f"{var_data['quality']},{var_data['timestamp']},{var_data['status']}\n")
            
            # logger.info(f"Data logged to {log_file} for {len(variables_to_log)} variables")
            
        except Exception as e:
            logger.error(f"Error logging data: {str(e)}", exc_info=True)
    
    def save_configuration(self, filename):
        """Save the current configuration to a file.
        
        Args:
            filename (str): Filename
        
        Returns:
            bool: True if successful
        """
        try:
            # Create config directory if it doesn't exist
            config_dir = os.path.dirname(filename)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            # Create configuration data
            config = {
                'variables': self.variable_manager.to_dict(),
                'settings': {
                    'update_rate': self.update_rate,
                    'logging_enabled': self.logging_enabled,
                    'logging_interval': self.logging_interval,
                    'storage_location': self.storage_location,
                    'storage_format': self.storage_format
                }
            }
            
            # Write configuration file
            with open(filename, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Configuration saved to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}", exc_info=True)
            return False
    
    def load_configuration(self, filename):
        """Load configuration from a file.
        
        Args:
            filename (str): Filename
        
        Returns:
            bool: True if successful
        """
        try:
            # Read configuration file
            with open(filename, 'r') as f:
                config = json.load(f)
            
            # Load variables
            if 'variables' in config:
                self.variable_manager.from_dict(config['variables'])
            
            # Load settings
            if 'settings' in config:
                settings = config['settings']
                if 'update_rate' in settings:
                    self.update_rate = float(settings['update_rate'])
                if 'logging_enabled' in settings:
                    self.logging_enabled = bool(settings['logging_enabled'])
                if 'logging_interval' in settings:
                    self.logging_interval = int(settings['logging_interval'])
                if 'storage_location' in settings:
                    self.storage_location = settings['storage_location']
                if 'storage_format' in settings:
                    self.storage_format = settings['storage_format']
            
            logger.info(f"Configuration loaded from {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}", exc_info=True)
            return False

# Create a singleton instance
acquisition_service = AcquisitionService() 