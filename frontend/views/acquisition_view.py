#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QGroupBox, QFormLayout, QLineEdit, QComboBox,
    QSpinBox, QCheckBox, QTabWidget, QMessageBox,
    QLabel, QTextEdit, QScrollArea, QDoubleSpinBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from backend.services.acquisition_service import acquisition_service
from backend.services.config_service import config_service

logger = logging.getLogger(__name__)

class CommunicationThread(QThread):
    """Thread for handling communication with devices."""
    
    status_update = pyqtSignal(str)
    
    def __init__(self, protocol, settings, parent=None):
        super().__init__(parent)
        self.protocol = protocol
        self.settings = settings
        self.running = False
    
    def run(self):
        """Run the communication thread."""
        self.running = True
        
        self.status_update.emit(f"启动 {self.protocol} 通讯...")
        
        try:
            if self.protocol == "S7":
                self._run_s7()
            elif self.protocol == "Modbus":
                self._run_modbus()
            elif self.protocol == "CAN":
                self._run_can()
            elif self.protocol == "GOOSE":
                self._run_goose()
        except Exception as e:
            self.status_update.emit(f"通讯错误: {str(e)}")
            logger.error(f"Communication error: {str(e)}", exc_info=True)
        
        self.status_update.emit(f"{self.protocol} 通讯已停止")
        self.running = False
    
    def stop(self):
        """Stop the communication thread."""
        self.running = False
        self.wait()
    
    def _run_s7(self):
        """Run Siemens S7 communication."""
        import time
        
        self.status_update.emit(f"正在连接到 S7 PLC: {self.settings['ip']}...")
        
        # Simulate connection and communication
        time.sleep(1)
        
        if not self.running:
            return
        
        self.status_update.emit(f"S7 PLC 连接成功!")
        
        # Simulate data acquisition
        counter = 0
        while self.running:
            counter += 1
            self.status_update.emit(f"S7 数据包 #{counter}: 读取成功")
            time.sleep(2)
    
    def _run_modbus(self):
        """Run Modbus communication."""
        import time
        
        if self.settings['type'] == 'TCP':
            self.status_update.emit(f"正在连接到 Modbus TCP: {self.settings['ip']}:{self.settings['port']}...")
        else:
            self.status_update.emit(f"正在连接到 Modbus RTU: {self.settings['port']}...")
        
        # Simulate connection and communication
        time.sleep(1)
        
        if not self.running:
            return
        
        self.status_update.emit(f"Modbus 连接成功!")
        
        # Simulate data acquisition
        counter = 0
        while self.running:
            counter += 1
            self.status_update.emit(f"Modbus 数据包 #{counter}: 读取成功")
            time.sleep(2)
    
    def _run_can(self):
        """Run CAN communication."""
        import time
        
        self.status_update.emit(f"正在初始化 CAN 设备: {self.settings['interface']}...")
        
        # Simulate connection and communication
        time.sleep(1)
        
        if not self.running:
            return
        
        self.status_update.emit(f"CAN 设备初始化成功!")
        
        # Simulate data acquisition
        counter = 0
        while self.running:
            counter += 1
            self.status_update.emit(f"CAN 数据包 #{counter}: 读取成功")
            time.sleep(0.5)  # CAN is faster
    
    def _run_goose(self):
        """Run GOOSE communication."""
        import time
        
        self.status_update.emit(f"正在初始化 GOOSE 接口: {self.settings['interface']}...")
        
        # Simulate connection and communication
        time.sleep(1)
        
        if not self.running:
            return
        
        self.status_update.emit(f"GOOSE 接口初始化成功!")
        
        # Simulate data acquisition
        counter = 0
        while self.running:
            counter += 1
            self.status_update.emit(f"GOOSE 数据包 #{counter}: 读取成功")
            time.sleep(1)

class S7ConfigWidget(QWidget):
    """Widget for configuring Siemens S7 communication."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        
        # Connection settings
        connection_group = QGroupBox("连接设置")
        connection_layout = QFormLayout()
        
        self.ip_edit = QLineEdit("192.168.0.1")
        self.rack_spin = QSpinBox()
        self.rack_spin.setRange(0, 7)
        self.slot_spin = QSpinBox()
        self.slot_spin.setRange(0, 31)
        self.slot_spin.setValue(1)  # Default slot is often 1
        
        connection_layout.addRow("IP 地址:", self.ip_edit)
        connection_layout.addRow("机架号:", self.rack_spin)
        connection_layout.addRow("插槽号:", self.slot_spin)
        
        connection_group.setLayout(connection_layout)
        
        # Advanced settings
        advanced_group = QGroupBox("高级设置")
        advanced_layout = QFormLayout()
        
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 60)
        self.timeout_spin.setValue(5)
        self.timeout_spin.setSuffix(" 秒")
        
        self.pdu_size_combo = QComboBox()
        self.pdu_size_combo.addItems(["240", "480", "960", "1920"])
        
        advanced_layout.addRow("超时时间:", self.timeout_spin)
        advanced_layout.addRow("PDU 大小:", self.pdu_size_combo)
        
        advanced_group.setLayout(advanced_layout)
        
        # Add to main layout
        layout.addWidget(connection_group)
        layout.addWidget(advanced_group)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def get_settings(self):
        """Get the current S7 settings."""
        return {
            'ip': self.ip_edit.text(),
            'rack': self.rack_spin.value(),
            'slot': self.slot_spin.value(),
            'timeout': self.timeout_spin.value(),
            'pdu_size': self.pdu_size_combo.currentText()
        }

class ModbusConfigWidget(QWidget):
    """Widget for configuring Modbus communication."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        
        # Modbus type selection
        type_group = QGroupBox("Modbus 类型")
        type_layout = QVBoxLayout()
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["TCP", "RTU"])
        self.type_combo.currentTextChanged.connect(self.type_changed)
        
        type_layout.addWidget(self.type_combo)
        type_group.setLayout(type_layout)
        
        # TCP settings
        self.tcp_group = QGroupBox("TCP 设置")
        tcp_layout = QFormLayout()
        
        self.ip_edit = QLineEdit("192.168.0.1")
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(502)  # Default Modbus TCP port
        
        tcp_layout.addRow("IP 地址:", self.ip_edit)
        tcp_layout.addRow("端口:", self.port_spin)
        
        self.tcp_group.setLayout(tcp_layout)
        
        # RTU settings
        self.rtu_group = QGroupBox("RTU 设置")
        rtu_layout = QFormLayout()
        
        self.port_edit = QLineEdit("COM1")
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.parity_combo = QComboBox()
        self.parity_combo.addItems(["None", "Even", "Odd"])
        self.data_bits_combo = QComboBox()
        self.data_bits_combo.addItems(["7", "8"])
        self.data_bits_combo.setCurrentText("8")
        self.stop_bits_combo = QComboBox()
        self.stop_bits_combo.addItems(["1", "2"])
        
        rtu_layout.addRow("端口:", self.port_edit)
        rtu_layout.addRow("波特率:", self.baud_combo)
        rtu_layout.addRow("校验位:", self.parity_combo)
        rtu_layout.addRow("数据位:", self.data_bits_combo)
        rtu_layout.addRow("停止位:", self.stop_bits_combo)
        
        self.rtu_group.setLayout(rtu_layout)
        
        # Common settings
        common_group = QGroupBox("通用设置")
        common_layout = QFormLayout()
        
        self.slave_id_spin = QSpinBox()
        self.slave_id_spin.setRange(1, 247)
        self.slave_id_spin.setValue(1)
        
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 60)
        self.timeout_spin.setValue(5)
        self.timeout_spin.setSuffix(" 秒")
        
        common_layout.addRow("从站地址:", self.slave_id_spin)
        common_layout.addRow("超时时间:", self.timeout_spin)
        
        common_group.setLayout(common_layout)
        
        # Add to main layout
        layout.addWidget(type_group)
        layout.addWidget(self.tcp_group)
        layout.addWidget(self.rtu_group)
        layout.addWidget(common_group)
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Show/hide groups based on initial type
        self.type_changed(self.type_combo.currentText())
    
    def type_changed(self, type_text):
        """Update UI when Modbus type changes."""
        if type_text == "TCP":
            self.tcp_group.show()
            self.rtu_group.hide()
        else:
            self.tcp_group.hide()
            self.rtu_group.show()
    
    def get_settings(self):
        """Get the current Modbus settings."""
        type_text = self.type_combo.currentText()
        
        settings = {
            'type': type_text,
            'slave_id': self.slave_id_spin.value(),
            'timeout': self.timeout_spin.value()
        }
        
        if type_text == "TCP":
            settings.update({
                'ip': self.ip_edit.text(),
                'port': self.port_spin.value()
            })
        else:
            settings.update({
                'port': self.port_edit.text(),
                'baud': self.baud_combo.currentText(),
                'parity': self.parity_combo.currentText(),
                'data_bits': self.data_bits_combo.currentText(),
                'stop_bits': self.stop_bits_combo.currentText()
            })
        
        return settings

class CANConfigWidget(QWidget):
    """Widget for configuring CAN communication."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        
        # Interface settings
        interface_group = QGroupBox("接口设置")
        interface_layout = QFormLayout()
        
        self.interface_combo = QComboBox()
        self.interface_combo.addItems(["can0", "can1", "vcan0", "slcan0"])
        
        self.bitrate_combo = QComboBox()
        self.bitrate_combo.addItems(["125000", "250000", "500000", "1000000"])
        self.bitrate_combo.setCurrentText("500000")
        
        interface_layout.addRow("接口:", self.interface_combo)
        interface_layout.addRow("比特率:", self.bitrate_combo)
        
        interface_group.setLayout(interface_layout)
        
        # Filter settings
        filter_group = QGroupBox("过滤器设置")
        filter_layout = QFormLayout()
        
        self.filter_id_edit = QLineEdit()
        self.filter_id_edit.setPlaceholderText("例如: 0x123")
        
        self.filter_mask_edit = QLineEdit()
        self.filter_mask_edit.setPlaceholderText("例如: 0x7FF")
        
        self.extended_check = QCheckBox("使用扩展帧 (29位)")
        
        filter_layout.addRow("过滤器 ID:", self.filter_id_edit)
        filter_layout.addRow("过滤器掩码:", self.filter_mask_edit)
        filter_layout.addRow("", self.extended_check)
        
        filter_group.setLayout(filter_layout)
        
        # Add to main layout
        layout.addWidget(interface_group)
        layout.addWidget(filter_group)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def get_settings(self):
        """Get the current CAN settings."""
        return {
            'interface': self.interface_combo.currentText(),
            'bitrate': self.bitrate_combo.currentText(),
            'filter_id': self.filter_id_edit.text(),
            'filter_mask': self.filter_mask_edit.text(),
            'extended': self.extended_check.isChecked()
        }

class GOOSEConfigWidget(QWidget):
    """Widget for configuring GOOSE communication."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        
        # Interface settings
        interface_group = QGroupBox("接口设置")
        interface_layout = QFormLayout()
        
        self.interface_combo = QComboBox()
        self.interface_combo.addItems(["eth0", "eth1", "enp0s3", "enp0s8"])
        
        interface_layout.addRow("网络接口:", self.interface_combo)
        
        interface_group.setLayout(interface_layout)
        
        # GOOSE settings
        goose_group = QGroupBox("GOOSE 设置")
        goose_layout = QFormLayout()
        
        self.appid_edit = QLineEdit()
        self.appid_edit.setPlaceholderText("例如: 0x1000")
        
        self.dst_mac_edit = QLineEdit()
        self.dst_mac_edit.setPlaceholderText("例如: 01:0C:CD:01:00:00")
        self.dst_mac_edit.setText("01:0C:CD:01:00:00")  # Default GOOSE MAC
        
        self.gocb_ref_edit = QLineEdit()
        self.gocb_ref_edit.setPlaceholderText("例如: IED1CTRL/LLN0$GO$gcb01")
        
        goose_layout.addRow("AppID:", self.appid_edit)
        goose_layout.addRow("目标MAC:", self.dst_mac_edit)
        goose_layout.addRow("GoCB参考:", self.gocb_ref_edit)
        
        goose_group.setLayout(goose_layout)
        
        # Add to main layout
        layout.addWidget(interface_group)
        layout.addWidget(goose_group)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def get_settings(self):
        """Get the current GOOSE settings."""
        return {
            'interface': self.interface_combo.currentText(),
            'appid': self.appid_edit.text(),
            'dst_mac': self.dst_mac_edit.text(),
            'gocb_ref': self.gocb_ref_edit.text()
        }

class VariableSettingsWidget(QWidget):
    """Widget for configuring variable-specific acquisition and storage settings."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_variables()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        
        # Global settings
        global_group = QGroupBox("全局设置")
        global_layout = QFormLayout()
        
        self.update_rate_spin = QDoubleSpinBox()
        self.update_rate_spin.setRange(0.1, 3600)
        self.update_rate_spin.setValue(1.0)
        self.update_rate_spin.setSuffix(" 秒")
        self.update_rate_spin.setDecimals(1)
        
        self.logging_enabled_check = QCheckBox("启用数据记录")
        self.logging_enabled_check.setChecked(True)
        
        self.logging_interval_spin = QSpinBox()
        self.logging_interval_spin.setRange(1, 3600)
        self.logging_interval_spin.setValue(60)
        self.logging_interval_spin.setSuffix(" 秒")
        
        self.storage_location_edit = QLineEdit("logs")
        self.storage_location_btn = QPushButton("浏览...")
        self.storage_location_btn.clicked.connect(self.browse_storage_location)
        
        storage_location_layout = QHBoxLayout()
        storage_location_layout.addWidget(self.storage_location_edit)
        storage_location_layout.addWidget(self.storage_location_btn)
        
        self.storage_format_combo = QComboBox()
        self.storage_format_combo.addItems(["json", "csv"])
        
        global_layout.addRow("全局更新频率:", self.update_rate_spin)
        global_layout.addRow("", self.logging_enabled_check)
        global_layout.addRow("全局记录间隔:", self.logging_interval_spin)
        global_layout.addRow("存储位置:", storage_location_layout)
        global_layout.addRow("存储格式:", self.storage_format_combo)
        
        # Apply global settings button
        self.apply_global_btn = QPushButton("应用全局设置")
        self.apply_global_btn.clicked.connect(self.apply_global_settings)
        global_layout.addRow("", self.apply_global_btn)
        
        global_group.setLayout(global_layout)
        
        # Variable-specific settings
        variable_group = QGroupBox("变量设置")
        variable_layout = QVBoxLayout()
        
        # Variables table
        self.variables_table = QTableWidget()
        self.variables_table.setColumnCount(6)
        self.variables_table.setHorizontalHeaderLabels([
            "变量ID", "名称", "采集频率(秒)", "存储频率(秒)", "启用存储", "应用"
        ])
        self.variables_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.variables_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        
        variable_layout.addWidget(self.variables_table)
        
        # Refresh variables button
        self.refresh_btn = QPushButton("刷新变量列表")
        self.refresh_btn.clicked.connect(self.load_variables)
        variable_layout.addWidget(self.refresh_btn)
        
        variable_group.setLayout(variable_layout)
        
        # Add to main layout
        layout.addWidget(global_group)
        layout.addWidget(variable_group)
        
        self.setLayout(layout)
        
        # Load current settings
        self.load_global_settings()
    
    def load_global_settings(self):
        """Load global acquisition and storage settings."""
        try:
            # Get acquisition settings
            acq_settings = config_service.get_acquisition_settings()
            
            # Update UI
            self.update_rate_spin.setValue(acq_settings.get("update_rate", 1.0))
            self.logging_enabled_check.setChecked(acq_settings.get("logging_enabled", False))
            self.logging_interval_spin.setValue(acq_settings.get("logging_interval", 60))
            self.storage_location_edit.setText(acq_settings.get("storage_location", "logs"))
            
            # Set storage format
            format_index = self.storage_format_combo.findText(acq_settings.get("storage_format", "json"))
            if format_index >= 0:
                self.storage_format_combo.setCurrentIndex(format_index)
            
            logger.info("Global acquisition settings loaded")
        except Exception as e:
            logger.error(f"Error loading global settings: {str(e)}")
            QMessageBox.warning(self, "加载设置错误", f"加载全局设置时出错: {str(e)}")
    
    def apply_global_settings(self):
        """Apply global acquisition and storage settings."""
        try:
            # Get settings from UI
            update_rate = self.update_rate_spin.value()
            logging_enabled = self.logging_enabled_check.isChecked()
            logging_interval = self.logging_interval_spin.value()
            storage_location = self.storage_location_edit.text()
            storage_format = self.storage_format_combo.currentText()
            
            # Update acquisition service
            acquisition_service.set_update_rate(update_rate)
            acquisition_service.set_logging(logging_enabled, logging_interval)
            acquisition_service.set_storage_location(storage_location)
            acquisition_service.set_storage_format(storage_format)
            
            # Update config service
            acq_settings = {
                "update_rate": update_rate,
                "logging_enabled": logging_enabled,
                "logging_interval": logging_interval,
                "storage_location": storage_location,
                "storage_format": storage_format
            }
            config_service.set_acquisition_settings(acq_settings)
            config_service.save_config()
            
            logger.info("Global acquisition settings applied")
            QMessageBox.information(self, "设置已应用", "全局采集设置已应用")
        except Exception as e:
            logger.error(f"Error applying global settings: {str(e)}")
            QMessageBox.warning(self, "应用设置错误", f"应用全局设置时出错: {str(e)}")
    
    def load_variables(self):
        """Load variables and their acquisition settings."""
        try:
            # Clear table
            self.variables_table.setRowCount(0)
            
            # Get all variables
            variables = acquisition_service.get_all_variables()
            
            # Add variables to table
            self.variables_table.setRowCount(len(variables))
            
            for i, variable in enumerate(variables):
                # Variable ID (read-only)
                id_item = QTableWidgetItem(variable.id)
                id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
                self.variables_table.setItem(i, 0, id_item)
                
                # Variable name (read-only)
                name_item = QTableWidgetItem(variable.name)
                name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
                self.variables_table.setItem(i, 1, name_item)
                
                # Collection frequency
                collection_spin = QDoubleSpinBox()
                collection_spin.setRange(0.1, 3600)
                collection_spin.setValue(variable.collection_frequency)
                collection_spin.setSuffix(" 秒")
                collection_spin.setDecimals(1)
                self.variables_table.setCellWidget(i, 2, collection_spin)
                
                # Storage frequency
                storage_spin = QDoubleSpinBox()
                storage_spin.setRange(1, 3600)
                storage_spin.setValue(variable.storage_frequency)
                storage_spin.setSuffix(" 秒")
                storage_spin.setDecimals(1)
                self.variables_table.setCellWidget(i, 3, storage_spin)
                
                # Storage enabled
                storage_check = QCheckBox()
                storage_check.setChecked(variable.storage_enabled)
                storage_check_container = QWidget()
                storage_check_layout = QHBoxLayout(storage_check_container)
                storage_check_layout.addWidget(storage_check)
                storage_check_layout.setAlignment(Qt.AlignCenter)
                storage_check_layout.setContentsMargins(0, 0, 0, 0)
                self.variables_table.setCellWidget(i, 4, storage_check_container)
                
                # Apply button
                apply_btn = QPushButton("应用")
                apply_btn.variable_id = variable.id  # Store variable ID in the button
                apply_btn.clicked.connect(self.apply_variable_settings)
                self.variables_table.setCellWidget(i, 5, apply_btn)
            
            logger.info(f"Loaded {len(variables)} variables")
        except Exception as e:
            logger.error(f"Error loading variables: {str(e)}")
            QMessageBox.warning(self, "加载变量错误", f"加载变量列表时出错: {str(e)}")
    
    def apply_variable_settings(self):
        """Apply settings for a specific variable."""
        try:
            # Get the button that was clicked
            button = self.sender()
            variable_id = button.variable_id
            
            # Find the row for this variable
            for row in range(self.variables_table.rowCount()):
                if self.variables_table.item(row, 0).text() == variable_id:
                    # Get settings from UI
                    collection_spin = self.variables_table.cellWidget(row, 2)
                    storage_spin = self.variables_table.cellWidget(row, 3)
                    storage_check_container = self.variables_table.cellWidget(row, 4)
                    storage_check = storage_check_container.findChild(QCheckBox)
                    
                    collection_frequency = collection_spin.value()
                    storage_frequency = storage_spin.value()
                    storage_enabled = storage_check.isChecked()
                    
                    # Update acquisition service
                    acquisition_service.set_variable_collection_frequency(variable_id, collection_frequency)
                    acquisition_service.set_variable_storage_settings(
                        variable_id, 
                        storage_frequency=storage_frequency,
                        storage_enabled=storage_enabled
                    )
                    
                    # Update config service
                    config_service.update_variable_acquisition_settings(
                        variable_id,
                        collection_frequency=collection_frequency,
                        storage_frequency=storage_frequency,
                        storage_enabled=storage_enabled
                    )
                    config_service.save_config()
                    
                    logger.info(f"Variable {variable_id} settings applied")
                    QMessageBox.information(self, "设置已应用", f"变量 {variable_id} 的设置已应用")
                    break
        except Exception as e:
            logger.error(f"Error applying variable settings: {str(e)}")
            QMessageBox.warning(self, "应用设置错误", f"应用变量设置时出错: {str(e)}")
    
    def browse_storage_location(self):
        """Browse for storage location."""
        directory = QFileDialog.getExistingDirectory(
            self, 
            "选择存储位置", 
            self.storage_location_edit.text()
        )
        
        if directory:
            self.storage_location_edit.setText(directory)

class AcquisitionView(QWidget):
    """View for configuring and monitoring data acquisition."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.comm_thread = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout()
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Protocol configuration tab
        protocol_tab = QWidget()
        protocol_layout = QVBoxLayout()
        
        # Protocol selection
        protocol_group = QGroupBox("协议选择")
        protocol_selection = QHBoxLayout()
        
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["S7", "Modbus", "CAN", "GOOSE"])
        self.protocol_combo.currentTextChanged.connect(self.protocol_changed)
        
        protocol_selection.addWidget(QLabel("通讯协议:"))
        protocol_selection.addWidget(self.protocol_combo)
        protocol_selection.addStretch()
        
        protocol_group.setLayout(protocol_selection)
        protocol_layout.addWidget(protocol_group)
        
        # Protocol configuration
        self.config_stack = QTabWidget()
        
        # Create configuration widgets
        self.s7_config = S7ConfigWidget()
        self.modbus_config = ModbusConfigWidget()
        self.can_config = CANConfigWidget()
        self.goose_config = GOOSEConfigWidget()
        
        # Add widgets to stack
        self.config_stack.addTab(self.s7_config, "S7")
        self.config_stack.addTab(self.modbus_config, "Modbus")
        self.config_stack.addTab(self.can_config, "CAN")
        self.config_stack.addTab(self.goose_config, "GOOSE")
        
        protocol_layout.addWidget(self.config_stack)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("启动通讯")
        self.start_button.clicked.connect(self.start_current_protocol)
        
        self.stop_button = QPushButton("停止通讯")
        self.stop_button.clicked.connect(self.stop_current_protocol)
        self.stop_button.setEnabled(False)
        
        button_layout.addStretch()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        
        protocol_layout.addLayout(button_layout)
        
        # Communication log
        log_group = QGroupBox("通讯日志")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        
        protocol_layout.addWidget(log_group)
        
        protocol_tab.setLayout(protocol_layout)
        
        # Add protocol tab to tab widget
        self.tab_widget.addTab(protocol_tab, "通讯协议")
        
        # Add variable settings tab
        self.variable_settings = VariableSettingsWidget()
        self.tab_widget.addTab(self.variable_settings, "采集设置")
        
        main_layout.addWidget(self.tab_widget)
        
        self.setLayout(main_layout)
        
        # Set initial protocol
        self.protocol_changed(self.protocol_combo.currentText())
    
    def protocol_changed(self, protocol):
        """Handle protocol selection change."""
        # Set the current tab in the config stack
        index = self.protocol_combo.findText(protocol)
        if index >= 0:
            self.config_stack.setCurrentIndex(index)
    
    def log_message(self, message):
        """Add a message to the log."""
        self.log_text.append(message)
        # Scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def start_current_protocol(self):
        """Start communication with the current protocol."""
        # Stop any running thread
        self.stop_communication()
        
        # Get current protocol
        protocol = self.protocol_combo.currentText()
        
        # Get settings for the current protocol
        if protocol == "S7":
            settings = self.s7_config.get_settings()
        elif protocol == "Modbus":
            settings = self.modbus_config.get_settings()
        elif protocol == "CAN":
            settings = self.can_config.get_settings()
        elif protocol == "GOOSE":
            settings = self.goose_config.get_settings()
        else:
            QMessageBox.warning(self, "错误", f"未知协议: {protocol}")
            return
        
        # Start communication thread
        self.start_communication(protocol, settings)
    
    def stop_current_protocol(self):
        """Stop the current protocol communication."""
        self.stop_communication()
    
    def start_communication(self, protocol, settings):
        """Start communication with the specified protocol and settings."""
        self.comm_thread = CommunicationThread(protocol, settings, self)
        self.comm_thread.status_update.connect(self.log_message)
        self.comm_thread.start()
        
        # Update UI
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.log_message(f"正在启动 {protocol} 通讯...")
    
    def stop_communication(self):
        """Stop the current communication thread."""
        if self.comm_thread and self.comm_thread.isRunning():
            self.log_message("正在停止通讯...")
            self.comm_thread.stop()
            self.comm_thread = None
        
        # Update UI
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False) 