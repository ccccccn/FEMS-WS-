#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QPushButton, QDoubleSpinBox, QCheckBox,
    QGroupBox, QComboBox, QLineEdit, QFileDialog
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from backend.services.config_service import config_service
from backend.services.acquisition_service import acquisition_service

logger = logging.getLogger(__name__)

class VariableSettingsWidget(QWidget):
    """Widget for configuring variable acquisition and storage settings."""
    
    settings_changed = pyqtSignal()  # Emitted when settings are changed
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_variable = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)
        
        # Global settings group
        global_group = QGroupBox("全局采集设置")
        global_layout = QFormLayout()
        
        # Global update rate
        self.global_update_rate = QDoubleSpinBox()
        self.global_update_rate.setRange(0.1, 3600)
        self.global_update_rate.setDecimals(1)
        self.global_update_rate.setSuffix(" 秒")
        self.global_update_rate.setValue(1.0)
        self.global_update_rate.valueChanged.connect(self.on_global_update_rate_changed)
        global_layout.addRow("全局更新频率:", self.global_update_rate)
        
        # Global logging settings
        self.global_logging_enabled = QCheckBox("启用数据记录")
        self.global_logging_enabled.stateChanged.connect(self.on_global_logging_changed)
        global_layout.addRow("", self.global_logging_enabled)
        
        self.global_logging_interval = QDoubleSpinBox()
        self.global_logging_interval.setRange(1, 3600)
        self.global_logging_interval.setDecimals(0)
        self.global_logging_interval.setSuffix(" 秒")
        self.global_logging_interval.setValue(60)
        self.global_logging_interval.valueChanged.connect(self.on_global_logging_interval_changed)
        global_layout.addRow("全局记录间隔:", self.global_logging_interval)
        
        global_group.setLayout(global_layout)
        main_layout.addWidget(global_group)
        
        # Storage settings group
        storage_group = QGroupBox("存储设置")
        storage_layout = QFormLayout()
        
        # Storage location
        storage_location_layout = QHBoxLayout()
        self.storage_location = QLineEdit()
        self.storage_location.setPlaceholderText("数据存储路径")
        self.storage_location.textChanged.connect(self.on_storage_location_changed)
        
        self.browse_button = QPushButton("浏览...")
        self.browse_button.clicked.connect(self.browse_storage_location)
        
        storage_location_layout.addWidget(self.storage_location)
        storage_location_layout.addWidget(self.browse_button)
        storage_layout.addRow("存储位置:", storage_location_layout)
        
        # Storage format
        self.storage_format = QComboBox()
        self.storage_format.addItems(["JSON", "CSV"])
        self.storage_format.currentTextChanged.connect(self.on_storage_format_changed)
        storage_layout.addRow("存储格式:", self.storage_format)
        
        storage_group.setLayout(storage_layout)
        main_layout.addWidget(storage_group)
        
        # Variable-specific settings group
        variable_group = QGroupBox("变量采集设置")
        variable_layout = QFormLayout()
        
        # Variable collection frequency
        self.collection_frequency = QDoubleSpinBox()
        self.collection_frequency.setRange(0.1, 3600)
        self.collection_frequency.setDecimals(1)
        self.collection_frequency.setSuffix(" 秒")
        self.collection_frequency.setValue(1.0)
        self.collection_frequency.valueChanged.connect(self.on_collection_frequency_changed)
        variable_layout.addRow("采集频率:", self.collection_frequency)
        
        # Variable storage frequency
        self.storage_frequency = QDoubleSpinBox()
        self.storage_frequency.setRange(1, 3600)
        self.storage_frequency.setDecimals(1)
        self.storage_frequency.setSuffix(" 秒")
        self.storage_frequency.setValue(60.0)
        self.storage_frequency.valueChanged.connect(self.on_storage_frequency_changed)
        variable_layout.addRow("存储频率:", self.storage_frequency)
        
        # Storage enabled
        self.storage_enabled = QCheckBox("启用存储")
        self.storage_enabled.setChecked(True)
        self.storage_enabled.stateChanged.connect(self.on_storage_enabled_changed)
        variable_layout.addRow("", self.storage_enabled)
        
        variable_group.setLayout(variable_layout)
        main_layout.addWidget(variable_group)
        
        # Help text
        help_text = (
            "说明：\n"
            "1. 全局更新频率控制整个系统的基础采集周期\n"
            "2. 变量采集频率可以单独设置，优先级高于全局设置\n"
            "3. 存储频率控制将变量数据保存到存储位置的间隔\n"
            "4. 可以单独启用或禁用每个变量的存储功能"
        )
        help_label = QLabel(help_text)
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: #666; font-style: italic;")
        main_layout.addWidget(help_label)
        
        # Add stretch to push everything to the top
        main_layout.addStretch(1)
        
        # Load initial settings
        self.load_settings()
    
    def load_settings(self):
        """Load settings from the config service."""
        try:
            # Load global acquisition settings
            acq_settings = config_service.get_acquisition_settings()
            self.global_update_rate.setValue(acq_settings.get("update_rate", 1.0))
            self.global_logging_enabled.setChecked(acq_settings.get("logging_enabled", False))
            self.global_logging_interval.setValue(acq_settings.get("logging_interval", 60))
            
            # Load storage settings
            storage_settings = config_service.get_storage_settings()
            self.storage_location.setText(storage_settings.get("location", "logs"))
            format_index = self.storage_format.findText(storage_settings.get("format", "JSON").upper())
            if format_index >= 0:
                self.storage_format.setCurrentIndex(format_index)
            
            logger.info("Settings loaded successfully")
        except Exception as e:
            logger.error(f"Error loading settings: {str(e)}")
    
    def set_variable(self, variable):
        """Set the current variable and load its settings.
        
        Args:
            variable: Variable object
        """
        self.current_variable = variable
        
        if variable:
            # Update variable-specific settings
            self.collection_frequency.setValue(variable.collection_frequency)
            self.storage_frequency.setValue(variable.storage_frequency)
            self.storage_enabled.setChecked(variable.storage_enabled)
            
            # Enable variable-specific controls
            self.collection_frequency.setEnabled(True)
            self.storage_frequency.setEnabled(True)
            self.storage_enabled.setEnabled(True)
        else:
            # Disable variable-specific controls
            self.collection_frequency.setEnabled(False)
            self.storage_frequency.setEnabled(False)
            self.storage_enabled.setEnabled(False)
    
    def on_global_update_rate_changed(self, value):
        """Handle global update rate change."""
        try:
            acquisition_service.set_update_rate(value)
            config_service.set_acquisition_settings({
                "update_rate": value,
                "logging_enabled": self.global_logging_enabled.isChecked(),
                "logging_interval": int(self.global_logging_interval.value())
            })
            self.settings_changed.emit()
            logger.info(f"Global update rate set to {value} seconds")
        except Exception as e:
            logger.error(f"Error setting global update rate: {str(e)}")
    
    def on_global_logging_changed(self, state):
        """Handle global logging enabled change."""
        try:
            enabled = state == Qt.Checked
            interval = int(self.global_logging_interval.value())
            acquisition_service.set_logging(enabled, interval)
            config_service.set_acquisition_settings({
                "update_rate": self.global_update_rate.value(),
                "logging_enabled": enabled,
                "logging_interval": interval
            })
            self.settings_changed.emit()
            logger.info(f"Global logging {'enabled' if enabled else 'disabled'}")
        except Exception as e:
            logger.error(f"Error setting global logging: {str(e)}")
    
    def on_global_logging_interval_changed(self, value):
        """Handle global logging interval change."""
        try:
            enabled = self.global_logging_enabled.isChecked()
            interval = int(value)
            acquisition_service.set_logging(enabled, interval)
            config_service.set_acquisition_settings({
                "update_rate": self.global_update_rate.value(),
                "logging_enabled": enabled,
                "logging_interval": interval
            })
            self.settings_changed.emit()
            logger.info(f"Global logging interval set to {interval} seconds")
        except Exception as e:
            logger.error(f"Error setting global logging interval: {str(e)}")
    
    def on_storage_location_changed(self, location):
        """Handle storage location change."""
        try:
            acquisition_service.set_storage_location(location)
            config_service.set_storage_settings(
                location=location,
                format_type=self.storage_format.currentText().lower()
            )
            self.settings_changed.emit()
            logger.info(f"Storage location set to {location}")
        except Exception as e:
            logger.error(f"Error setting storage location: {str(e)}")
    
    def on_storage_format_changed(self, format_type):
        """Handle storage format change."""
        try:
            acquisition_service.set_storage_format(format_type.lower())
            config_service.set_storage_settings(
                location=self.storage_location.text(),
                format_type=format_type.lower()
            )
            self.settings_changed.emit()
            logger.info(f"Storage format set to {format_type}")
        except Exception as e:
            logger.error(f"Error setting storage format: {str(e)}")
    
    def browse_storage_location(self):
        """Open a file dialog to select storage location."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择存储位置",
            self.storage_location.text()
        )
        if directory:
            self.storage_location.setText(directory)
    
    def on_collection_frequency_changed(self, value):
        """Handle variable collection frequency change."""
        if not self.current_variable:
            return
        
        try:
            # Update variable and service
            self.current_variable.set_acquisition_settings(collection_frequency=value)
            acquisition_service.set_variable_collection_frequency(self.current_variable.id, value)
            
            # Update config
            config_service.update_variable_acquisition_settings(
                self.current_variable.id,
                collection_frequency=value
            )
            
            self.settings_changed.emit()
            logger.info(f"Variable {self.current_variable.name} collection frequency set to {value} seconds")
        except Exception as e:
            logger.error(f"Error setting variable collection frequency: {str(e)}")
    
    def on_storage_frequency_changed(self, value):
        """Handle variable storage frequency change."""
        if not self.current_variable:
            return
        
        try:
            # Update variable and service
            self.current_variable.set_acquisition_settings(storage_frequency=value)
            acquisition_service.set_variable_storage_settings(
                self.current_variable.id,
                storage_frequency=value
            )
            
            # Update config
            config_service.update_variable_acquisition_settings(
                self.current_variable.id,
                storage_frequency=value
            )
            
            self.settings_changed.emit()
            logger.info(f"Variable {self.current_variable.name} storage frequency set to {value} seconds")
        except Exception as e:
            logger.error(f"Error setting variable storage frequency: {str(e)}")
    
    def on_storage_enabled_changed(self, state):
        """Handle variable storage enabled change."""
        if not self.current_variable:
            return
        
        try:
            enabled = state == Qt.Checked
            
            # Update variable and service
            self.current_variable.set_acquisition_settings(storage_enabled=enabled)
            acquisition_service.set_variable_storage_settings(
                self.current_variable.id,
                storage_enabled=enabled
            )
            
            # Update config
            config_service.update_variable_acquisition_settings(
                self.current_variable.id,
                storage_enabled=enabled
            )
            
            self.settings_changed.emit()
            logger.info(f"Variable {self.current_variable.name} storage {'enabled' if enabled else 'disabled'}")
        except Exception as e:
            logger.error(f"Error setting variable storage enabled: {str(e)}") 