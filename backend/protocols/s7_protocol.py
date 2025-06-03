#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time
import snap7
from snap7.util import get_bool, get_int, get_real, get_string
from snap7.snap7types import S7WLBit, S7WLByte, S7WLWord, S7WLDWord, S7WLReal, S7WLString

logger = logging.getLogger(__name__)

class S7Protocol:
    """Class for handling Siemens S7 PLC communication."""
    
    # Data type mapping
    DATA_TYPES = {
        'BOOL': S7WLBit,
        'BYTE': S7WLByte,
        'WORD': S7WLWord,
        'DWORD': S7WLDWord,
        'INT': S7WLWord,
        'DINT': S7WLDWord,
        'REAL': S7WLReal,
        'STRING': S7WLString
    }
    
    def __init__(self, ip, rack=0, slot=1, timeout=5, pdu_size=480):
        """Initialize the S7 protocol handler.
        
        Args:
            ip (str): IP address of the PLC
            rack (int): Rack number (default: 0)
            slot (int): Slot number (default: 1)
            timeout (int): Connection timeout in seconds (default: 5)
            pdu_size (int): PDU size (default: 480)
        """
        self.ip = ip
        self.rack = rack
        self.slot = slot
        self.timeout = timeout
        self.pdu_size = int(pdu_size)
        self.client = None
        self.connected = False
    
    def connect(self):
        """Connect to the S7 PLC."""
        try:
            self.client = snap7.client.Client()
            self.client.set_connection_params(self.ip, self.rack, self.slot)
            self.client.connect()
            
            if self.client.get_connected():
                logger.info(f"Connected to S7 PLC at {self.ip}")
                self.connected = True
                return True
            else:
                logger.error(f"Failed to connect to S7 PLC at {self.ip}")
                return False
        except Exception as e:
            logger.error(f"Error connecting to S7 PLC: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from the S7 PLC."""
        if self.client and self.connected:
            try:
                self.client.disconnect()
                self.connected = False
                logger.info(f"Disconnected from S7 PLC at {self.ip}")
                return True
            except Exception as e:
                logger.error(f"Error disconnecting from S7 PLC: {str(e)}")
                return False
        return True
    
    def read_variable(self, variable):
        """Read a variable from the PLC.
        
        Args:
            variable (dict): Variable information with keys:
                - data_type: The data type (BOOL, BYTE, WORD, DWORD, INT, DINT, REAL, STRING)
                - address: The address in S7 format (e.g., DB1.DBX0.0, M10.0, I0.1, Q0.1)
        
        Returns:
            tuple: (value, status) 
                - value: The read value
                - status: True if successful, False otherwise
        """
        if not self.connected:
            logger.error("Cannot read variable: Not connected to PLC")
            return None, False
        
        try:
            data_type = variable.get('data_type')
            address = variable.get('address')
            
            if not data_type or not address:
                logger.error("Data type or address missing")
                return None, False
            
            # Parse address
            if address.startswith('DB'):
                # DB address (e.g., DB1.DBX0.0, DB1.DBD0)
                parts = address.split('.')
                if len(parts) < 2:
                    logger.error(f"Invalid DB address format: {address}")
                    return None, False
                
                db_number = int(parts[0].replace('DB', ''))
                var_address = parts[1]
                
                # Extract offset and bit (if applicable)
                offset = int(var_address[3:].split('.')[0])
                bit = 0
                if '.' in var_address and data_type == 'BOOL':
                    bit = int(var_address.split('.')[1])
                
                # Read data block
                data = self.client.db_read(db_number, offset, self._get_size(data_type))
                
                # Convert data based on type
                value = self._convert_data(data, data_type, bit)
                return value, True
                
            elif address.startswith('M'):
                # Memory address (e.g., M10.0)
                offset = int(address[1:].split('.')[0])
                bit = 0
                if '.' in address and data_type == 'BOOL':
                    bit = int(address.split('.')[1])
                
                # Read memory
                data = self.client.read_area(snap7.types.areas.MK, 0, offset, self._get_size(data_type))
                
                # Convert data based on type
                value = self._convert_data(data, data_type, bit)
                return value, True
                
            elif address.startswith('I'):
                # Input address (e.g., I0.1)
                offset = int(address[1:].split('.')[0])
                bit = 0
                if '.' in address and data_type == 'BOOL':
                    bit = int(address.split('.')[1])
                
                # Read input
                data = self.client.read_area(snap7.types.areas.PE, 0, offset, self._get_size(data_type))
                
                # Convert data based on type
                value = self._convert_data(data, data_type, bit)
                return value, True
                
            elif address.startswith('Q'):
                # Output address (e.g., Q0.1)
                offset = int(address[1:].split('.')[0])
                bit = 0
                if '.' in address and data_type == 'BOOL':
                    bit = int(address.split('.')[1])
                
                # Read output
                data = self.client.read_area(snap7.types.areas.PA, 0, offset, self._get_size(data_type))
                
                # Convert data based on type
                value = self._convert_data(data, data_type, bit)
                return value, True
            
            else:
                logger.error(f"Unsupported address format: {address}")
                return None, False
                
        except Exception as e:
            logger.error(f"Error reading variable: {str(e)}")
            return None, False
    
    def write_variable(self, variable, value):
        """Write a value to a variable in the PLC.
        
        Args:
            variable (dict): Variable information with keys:
                - data_type: The data type (BOOL, BYTE, WORD, DWORD, INT, DINT, REAL, STRING)
                - address: The address in S7 format (e.g., DB1.DBX0.0, M10.0, Q0.1)
            value: The value to write
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.connected:
            logger.error("Cannot write variable: Not connected to PLC")
            return False
        
        try:
            data_type = variable.get('data_type')
            address = variable.get('address')
            
            if not data_type or not address:
                logger.error("Data type or address missing")
                return False
            
            # Parse address
            if address.startswith('DB'):
                # DB address (e.g., DB1.DBX0.0, DB1.DBD0)
                parts = address.split('.')
                if len(parts) < 2:
                    logger.error(f"Invalid DB address format: {address}")
                    return False
                
                db_number = int(parts[0].replace('DB', ''))
                var_address = parts[1]
                
                # Extract offset and bit (if applicable)
                offset = int(var_address[3:].split('.')[0])
                bit = 0
                if '.' in var_address and data_type == 'BOOL':
                    bit = int(var_address.split('.')[1])
                
                # Read current data block
                size = self._get_size(data_type)
                data = self.client.db_read(db_number, offset, size)
                
                # Modify data based on type
                self._set_value(data, data_type, value, bit)
                
                # Write data back to PLC
                self.client.db_write(db_number, offset, data)
                return True
                
            elif address.startswith('M'):
                # Memory address (e.g., M10.0)
                offset = int(address[1:].split('.')[0])
                bit = 0
                if '.' in address and data_type == 'BOOL':
                    bit = int(address.split('.')[1])
                
                # Read current memory
                size = self._get_size(data_type)
                data = self.client.read_area(snap7.types.areas.MK, 0, offset, size)
                
                # Modify data based on type
                self._set_value(data, data_type, value, bit)
                
                # Write data back to PLC
                self.client.write_area(snap7.types.areas.MK, 0, offset, data)
                return True
                
            elif address.startswith('Q'):
                # Output address (e.g., Q0.1)
                offset = int(address[1:].split('.')[0])
                bit = 0
                if '.' in address and data_type == 'BOOL':
                    bit = int(address.split('.')[1])
                
                # Read current output
                size = self._get_size(data_type)
                data = self.client.read_area(snap7.types.areas.PA, 0, offset, size)
                
                # Modify data based on type
                self._set_value(data, data_type, value, bit)
                
                # Write data back to PLC
                self.client.write_area(snap7.types.areas.PA, 0, offset, data)
                return True
            
            else:
                logger.error(f"Unsupported address format: {address}")
                return False
                
        except Exception as e:
            logger.error(f"Error writing variable: {str(e)}")
            return False
    
    def _get_size(self, data_type):
        """Get the size in bytes for a data type.
        
        Args:
            data_type (str): The data type
        
        Returns:
            int: Size in bytes
        """
        if data_type == 'BOOL':
            return 1
        elif data_type in ('BYTE', 'CHAR'):
            return 1
        elif data_type in ('WORD', 'INT'):
            return 2
        elif data_type in ('DWORD', 'DINT', 'REAL'):
            return 4
        elif data_type == 'STRING':
            return 256  # Maximum string size
        else:
            logger.warning(f"Unknown data type: {data_type}, using default size of 1")
            return 1
    
    def _convert_data(self, data, data_type, bit=0):
        """Convert raw data to Python value.
        
        Args:
            data (bytearray): Raw data from PLC
            data_type (str): The data type
            bit (int): Bit index for BOOL types
        
        Returns:
            The converted value
        """
        if data_type == 'BOOL':
            return get_bool(data, 0, bit)
        elif data_type == 'BYTE':
            return data[0]
        elif data_type == 'WORD':
            return get_int(data, 0)
        elif data_type == 'DWORD':
            return get_int(data, 0)
        elif data_type == 'INT':
            return get_int(data, 0)
        elif data_type == 'DINT':
            return get_int(data, 0)
        elif data_type == 'REAL':
            return get_real(data, 0)
        elif data_type == 'STRING':
            return get_string(data, 0, 256)
        else:
            logger.warning(f"Unknown data type: {data_type}")
            return None
    
    def _set_value(self, data, data_type, value, bit=0):
        """Set a value in a bytearray.
        
        Args:
            data (bytearray): Raw data buffer
            data_type (str): The data type
            value: The value to set
            bit (int): Bit index for BOOL types
            
        Returns:
            bytearray: Modified data
        """
        if data_type == 'BOOL':
            snap7.util.set_bool(data, 0, bit, value)
        elif data_type == 'BYTE':
            data[0] = value
        elif data_type == 'WORD':
            snap7.util.set_int(data, 0, value)
        elif data_type == 'DWORD':
            snap7.util.set_dword(data, 0, value)
        elif data_type == 'INT':
            snap7.util.set_int(data, 0, value)
        elif data_type == 'DINT':
            snap7.util.set_dint(data, 0, value)
        elif data_type == 'REAL':
            snap7.util.set_real(data, 0, value)
        elif data_type == 'STRING':
            snap7.util.set_string(data, 0, value, 256)
        else:
            logger.warning(f"Unknown data type: {data_type}")
        
        return data 