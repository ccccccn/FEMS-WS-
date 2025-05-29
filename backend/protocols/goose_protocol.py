#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time
import struct
import threading
import queue
import socket
import binascii

logger = logging.getLogger(__name__)

class GOOSEProtocol:
    """Class for handling IEC 61850 GOOSE protocol communication.
    
    This is a simplified implementation for educational purposes.
    A production implementation would need to use a full IEC 61850 library.
    """
    
    # GOOSE Ethertype
    GOOSE_ETHERTYPE = 0x88b8
    
    def __init__(self, settings):
        """Initialize the GOOSE protocol handler.
        
        Args:
            settings (dict): Connection settings
        """
        self.settings = settings
        self.socket = None
        self.connected = False
        self.receive_thread = None
        self.running = False
        self.callbacks = {}
        self.message_queue = queue.Queue()
    
    def connect(self):
        """Connect to the network interface for GOOSE communication."""
        try:
            interface = self.settings.get('interface', 'eth0')
            
            # Create raw socket
            self.socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(self.GOOSE_ETHERTYPE))
            
            # Bind to interface
            self.socket.bind((interface, 0))
            
            # Set timeout for recv
            self.socket.settimeout(0.1)
            
            # Get destination MAC from settings
            dst_mac = self.settings.get('dst_mac', '01:0C:CD:01:00:00')
            self.dst_mac_bytes = binascii.unhexlify(dst_mac.replace(':', ''))
            
            # Get AppID from settings
            appid = self.settings.get('appid', '0x1000')
            if isinstance(appid, str) and appid.startswith('0x'):
                self.appid = int(appid, 16)
            else:
                self.appid = int(appid)
            
            # Start receive thread
            self.running = True
            self.receive_thread = threading.Thread(target=self._receive_loop)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            
            self.connected = True
            logger.info(f"Connected to GOOSE on interface {interface}")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to GOOSE: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from the GOOSE interface."""
        if self.socket and self.connected:
            try:
                # Stop receive thread
                self.running = False
                if self.receive_thread:
                    self.receive_thread.join(timeout=1.0)
                
                # Close socket
                self.socket.close()
                self.connected = False
                logger.info("Disconnected from GOOSE interface")
                return True
            except Exception as e:
                logger.error(f"Error disconnecting from GOOSE: {str(e)}")
                return False
        return True
    
    def _receive_loop(self):
        """Background thread for receiving GOOSE messages."""
        logger.info("Starting GOOSE receive thread")
        
        while self.running:
            try:
                # Receive packet with timeout
                packet = self.socket.recv(1518)  # Maximum Ethernet frame size
                
                # Process GOOSE packet
                if len(packet) >= 14:  # Minimum size: dest MAC + src MAC + ethertype
                    # Extract destination MAC, source MAC, ethertype
                    dst_mac = packet[0:6]
                    src_mac = packet[6:12]
                    ethertype = (packet[12] << 8) | packet[13]
                    
                    # Check if this is a GOOSE packet
                    if ethertype == self.GOOSE_ETHERTYPE:
                        # Parse GOOSE header
                        if len(packet) >= 22:  # Basic GOOSE header size
                            appid = (packet[14] << 8) | packet[15]
                            length = (packet[16] << 8) | packet[17]
                            reserved1 = (packet[18] << 8) | packet[19]
                            reserved2 = (packet[20] << 8) | packet[21]
                            
                            # Extract GOOSE data
                            goose_data = packet[22:22+length]
                            
                            # Process GOOSE data (simplified)
                            logger.debug(f"Received GOOSE: AppID={appid:x}, length={length}")
                            
                            # Put message on queue
                            goose_msg = {
                                'src_mac': src_mac,
                                'dst_mac': dst_mac,
                                'appid': appid,
                                'data': goose_data
                            }
                            self.message_queue.put(goose_msg)
                            
                            # Process callbacks
                            for cb_appid, callback in self.callbacks.items():
                                if cb_appid == appid:
                                    callback(goose_msg)
            except socket.timeout:
                # Expected timeout, continue
                pass
            except Exception as e:
                logger.error(f"Error in GOOSE receive loop: {str(e)}")
                time.sleep(0.1)  # Prevent tight loop on error
        
        logger.info("GOOSE receive thread stopped")
    
    def register_callback(self, appid, callback):
        """Register a callback for a specific GOOSE AppID.
        
        Args:
            appid (int): The GOOSE AppID to listen for
            callback (function): Callback function that will receive the GOOSE message
        """
        self.callbacks[appid] = callback
    
    def unregister_callback(self, appid):
        """Unregister a callback for a specific GOOSE AppID.
        
        Args:
            appid (int): The GOOSE AppID to stop listening for
        """
        if appid in self.callbacks:
            del self.callbacks[appid]
    
    def read_variable(self, variable):
        """Read a variable from GOOSE messages.
        
        Note: GOOSE is a publish/subscribe protocol, so this method
        simulates a read by waiting for the next message with the
        specified AppID and data index.
        
        Args:
            variable (dict): Variable information with keys:
                - appid: The GOOSE AppID to read
                - data_type: The data type (BOOL, BYTE, WORD, DWORD, INT, DINT, REAL)
                - index: Data index in the GOOSE message
        
        Returns:
            tuple: (value, status)
                - value: The read value
                - status: True if successful, False otherwise
        """
        if not self.connected:
            logger.error("Cannot read variable: Not connected to GOOSE interface")
            return None, False
        
        try:
            appid = variable.get('appid')
            data_type = variable.get('data_type')
            index = variable.get('index', 0)
            
            if not appid or not data_type:
                logger.error("AppID or data type missing")
                return None, False
            
            # Convert string hex to int if needed
            if isinstance(appid, str) and appid.startswith('0x'):
                appid = int(appid, 16)
            elif isinstance(appid, str):
                appid = int(appid)
            
            # Wait for next message with this AppID
            timeout = self.settings.get('timeout', 1.0)
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    # Try to get message from queue
                    msg = self.message_queue.get(block=False)
                    
                    # Check if this is the message we're looking for
                    if msg['appid'] == appid:
                        # Parse data based on type and index
                        data = msg['data']
                        if len(data) > index:
                            return self._parse_goose_data(data[index:], data_type), True
                        else:
                            logger.warning(f"GOOSE message index out of range: {index} >= {len(data)}")
                except queue.Empty:
                    # No message available, wait a bit
                    time.sleep(0.01)
            
            logger.warning(f"Timeout waiting for GOOSE AppID: {appid:x}")
            return None, False
            
        except Exception as e:
            logger.error(f"Error reading GOOSE variable: {str(e)}")
            return None, False
    
    def send_goose(self, goose_data):
        """Send a GOOSE message.
        
        Args:
            goose_data (bytes): GOOSE data to send
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.connected:
            logger.error("Cannot send GOOSE: Not connected to GOOSE interface")
            return False
        
        try:
            # Create Ethernet header: dst MAC (6) + src MAC (6) + ethertype (2)
            # Get interface hardware address (MAC)
            if_addr = self.socket.getsockname()[4]
            
            # Create packet: dst MAC + src MAC + ethertype + GOOSE header + data
            packet = bytearray()
            
            # Add destination MAC
            packet.extend(self.dst_mac_bytes)
            
            # Add source MAC
            packet.extend(if_addr)
            
            # Add ethertype
            packet.append((self.GOOSE_ETHERTYPE >> 8) & 0xFF)
            packet.append(self.GOOSE_ETHERTYPE & 0xFF)
            
            # Add GOOSE header: APPID (2) + Length (2) + Reserved1 (2) + Reserved2 (2)
            packet.append((self.appid >> 8) & 0xFF)
            packet.append(self.appid & 0xFF)
            
            # Length
            length = len(goose_data)
            packet.append((length >> 8) & 0xFF)
            packet.append(length & 0xFF)
            
            # Reserved fields
            packet.append(0)
            packet.append(0)
            packet.append(0)
            packet.append(0)
            
            # Add GOOSE data
            packet.extend(goose_data)
            
            # Send packet
            self.socket.send(packet)
            logger.debug(f"Sent GOOSE message: AppID={self.appid:x}, length={length}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending GOOSE message: {str(e)}")
            return False
    
    def write_variable(self, variable, value):
        """Write a value to a GOOSE message.
        
        Note: This is a simplified implementation for educational purposes.
        Production systems would use a full IEC 61850 library.
        
        Args:
            variable (dict): Variable information with keys:
                - data_type: The data type (BOOL, BYTE, WORD, DWORD, INT, DINT, REAL)
                - index: Position in the GOOSE data
            value: The value to write
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.connected:
            logger.error("Cannot write variable: Not connected to GOOSE interface")
            return False
        
        try:
            data_type = variable.get('data_type')
            index = variable.get('index', 0)
            
            if not data_type:
                logger.error("Data type missing")
                return False
            
            # Create GOOSE data (simplified)
            # In a real implementation, this would construct an ASN.1 encoded GOOSE message
            
            # For this simple example, we'll just create a data array
            data = bytearray(20)  # Arbitrary size
            
            # Set the value at the specified index
            data_bytes = self._create_goose_data(value, data_type)
            for i, b in enumerate(data_bytes):
                if index + i < len(data):
                    data[index + i] = b
            
            # Send the GOOSE message
            return self.send_goose(data)
            
        except Exception as e:
            logger.error(f"Error writing GOOSE variable: {str(e)}")
            return False
    
    def _parse_goose_data(self, data, data_type):
        """Parse GOOSE data based on data type.
        
        Args:
            data (bytes): Raw GOOSE data
            data_type (str): Data type
        
        Returns:
            The parsed value
        """
        if data_type == 'BOOL':
            return data[0] != 0
        elif data_type == 'BYTE':
            return data[0]
        elif data_type == 'WORD':
            return (data[0] << 8) | data[1] if len(data) >= 2 else 0
        elif data_type == 'INT':
            return struct.unpack('>h', data[:2])[0] if len(data) >= 2 else 0
        elif data_type == 'DWORD':
            return (data[0] << 24) | (data[1] << 16) | (data[2] << 8) | data[3] if len(data) >= 4 else 0
        elif data_type == 'DINT':
            return struct.unpack('>i', data[:4])[0] if len(data) >= 4 else 0
        elif data_type == 'REAL':
            return struct.unpack('>f', data[:4])[0] if len(data) >= 4 else 0
        else:
            logger.warning(f"Unknown data type: {data_type}")
            return int.from_bytes(data, byteorder='big')
    
    def _create_goose_data(self, value, data_type):
        """Create GOOSE data based on data type.
        
        Args:
            value: The value to encode
            data_type (str): Data type
        
        Returns:
            bytes: The encoded GOOSE data
        """
        if data_type == 'BOOL':
            return bytes([1 if value else 0])
        elif data_type == 'BYTE':
            return bytes([value & 0xFF])
        elif data_type == 'WORD':
            return ((value >> 8) & 0xFF).to_bytes(1, 'big') + (value & 0xFF).to_bytes(1, 'big')
        elif data_type == 'INT':
            return struct.pack('>h', value)
        elif data_type == 'DWORD':
            return value.to_bytes(4, 'big')
        elif data_type == 'DINT':
            return struct.pack('>i', value)
        elif data_type == 'REAL':
            return struct.pack('>f', float(value))
        else:
            logger.warning(f"Unknown data type: {data_type}")
            # Default to treating as raw bytes
            if isinstance(value, bytes):
                return value
            else:
                return str(value).encode('utf-8') 