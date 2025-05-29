#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time
import struct
import threading
import queue
import can

logger = logging.getLogger(__name__)

class CANProtocol:
    """Class for handling CAN bus communication."""
    
    def __init__(self, settings):
        """Initialize the CAN protocol handler.
        
        Args:
            settings (dict): Connection settings
        """
        self.settings = settings
        self.bus = None
        self.connected = False
        self.receive_thread = None
        self.running = False
        self.callbacks = {}
        self.message_queue = queue.Queue()
    
    def connect(self):
        """Connect to the CAN bus."""
        try:
            interface = self.settings.get('interface', 'can0')
            bitrate = int(self.settings.get('bitrate', 500000))
            
            # Create CAN bus
            self.bus = can.interface.Bus(
                channel=interface,
                bustype='socketcan',
                bitrate=bitrate
            )
            
            # Set up filters if specified
            filter_id = self.settings.get('filter_id')
            filter_mask = self.settings.get('filter_mask')
            extended = self.settings.get('extended', False)
            
            if filter_id and filter_mask:
                # Convert string hex to int if needed
                if isinstance(filter_id, str) and filter_id.startswith('0x'):
                    filter_id = int(filter_id, 16)
                else:
                    filter_id = int(filter_id)
                
                if isinstance(filter_mask, str) and filter_mask.startswith('0x'):
                    filter_mask = int(filter_mask, 16)
                else:
                    filter_mask = int(filter_mask)
                
                # Apply filter
                can_filter = [{"can_id": filter_id, "can_mask": filter_mask, "extended": extended}]
                self.bus.set_filters(can_filter)
                logger.info(f"Applied CAN filter: ID={filter_id:x}, mask={filter_mask:x}, extended={extended}")
            
            # Start receive thread
            self.running = True
            self.receive_thread = threading.Thread(target=self._receive_loop)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            
            self.connected = True
            logger.info(f"Connected to CAN bus on {interface}")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to CAN bus: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from the CAN bus."""
        if self.bus and self.connected:
            try:
                # Stop receive thread
                self.running = False
                if self.receive_thread:
                    self.receive_thread.join(timeout=1.0)
                
                # Close bus
                self.bus.shutdown()
                self.connected = False
                logger.info("Disconnected from CAN bus")
                return True
            except Exception as e:
                logger.error(f"Error disconnecting from CAN bus: {str(e)}")
                return False
        return True
    
    def _receive_loop(self):
        """Background thread for receiving CAN messages."""
        logger.info("Starting CAN receive thread")
        
        while self.running:
            try:
                # Receive message with timeout
                msg = self.bus.recv(timeout=0.1)
                if msg is not None:
                    # Put message on queue
                    self.message_queue.put(msg)
                    
                    # Process callbacks
                    for can_id, callback in self.callbacks.items():
                        if can_id == msg.arbitration_id:
                            callback(msg)
                    
                    logger.debug(f"Received CAN message: ID={msg.arbitration_id:x}, data={msg.data.hex()}")
            except Exception as e:
                logger.error(f"Error in CAN receive loop: {str(e)}")
                time.sleep(0.1)  # Prevent tight loop on error
        
        logger.info("CAN receive thread stopped")
    
    def register_callback(self, can_id, callback):
        """Register a callback for a specific CAN ID.
        
        Args:
            can_id (int): The CAN ID to listen for
            callback (function): Callback function that will receive the CAN message
        """
        self.callbacks[can_id] = callback
    
    def unregister_callback(self, can_id):
        """Unregister a callback for a specific CAN ID.
        
        Args:
            can_id (int): The CAN ID to stop listening for
        """
        if can_id in self.callbacks:
            del self.callbacks[can_id]
    
    def read_variable(self, variable):
        """Read a variable from the CAN bus.
        
        Note: This is not a typical operation for CAN, as it's a
        broadcast medium. This method simulates a read by waiting
        for the next message with the specified CAN ID.
        
        Args:
            variable (dict): Variable information with keys:
                - can_id: The CAN ID to read
                - data_type: The data type (BOOL, BYTE, WORD, DWORD, INT, DINT, REAL)
                - byte_order: Byte order ('little' or 'big')
                - start_bit: Starting bit for bit-level variables
                - length: Length in bits for bit-level variables
        
        Returns:
            tuple: (value, status)
                - value: The read value
                - status: True if successful, False otherwise
        """
        if not self.connected:
            logger.error("Cannot read variable: Not connected to CAN bus")
            return None, False
        
        try:
            can_id = variable.get('can_id')
            data_type = variable.get('data_type')
            
            if not can_id or not data_type:
                logger.error("CAN ID or data type missing")
                return None, False
            
            # Convert string hex to int if needed
            if isinstance(can_id, str) and can_id.startswith('0x'):
                can_id = int(can_id, 16)
            elif isinstance(can_id, str):
                can_id = int(can_id)
            
            # Get byte order
            byte_order = variable.get('byte_order', 'little')
            
            # Wait for next message with this ID
            timeout = self.settings.get('timeout', 1.0)
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    # Try to get message from queue
                    msg = self.message_queue.get(block=False)
                    
                    # Check if this is the message we're looking for
                    if msg.arbitration_id == can_id:
                        # Parse data based on type
                        return self._parse_can_data(msg.data, data_type, variable, byte_order), True
                except queue.Empty:
                    # No message available, wait a bit
                    time.sleep(0.01)
            
            logger.warning(f"Timeout waiting for CAN ID: {can_id:x}")
            return None, False
            
        except Exception as e:
            logger.error(f"Error reading CAN variable: {str(e)}")
            return None, False
    
    def write_variable(self, variable, value):
        """Write a value to the CAN bus.
        
        Args:
            variable (dict): Variable information with keys:
                - can_id: The CAN ID to write to
                - data_type: The data type (BOOL, BYTE, WORD, DWORD, INT, DINT, REAL)
                - byte_order: Byte order ('little' or 'big')
                - start_bit: Starting bit for bit-level variables
                - length: Length in bits for bit-level variables
            value: The value to write
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.connected:
            logger.error("Cannot write variable: Not connected to CAN bus")
            return False
        
        try:
            can_id = variable.get('can_id')
            data_type = variable.get('data_type')
            
            if not can_id or not data_type:
                logger.error("CAN ID or data type missing")
                return False
            
            # Convert string hex to int if needed
            if isinstance(can_id, str) and can_id.startswith('0x'):
                can_id = int(can_id, 16)
            elif isinstance(can_id, str):
                can_id = int(can_id)
            
            # Get byte order
            byte_order = variable.get('byte_order', 'little')
            
            # Check if extended ID
            extended = self.settings.get('extended', False)
            
            # Create data based on type
            data = self._create_can_data(value, data_type, variable, byte_order)
            
            # Create and send message
            msg = can.Message(
                arbitration_id=can_id,
                data=data,
                is_extended_id=extended
            )
            
            self.bus.send(msg)
            logger.debug(f"Sent CAN message: ID={can_id:x}, data={data.hex()}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing CAN variable: {str(e)}")
            return False
    
    def _parse_can_data(self, data, data_type, variable, byte_order):
        """Parse CAN data based on data type.
        
        Args:
            data (bytes): Raw CAN data
            data_type (str): Data type
            variable (dict): Variable information
            byte_order (str): Byte order ('little' or 'big')
        
        Returns:
            The parsed value
        """
        # Check if bit-level access
        start_bit = variable.get('start_bit')
        length = variable.get('length')
        
        if start_bit is not None and length is not None:
            # Convert to int for bit manipulation
            value = int.from_bytes(data, byteorder=byte_order)
            
            # Create mask and extract bits
            mask = ((1 << length) - 1) << start_bit
            return (value & mask) >> start_bit
        
        # Byte-level access
        if data_type == 'BOOL':
            return data[0] & 1 == 1
        elif data_type == 'BYTE':
            return data[0]
        elif data_type == 'WORD':
            return int.from_bytes(data[:2], byteorder=byte_order)
        elif data_type == 'INT':
            return struct.unpack('<h' if byte_order == 'little' else '>h', data[:2])[0]
        elif data_type == 'DWORD':
            return int.from_bytes(data[:4], byteorder=byte_order)
        elif data_type == 'DINT':
            return struct.unpack('<i' if byte_order == 'little' else '>i', data[:4])[0]
        elif data_type == 'REAL':
            return struct.unpack('<f' if byte_order == 'little' else '>f', data[:4])[0]
        else:
            logger.warning(f"Unknown data type: {data_type}")
            return int.from_bytes(data, byteorder=byte_order)
    
    def _create_can_data(self, value, data_type, variable, byte_order):
        """Create CAN data based on data type.
        
        Args:
            value: The value to encode
            data_type (str): Data type
            variable (dict): Variable information
            byte_order (str): Byte order ('little' or 'big')
        
        Returns:
            bytes: The encoded CAN data
        """
        # Initialize empty data (8 bytes for standard CAN)
        data = bytearray(8)
        
        # Check if bit-level access
        start_bit = variable.get('start_bit')
        length = variable.get('length')
        
        if start_bit is not None and length is not None:
            # Read current data bytes as integer
            current_value = int.from_bytes(data, byteorder=byte_order)
            
            # Create mask for the bits we want to change
            mask = ((1 << length) - 1) << start_bit
            
            # Clear the bits we want to change
            current_value &= ~mask
            
            # Set the new bits
            new_value = current_value | ((int(value) & ((1 << length) - 1)) << start_bit)
            
            # Convert back to bytes
            data = new_value.to_bytes(8, byteorder=byte_order)
        else:
            # Byte-level access
            if data_type == 'BOOL':
                data[0] = 1 if value else 0
            elif data_type == 'BYTE':
                data[0] = value & 0xFF
            elif data_type == 'WORD':
                int_value = int(value) & 0xFFFF
                data[:2] = int_value.to_bytes(2, byteorder=byte_order)
            elif data_type == 'INT':
                data[:2] = struct.pack('<h' if byte_order == 'little' else '>h', int(value))
            elif data_type == 'DWORD':
                int_value = int(value) & 0xFFFFFFFF
                data[:4] = int_value.to_bytes(4, byteorder=byte_order)
            elif data_type == 'DINT':
                data[:4] = struct.pack('<i' if byte_order == 'little' else '>i', int(value))
            elif data_type == 'REAL':
                data[:4] = struct.pack('<f' if byte_order == 'little' else '>f', float(value))
            else:
                logger.warning(f"Unknown data type: {data_type}")
                # Default to treating as raw bytes
                if isinstance(value, bytes):
                    for i, b in enumerate(value[:8]):
                        data[i] = b
                else:
                    int_value = int(value)
                    for i in range(min(8, (int_value.bit_length() + 7) // 8)):
                        data[i] = (int_value >> (i * 8)) & 0xFF
        
        return data 