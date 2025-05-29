#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time
import struct
from pymodbus.client import ModbusTcpClient, ModbusSerialClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder, BinaryPayloadBuilder

logger = logging.getLogger(__name__)

class ModbusProtocol:
    """Class for handling Modbus communication."""
    
    def __init__(self, settings):
        """Initialize the Modbus protocol handler.
        
        Args:
            settings (dict): Connection settings
        """
        self.settings = settings
        self.client = None
        self.connected = False
    
    def connect(self):
        """Connect to the Modbus device."""
        try:
            # Create Modbus client based on type
            if self.settings.get('type') == 'TCP':
                # TCP connection
                ip = self.settings.get('ip', '127.0.0.1')
                port = self.settings.get('port', 502)
                timeout = self.settings.get('timeout', 5)
                
                self.client = ModbusTcpClient(
                    host=ip,
                    port=port,
                    timeout=timeout
                )
                
                logger.info(f"Connecting to Modbus TCP at {ip}:{port}")
            else:
                # RTU connection
                port = self.settings.get('port', 'COM1')
                baud = int(self.settings.get('baud', 9600))
                parity = self.settings.get('parity', 'N')[0].upper()
                data_bits = int(self.settings.get('data_bits', 8))
                stop_bits = int(self.settings.get('stop_bits', 1))
                timeout = self.settings.get('timeout', 5)
                
                self.client = ModbusSerialClient(
                    method='rtu',
                    port=port,
                    baudrate=baud,
                    parity=parity,
                    bytesize=data_bits,
                    stopbits=stop_bits,
                    timeout=timeout
                )
                
                logger.info(f"Connecting to Modbus RTU on {port}")
            
            # Try to connect
            if self.client.connect():
                self.connected = True
                logger.info("Modbus connection successful")
                return True
            else:
                logger.error("Failed to connect to Modbus device")
                return False
                
        except Exception as e:
            logger.error(f"Error connecting to Modbus device: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from the Modbus device."""
        if self.client and self.connected:
            try:
                self.client.close()
                self.connected = False
                logger.info("Disconnected from Modbus device")
                return True
            except Exception as e:
                logger.error(f"Error disconnecting from Modbus device: {str(e)}")
                return False
        return True
    
    def read_variable(self, variable):
        """Read a variable from the Modbus device.
        
        Args:
            variable (dict): Variable information with keys:
                - data_type: The data type (BOOL, BYTE, WORD, DWORD, INT, DINT, REAL, STRING)
                - address: The Modbus address (e.g., 40001, 10001, 30001, 00001)
                - size: Number of registers to read (for multi-register data types)
        
        Returns:
            tuple: (value, status)
                - value: The read value
                - status: True if successful, False otherwise
        """
        if not self.connected:
            logger.error("Cannot read variable: Not connected to Modbus device")
            return None, False
        
        try:
            data_type = variable.get('data_type')
            address = variable.get('address')
            
            if not data_type or not address:
                logger.error("Data type or address missing")
                return None, False
            
            # Convert string address to integer if necessary
            if isinstance(address, str):
                try:
                    address = int(address)
                except ValueError:
                    logger.error(f"Invalid address format: {address}")
                    return None, False
            
            # Get slave ID
            slave_id = int(self.settings.get('slave_id', 1))
            
            # Determine function code based on address range
            func_code = None
            real_address = None
            
            if address >= 1 and address <= 9999:  # Coils (00001-09999)
                func_code = 1  # Read Coils
                real_address = address - 1
            elif address >= 10001 and address <= 19999:  # Discrete Inputs (10001-19999)
                func_code = 2  # Read Discrete Inputs
                real_address = address - 10001
            elif address >= 30001 and address <= 39999:  # Input Registers (30001-39999)
                func_code = 4  # Read Input Registers
                real_address = address - 30001
            elif address >= 40001 and address <= 49999:  # Holding Registers (40001-49999)
                func_code = 3  # Read Holding Registers
                real_address = address - 40001
            else:
                # Try to determine based on standard Modicon addressing
                if address < 10000:
                    func_code = 3  # Assume Holding Register
                    real_address = address
                else:
                    logger.error(f"Address out of range: {address}")
                    return None, False
            
            # Read data based on function code
            if func_code == 1:  # Read Coils
                result = self.client.read_coils(real_address, 1, unit=slave_id)
                if not result.isError():
                    return result.bits[0], True
            
            elif func_code == 2:  # Read Discrete Inputs
                result = self.client.read_discrete_inputs(real_address, 1, unit=slave_id)
                if not result.isError():
                    return result.bits[0], True
            
            elif func_code in (3, 4):  # Read Holding or Input Registers
                # Determine number of registers to read based on data type
                count = 1
                if data_type in ('DWORD', 'DINT', 'REAL'):
                    count = 2
                elif data_type == 'STRING':
                    count = 8  # Assuming a 16-character string (8 registers)
                
                # Read registers
                if func_code == 3:
                    result = self.client.read_holding_registers(real_address, count, unit=slave_id)
                else:
                    result = self.client.read_input_registers(real_address, count, unit=slave_id)
                
                if not result.isError():
                    # Decode the value based on data type
                    decoder = BinaryPayloadDecoder.fromRegisters(
                        result.registers,
                        byteorder=Endian.Big,
                        wordorder=Endian.Little
                    )
                    
                    if data_type == 'BOOL':
                        # For BOOL, read first register and check LSB
                        return (result.registers[0] & 1) == 1, True
                    elif data_type == 'BYTE':
                        # For BYTE, read first register and get lower byte
                        return result.registers[0] & 0xFF, True
                    elif data_type == 'WORD' or data_type == 'INT':
                        # For WORD/INT, read as 16-bit value
                        if data_type == 'INT':
                            # Convert to signed
                            value = decoder.decode_16bit_int()
                        else:
                            value = decoder.decode_16bit_uint()
                        return value, True
                    elif data_type == 'DWORD':
                        return decoder.decode_32bit_uint(), True
                    elif data_type == 'DINT':
                        return decoder.decode_32bit_int(), True
                    elif data_type == 'REAL':
                        return decoder.decode_32bit_float(), True
                    elif data_type == 'STRING':
                        return decoder.decode_string(16), True
                    else:
                        logger.warning(f"Unsupported data type: {data_type}")
                        return result.registers[0], True
            
            logger.error(f"Error reading Modbus data: {result}")
            return None, False
            
        except Exception as e:
            logger.error(f"Error reading variable: {str(e)}")
            return None, False
    
    def write_variable(self, variable, value):
        """Write a value to a variable in the Modbus device.
        
        Args:
            variable (dict): Variable information with keys:
                - data_type: The data type (BOOL, BYTE, WORD, DWORD, INT, DINT, REAL, STRING)
                - address: The Modbus address (e.g., 40001, 00001)
            value: The value to write
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.connected:
            logger.error("Cannot write variable: Not connected to Modbus device")
            return False
        
        try:
            data_type = variable.get('data_type')
            address = variable.get('address')
            
            if not data_type or not address:
                logger.error("Data type or address missing")
                return False
            
            # Convert string address to integer if necessary
            if isinstance(address, str):
                try:
                    address = int(address)
                except ValueError:
                    logger.error(f"Invalid address format: {address}")
                    return False
            
            # Get slave ID
            slave_id = int(self.settings.get('slave_id', 1))
            
            # Determine function code based on address range
            func_code = None
            real_address = None
            
            if address >= 1 and address <= 9999:  # Coils (00001-09999)
                func_code = 5  # Write Single Coil
                real_address = address - 1
            elif address >= 40001 and address <= 49999:  # Holding Registers (40001-49999)
                func_code = 6  # Write Single Register
                real_address = address - 40001
            else:
                # Try to determine based on standard Modicon addressing
                if address < 10000:
                    func_code = 6  # Assume Holding Register
                    real_address = address
                else:
                    logger.error(f"Address out of range or not writable: {address}")
                    return False
            
            # Write data based on function code
            if func_code == 5:  # Write Single Coil
                # Convert value to boolean
                bool_value = bool(value)
                result = self.client.write_coil(real_address, bool_value, unit=slave_id)
                return not result.isError()
            
            elif func_code == 6:  # Write Single Register
                # Handle different data types
                if data_type in ('DWORD', 'DINT', 'REAL', 'STRING'):
                    # These types require multiple registers, use write_registers
                    builder = BinaryPayloadBuilder(
                        byteorder=Endian.Big,
                        wordorder=Endian.Little
                    )
                    
                    if data_type == 'DWORD':
                        builder.add_32bit_uint(int(value))
                    elif data_type == 'DINT':
                        builder.add_32bit_int(int(value))
                    elif data_type == 'REAL':
                        builder.add_32bit_float(float(value))
                    elif data_type == 'STRING':
                        builder.add_string(str(value))
                    
                    registers = builder.to_registers()
                    result = self.client.write_registers(real_address, registers, unit=slave_id)
                    return not result.isError()
                else:
                    # Single register types
                    int_value = int(value)
                    if data_type == 'BOOL':
                        # For boolean, write 0 or 1
                        int_value = 1 if bool(value) else 0
                    elif data_type == 'BYTE':
                        # For byte, ensure it's in range 0-255
                        int_value = int(value) & 0xFF
                    
                    result = self.client.write_register(real_address, int_value, unit=slave_id)
                    return not result.isError()
            
            logger.error("Unknown function code")
            return False
            
        except Exception as e:
            logger.error(f"Error writing variable: {str(e)}")
            return False 