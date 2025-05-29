#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import csv
import io
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableView, QHeaderView, QDialog, QFormLayout,
    QLineEdit, QComboBox, QDialogButtonBox, QMessageBox,
    QLabel, QGroupBox, QSplitter, QTabWidget, QCheckBox,
    QDoubleSpinBox, QAbstractItemView, QSpinBox,
    QFileDialog, QPlainTextEdit, QListWidget, QListWidgetItem,
    QStackedWidget
)
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QFont, QColor

from frontend.models.variable_model import Variable
from frontend.views.variable_settings_widget import VariableSettingsWidget
from datetime import datetime

logger = logging.getLogger(__name__)

class VariableTableModel(QAbstractTableModel):
    """Table model for displaying variables."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.variables = []
        self.headers = ["变量ID", "变量名", "数据类型", "地址", "状态", "当前值", "描述"]
    
    def rowCount(self, parent=QModelIndex()):
        return len(self.variables)
    
    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self.variables)):
            return QVariant()
        
        variable = self.variables[index.row()]
        column = index.column()
        
        if role == Qt.DisplayRole:
            if column == 0:
                return variable.variable_id[:8] + "..."  # Truncate long ID
            elif column == 1:
                return variable.name
            elif column == 2:
                return variable.data_type
            elif column == 3:
                return variable.address
            elif column == 4:
                return variable.status
            elif column == 5:
                # Display value with units if available
                if variable.current_value is None:
                    return "未知"
                value_str = str(variable.current_value)
                if variable.units:
                    value_str += f" {variable.units}"
                return value_str
            elif column == 6:
                return variable.description
        
        elif role == Qt.BackgroundRole:
            # Color based on status
            if column == 4:
                if variable.status == "报警":
                    return QColor(255, 100, 100, 150)  # Red for alarm
                elif variable.status == "警告":
                    return QColor(255, 200, 50, 150)  # Yellow for warning
                else:
                    return QColor(100, 255, 100, 100)  # Green for normal
            
            # Alternate row colors for better readability
            if index.row() % 2 == 0:
                return QColor(240, 240, 240, 40)
        
        return QVariant()
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return QVariant()
    
    def set_variables(self, variables):
        """Set the variables to display."""
        self.beginResetModel()
        self.variables = variables
        self.endResetModel()
    
    def get_variable(self, row):
        """Get the variable at the specified row."""
        if 0 <= row < len(self.variables):
            return self.variables[row]
        return None
    
    def update_variable(self, variable):
        """Update a variable in the model."""
        for i, var in enumerate(self.variables):
            if var.variable_id == variable.variable_id:
                self.variables[i] = variable
                self.dataChanged.emit(
                    self.index(i, 0),
                    self.index(i, self.columnCount() - 1)
                )
                break

class AddVariableDialog(QDialog):
    """Dialog for adding a new variable."""
    
    def __init__(self, device_type, parent=None):
        super().__init__(parent)
        self.device_type = device_type
        self.setWindowTitle("添加变量")
        self.setMinimumWidth(500)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the dialog UI."""
        layout = QVBoxLayout()
        
        # Create tab widget for variable properties and thresholds
        self.tab_widget = QTabWidget()
        
        # Basic properties tab
        basic_tab = QWidget()
        basic_layout = QFormLayout(basic_tab)
        
        # Variable name
        self.name_edit = QLineEdit()
        basic_layout.addRow("变量名:", self.name_edit)
        
        # Data type
        self.data_type_combo = QComboBox()
        self.data_type_combo.addItems(["BOOL", "BYTE", "WORD", "DWORD", "INT", "DINT", "REAL", "STRING"])
        basic_layout.addRow("数据类型:", self.data_type_combo)
        
        # Address
        self.address_edit = QLineEdit()
        basic_layout.addRow("地址:", self.address_edit)
        
        # Protocol-specific help label
        if self.device_type == "S7":
            address_help = "格式: DB1.DBX0.0 或 DB1.DBW2 或 M10.0"
        elif self.device_type == "Modbus":
            address_help = "格式: 40001 (保持寄存器) 或 10001 (输入状态)"
        elif self.device_type == "CAN":
            address_help = "格式: 信号名称或ID.起始位.位长度"
        elif self.device_type == "GOOSE":
            address_help = "格式: 数据集.成员索引"
        else:
            address_help = ""
        
        address_help_label = QLabel(address_help)
        address_help_label.setStyleSheet("color: #666; font-style: italic;")
        basic_layout.addRow("", address_help_label)
        
        # Description
        self.description_edit = QLineEdit()
        basic_layout.addRow("描述:", self.description_edit)
        
        # Units
        self.units_edit = QLineEdit()
        basic_layout.addRow("单位:", self.units_edit)
        
        # Threshold tab
        threshold_tab = QWidget()
        threshold_layout = QVBoxLayout(threshold_tab)
        
        # Enable thresholds
        self.threshold_enabled = QCheckBox("启用阈值监控")
        threshold_layout.addWidget(self.threshold_enabled)
        
        # Threshold group
        threshold_group = QGroupBox("阈值设置")
        threshold_form = QFormLayout()
        
        # Warning thresholds
        self.warning_low = QDoubleSpinBox()
        self.warning_low.setRange(-999999, 999999)
        self.warning_low.setDecimals(2)
        threshold_form.addRow("警告下限:", self.warning_low)
        
        self.warning_high = QDoubleSpinBox()
        self.warning_high.setRange(-999999, 999999)
        self.warning_high.setDecimals(2)
        self.warning_high.setValue(100)
        threshold_form.addRow("警告上限:", self.warning_high)
        
        # Alarm thresholds
        self.alarm_low = QDoubleSpinBox()
        self.alarm_low.setRange(-999999, 999999)
        self.alarm_low.setDecimals(2)
        threshold_form.addRow("报警下限:", self.alarm_low)
        
        self.alarm_high = QDoubleSpinBox()
        self.alarm_high.setRange(-999999, 999999)
        self.alarm_high.setDecimals(2)
        self.alarm_high.setValue(120)
        threshold_form.addRow("报警上限:", self.alarm_high)
        
        threshold_group.setLayout(threshold_form)
        threshold_layout.addWidget(threshold_group)
        
        # Threshold info
        info_text = "阈值说明：\n"
        info_text += "1. 变量值低于警告下限或高于警告上限时，状态变为\"警告\"\n"
        info_text += "2. 变量值低于报警下限或高于报警上限时，状态变为\"报警\"\n"
        info_text += "3. 默认值0表示不启用该阈值"
        
        info_label = QLabel(info_text)
        info_label.setStyleSheet("color: #666; font-style: italic;")
        info_label.setWordWrap(True)
        threshold_layout.addWidget(info_label)
        
        # Data source tab
        data_source_tab = QWidget()
        data_source_layout = QFormLayout(data_source_tab)
        
        # API endpoint for real-time data
        self.api_enabled = QCheckBox("使用API获取实时数据")
        data_source_layout.addRow("", self.api_enabled)
        
        self.api_endpoint_edit = QLineEdit()
        self.api_endpoint_edit.setPlaceholderText("例如: /api/data/{device_id}/{variable_id}")
        data_source_layout.addRow("API端点:", self.api_endpoint_edit)
        
        # Polling interval
        self.polling_interval_spin = QSpinBox()
        self.polling_interval_spin.setRange(100, 60000)  # 100ms to 60s
        self.polling_interval_spin.setValue(1000)  # Default 1s
        self.polling_interval_spin.setSuffix(" ms")
        data_source_layout.addRow("轮询间隔:", self.polling_interval_spin)
        
        # API info
        api_info_text = "API说明：\n"
        api_info_text += "1. API端点用于从后端获取实时数据\n"
        api_info_text += "2. 可以使用{device_id}和{variable_id}作为占位符\n"
        api_info_text += "3. 轮询间隔决定了数据刷新的频率"
        
        api_info_label = QLabel(api_info_text)
        api_info_label.setStyleSheet("color: #666; font-style: italic;")
        api_info_label.setWordWrap(True)
        data_source_layout.addRow("", api_info_label)
        
        # Enable/disable API fields based on checkbox
        self.api_enabled.stateChanged.connect(self.toggle_api_fields)
        
        # Add tabs to tab widget
        self.tab_widget.addTab(basic_tab, "基本属性")
        self.tab_widget.addTab(threshold_tab, "阈值设置")
        self.tab_widget.addTab(data_source_tab, "数据源")
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # Add to main layout
        layout.addWidget(self.tab_widget)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # Initialize API fields state
        self.toggle_api_fields()
    
    def toggle_api_fields(self):
        """Enable or disable API fields based on checkbox state."""
        enabled = self.api_enabled.isChecked()
        self.api_endpoint_edit.setEnabled(enabled)
        self.polling_interval_spin.setEnabled(enabled)
    
    def get_variable_data(self):
        """Get variable data from the dialog."""
        variable = Variable(
            name=self.name_edit.text(),
            data_type=self.data_type_combo.currentText(),
            address=self.address_edit.text(),
            description=self.description_edit.text()
        )
        
        # Set units
        variable.units = self.units_edit.text()
        
        # Set threshold values if enabled
        if self.threshold_enabled.isChecked():
            variable.set_threshold(
                enabled=True,
                warning_low=self.warning_low.value() if self.warning_low.value() != 0 else None,
                warning_high=self.warning_high.value() if self.warning_high.value() != 0 else None,
                alarm_low=self.alarm_low.value() if self.alarm_low.value() != 0 else None,
                alarm_high=self.alarm_high.value() if self.alarm_high.value() != 0 else None
            )
        
        # Set API endpoint if enabled
        if self.api_enabled.isChecked() and self.api_endpoint_edit.text().strip():
            variable.set_api_endpoint(
                endpoint=self.api_endpoint_edit.text().strip(),
                polling_interval=self.polling_interval_spin.value()
            )
        
        return variable

class BatchImportVariableDialog(QDialog):
    """Dialog for batch importing variables."""
    
    def __init__(self, device_type, parent=None):
        super().__init__(parent)
        self.device_type = device_type
        self.setWindowTitle("批量导入变量")
        self.setMinimumSize(800, 600)
        self.variables = []
        self.init_ui()
    
    def init_ui(self):
        """Initialize the dialog UI."""
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel("您可以通过以下两种方式批量导入变量：")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # File import section
        file_group = QGroupBox("从CSV文件导入")
        file_layout = QVBoxLayout()
        
        file_help = QLabel("CSV文件应包含以下列：name,data_type,address,description,units")
        file_help.setWordWrap(True)
        file_layout.addWidget(file_help)
        
        # Add template download button
        template_layout = QHBoxLayout()
        template_label = QLabel("不确定格式？下载模板文件：")
        self.download_template_btn = QPushButton("下载模板")
        self.download_template_btn.clicked.connect(self.download_template)
        template_layout.addWidget(template_label)
        template_layout.addWidget(self.download_template_btn)
        template_layout.addStretch(1)
        file_layout.addLayout(template_layout)
        
        file_btn_layout = QHBoxLayout()
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setReadOnly(True)
        self.file_path_edit.setPlaceholderText("选择CSV文件...")
        
        self.browse_btn = QPushButton("浏览...")
        self.browse_btn.clicked.connect(self.browse_file)
        
        file_btn_layout.addWidget(self.file_path_edit)
        file_btn_layout.addWidget(self.browse_btn)
        
        file_layout.addLayout(file_btn_layout)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Text import section
        text_group = QGroupBox("从文本导入")
        text_layout = QVBoxLayout()
        
        text_help = QLabel("请输入CSV格式的文本，每行一个变量，列应为：name,data_type,address,description,units")
        text_help.setWordWrap(True)
        text_layout.addWidget(text_help)
        
        protocol_help = QLabel(f"当前设备类型: {self.device_type}")
        protocol_help.setStyleSheet("font-weight: bold; color: #2a82da;")
        text_layout.addWidget(protocol_help)
        
        # Add protocol-specific address format help
        if self.device_type == "S7":
            address_help = "地址格式: DB1.DBX0.0 或 DB1.DBW2 或 M10.0"
        elif self.device_type == "Modbus":
            address_help = "地址格式: 40001 (保持寄存器) 或 10001 (输入状态)"
        elif self.device_type == "CAN":
            address_help = "地址格式: 信号名称或ID.起始位.位长度"
        elif self.device_type == "GOOSE":
            address_help = "地址格式: 数据集.成员索引"
        else:
            address_help = ""
        
        address_help_label = QLabel(address_help)
        address_help_label.setStyleSheet("color: #666; font-style: italic;")
        text_layout.addWidget(address_help_label)
        
        self.csv_text_edit = QPlainTextEdit()
        self.csv_text_edit.setPlaceholderText("例如：\n温度,REAL,DB1.DBD0,温度传感器,°C\n压力,REAL,DB1.DBD4,压力传感器,MPa")
        text_layout.addWidget(self.csv_text_edit)
        
        text_group.setLayout(text_layout)
        layout.addWidget(text_group)
        
        # Options
        options_layout = QHBoxLayout()
        
        self.has_header_checkbox = QCheckBox("CSV包含表头")
        self.has_header_checkbox.setChecked(True)
        options_layout.addWidget(self.has_header_checkbox)
        
        self.enable_thresholds_checkbox = QCheckBox("启用阈值")
        options_layout.addWidget(self.enable_thresholds_checkbox)
        
        options_layout.addStretch(1)
        
        self.preview_btn = QPushButton("预览")
        self.preview_btn.clicked.connect(self.preview_import)
        options_layout.addWidget(self.preview_btn)
        
        layout.addLayout(options_layout)
        
        # Preview section
        preview_group = QGroupBox("预览")
        preview_layout = QVBoxLayout()
        
        self.preview_label = QLabel("导入预览将显示在这里")
        preview_layout.addWidget(self.preview_label)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def browse_file(self):
        """Browse for a CSV file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择CSV文件", "", "CSV文件 (*.csv);;所有文件 (*)")
        if file_path:
            self.file_path_edit.setText(file_path)
            # Load file content into text edit
            try:
                # Try different encodings in order of likelihood
                encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312', 'iso-8859-1']
                content = None
                
                for encoding in encodings:
                    try:
                        with open(file_path, 'r', encoding=encoding) as f:
                            content = f.read()
                        break  # If successful, exit the loop
                    except UnicodeDecodeError:
                        continue  # Try next encoding
                
                if content is not None:
                    self.csv_text_edit.setPlainText(content)
                else:
                    raise ValueError("无法以任何已知编码读取文件")
                    
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法读取文件: {str(e)}")
                logger.error(f"读取CSV文件失败: {str(e)}")
    
    def preview_import(self):
        """Preview the variables to be imported."""
        try:
            # Get CSV content
            csv_content = self.csv_text_edit.toPlainText()
            if not csv_content.strip():
                self.preview_label.setText("没有数据可预览")
                return
            
            # Parse CSV
            self.variables = self.parse_csv(csv_content)
            
            if not self.variables:
                self.preview_label.setText("没有找到有效的变量数据")
                return
            
            # Generate preview text
            preview_text = f"找到 {len(self.variables)} 个变量：\n\n"
            for i, variable in enumerate(self.variables[:5]):  # Show first 5 variables
                preview_text += f"{i+1}. {variable.name} ({variable.data_type}) - 地址: {variable.address}\n"
            
            if len(self.variables) > 5:
                preview_text += f"...以及 {len(self.variables) - 5} 个更多变量"
            
            self.preview_label.setText(preview_text)
        except Exception as e:
            QMessageBox.critical(self, "预览错误", f"预览数据时出错: {str(e)}")
            self.preview_label.setText(f"预览失败: {str(e)}")
    
    def parse_csv(self, csv_content):
        """Parse CSV content and return a list of Variable objects."""
        variables = []
        
        # Parse CSV
        csv_file = io.StringIO(csv_content)
        has_header = self.has_header_checkbox.isChecked()
        
        try:
            # Use csv.reader with proper dialect detection
            dialect = csv.Sniffer().sniff(csv_content[:1024]) if len(csv_content) > 0 else csv.excel
            reader = csv.reader(csv_file, dialect)
            
            # Skip header if needed
            if has_header:
                try:
                    header = next(reader, None)
                    # Validate header
                    required_fields = ["name", "data_type", "address"]
                    
                    # Check if header contains required fields (case-insensitive)
                    if header and len(header) >= 3:
                        header_lower = [h.lower() for h in header]
                        missing_fields = [f for f in required_fields if f.lower() not in header_lower]
                        
                        if missing_fields:
                            raise ValueError(f"CSV头部缺少必要字段: {', '.join(missing_fields)}")
                    else:
                        raise ValueError(f"CSV头部缺少必要字段。需要: {', '.join(required_fields)}")
                except StopIteration:
                    raise ValueError("CSV文件为空或格式错误")
            
            # Process rows
            for row in reader:
                if not row or len(row) < 3:  # Need at least name, data_type, address
                    continue
                
                try:
                    # Create variable
                    variable = Variable(
                        name=row[0].strip(),
                        data_type=row[1].strip(),
                        address=row[2].strip(),
                        description=row[3].strip() if len(row) > 3 else ""
                    )
                    
                    # Set units if available
                    if len(row) > 4:
                        variable.units = row[4].strip()
                    
                    # Set threshold values if enabled and provided
                    if self.enable_thresholds_checkbox.isChecked() and len(row) > 5:
                        try:
                            warning_low = float(row[5]) if row[5].strip() else None
                            warning_high = float(row[6]) if len(row) > 6 and row[6].strip() else None
                            alarm_low = float(row[7]) if len(row) > 7 and row[7].strip() else None
                            alarm_high = float(row[8]) if len(row) > 8 and row[8].strip() else None
                            
                            variable.set_threshold(
                                enabled=True,
                                warning_low=warning_low,
                                warning_high=warning_high,
                                alarm_low=alarm_low,
                                alarm_high=alarm_high
                            )
                        except (ValueError, IndexError):
                            # If threshold values are invalid, just use default values
                            logger.warning(f"变量 {variable.name} 的阈值数据无效，使用默认值")
                    
                    variables.append(variable)
                except (ValueError, IndexError) as e:
                    logger.warning(f"跳过无效行: {row}. 错误: {str(e)}")
                    continue
                
        except Exception as e:
            raise ValueError(f"解析CSV时出错: {str(e)}")
        
        return variables
    
    def get_variables(self):
        """Get the parsed variables."""
        return self.variables

    def download_template(self):
        """Generate and download a template CSV file for variable import."""
        try:
            # Ask user where to save the template
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "保存变量导入模板",
                f"{self.device_type}变量导入模板.csv",
                "CSV文件 (*.csv);;所有文件 (*)"
            )
            
            if not file_path:
                return  # User cancelled
            
            # Ensure file has .csv extension
            if not file_path.lower().endswith('.csv'):
                file_path += '.csv'
            
            # Create template content based on device type
            template_content = [
                # Header row
                ["name", "data_type", "address", "description", "units", "warning_low", "warning_high", "alarm_low", "alarm_high"]
            ]
            
            # Add device type specific examples
            if self.device_type == "S7":
                template_content.extend([
                    ["温度", "REAL", "DB1.DBD0", "温度传感器", "°C", "10", "50", "5", "60"],
                    ["压力", "REAL", "DB1.DBD4", "压力传感器", "MPa", "0.2", "0.8", "0.1", "1.0"],
                    ["开关状态", "BOOL", "DB1.DBX8.0", "设备开关状态", "", "", "", "", ""],
                    ["计数器", "INT", "DB1.DBW10", "产品计数器", "个", "0", "1000", "", ""],
                    ["液位", "REAL", "DB1.DBD12", "储罐液位", "m", "1.0", "8.0", "0.5", "9.0"]
                ])
            elif self.device_type == "Modbus":
                template_content.extend([
                    ["温度", "REAL", "40001", "温度传感器", "°C", "10", "50", "5", "60"],
                    ["压力", "REAL", "40003", "压力传感器", "MPa", "0.2", "0.8", "0.1", "1.0"],
                    ["开关状态", "BOOL", "10001", "设备开关状态", "", "", "", "", ""],
                    ["计数器", "INT", "40005", "产品计数器", "个", "0", "1000", "", ""],
                    ["液位", "REAL", "40007", "储罐液位", "m", "1.0", "8.0", "0.5", "9.0"]
                ])
            elif self.device_type == "CAN":
                template_content.extend([
                    ["发动机温度", "REAL", "0x100.0.16", "发动机温度传感器", "°C", "60", "90", "50", "110"],
                    ["转速", "INT", "0x100.16.16", "发动机转速", "rpm", "800", "6000", "500", "7000"],
                    ["油门位置", "REAL", "0x101.0.8", "油门踏板位置", "%", "0", "100", "", ""],
                    ["车速", "REAL", "0x102.0.16", "车辆速度", "km/h", "0", "120", "", "150"],
                    ["燃油量", "REAL", "0x103.0.8", "燃油剩余量", "L", "10", "", "5", ""]
                ])
            elif self.device_type == "GOOSE":
                template_content.extend([
                    ["断路器状态", "BOOL", "DataSet1.0", "断路器开关状态", "", "", "", "", ""],
                    ["电流", "REAL", "DataSet1.1", "线路电流", "A", "0", "100", "", "120"],
                    ["电压", "REAL", "DataSet1.2", "线路电压", "V", "220", "240", "210", "250"],
                    ["功率", "REAL", "DataSet1.3", "有功功率", "kW", "0", "50", "", "60"],
                    ["频率", "REAL", "DataSet1.4", "系统频率", "Hz", "49.5", "50.5", "49.0", "51.0"]
                ])
            else:
                # Generic template for other device types
                template_content.extend([
                    ["变量1", "REAL", "地址1", "变量1描述", "单位1", "10", "100", "0", "120"],
                    ["变量2", "INT", "地址2", "变量2描述", "单位2", "0", "1000", "", ""],
                    ["变量3", "BOOL", "地址3", "变量3描述", "", "", "", "", ""],
                    ["变量4", "DINT", "地址4", "变量4描述", "单位4", "100", "10000", "50", "12000"],
                    ["变量5", "STRING", "地址5", "变量5描述", "", "", "", "", ""]
                ])
            
            # Write to CSV file with UTF-8-BOM encoding for better Excel compatibility
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerows(template_content)
            
            # Show success message with device-specific notes
            message = f"变量导入模板已保存到：\n{file_path}\n\n请按照模板格式填写您的变量信息。"
            
            # Add device-specific notes
            if self.device_type == "S7":
                message += "\n\n注意：S7地址格式示例：\n- DB1.DBX0.0 (位)\n- DB1.DBW2 (字)\n- DB1.DBD4 (双字)\n- M10.0 (内存位)"
            elif self.device_type == "Modbus":
                message += "\n\n注意：Modbus地址格式示例：\n- 40001-49999 (保持寄存器)\n- 30001-39999 (输入寄存器)\n- 10001-19999 (输入状态)\n- 00001-09999 (线圈)"
            elif self.device_type == "CAN":
                message += "\n\n注意：CAN地址格式示例：\n- ID.起始位.位长度 (如 0x100.0.16)"
            elif self.device_type == "GOOSE":
                message += "\n\n注意：GOOSE地址格式示例：\n- 数据集.成员索引 (如 DataSet1.0)"
            
            QMessageBox.information(
                self,
                "模板已保存",
                message
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "保存模板失败",
                f"保存模板时出错：{str(e)}"
            )

class DataForwardingWidget(QWidget):
    """Widget for configuring data forwarding settings."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        
        # Enable forwarding checkbox
        self.enable_forwarding = QCheckBox("启用数据转发")
        layout.addWidget(self.enable_forwarding)
        
        # Forwarding protocols group
        protocol_group = QGroupBox("转发协议")
        protocol_layout = QVBoxLayout()
        
        # Protocol selection
        protocol_form = QFormLayout()
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["HTTP/HTTPS", "MQTT", "WebSocket", "TCP/IP", "自定义"])
        protocol_form.addRow("协议类型:", self.protocol_combo)
        protocol_layout.addLayout(protocol_form)
        
        # Protocol specific settings
        self.protocol_settings = QStackedWidget()
        
        # HTTP settings
        http_widget = QWidget()
        http_layout = QFormLayout()
        self.http_url = QLineEdit()
        self.http_method = QComboBox()
        self.http_method.addItems(["POST", "PUT"])
        self.http_headers = QPlainTextEdit()
        self.http_headers.setPlaceholderText("每行一个header，格式：key: value")
        http_layout.addRow("URL:", self.http_url)
        http_layout.addRow("请求方法:", self.http_method)
        http_layout.addRow("Headers:", self.http_headers)
        http_widget.setLayout(http_layout)
        self.protocol_settings.addWidget(http_widget)
        
        # MQTT settings
        mqtt_widget = QWidget()
        mqtt_layout = QFormLayout()
        self.mqtt_broker = QLineEdit()
        self.mqtt_port = QSpinBox()
        self.mqtt_port.setRange(1, 65535)
        self.mqtt_port.setValue(1883)
        self.mqtt_topic = QLineEdit()
        self.mqtt_username = QLineEdit()
        self.mqtt_password = QLineEdit()
        self.mqtt_password.setEchoMode(QLineEdit.Password)
        mqtt_layout.addRow("Broker:", self.mqtt_broker)
        mqtt_layout.addRow("Port:", self.mqtt_port)
        mqtt_layout.addRow("Topic:", self.mqtt_topic)
        mqtt_layout.addRow("Username:", self.mqtt_username)
        mqtt_layout.addRow("Password:", self.mqtt_password)
        mqtt_widget.setLayout(mqtt_layout)
        self.protocol_settings.addWidget(mqtt_widget)
        
        # WebSocket settings
        ws_widget = QWidget()
        ws_layout = QFormLayout()
        self.ws_url = QLineEdit()
        self.ws_protocol = QComboBox()
        self.ws_protocol.addItems(["ws://", "wss://"])
        ws_layout.addRow("URL:", self.ws_url)
        ws_layout.addRow("Protocol:", self.ws_protocol)
        ws_widget.setLayout(ws_layout)
        self.protocol_settings.addWidget(ws_widget)
        
        # TCP/IP settings
        tcp_widget = QWidget()
        tcp_layout = QFormLayout()
        self.tcp_host = QLineEdit()
        self.tcp_port = QSpinBox()
        self.tcp_port.setRange(1, 65535)
        tcp_layout.addRow("Host:", self.tcp_host)
        tcp_layout.addRow("Port:", self.tcp_port)
        tcp_widget.setLayout(tcp_layout)
        self.protocol_settings.addWidget(tcp_widget)
        
        # Custom settings
        custom_widget = QWidget()
        custom_layout = QFormLayout()
        self.custom_config = QPlainTextEdit()
        self.custom_config.setPlaceholderText("自定义配置（JSON格式）")
        custom_layout.addRow("配置:", self.custom_config)
        custom_widget.setLayout(custom_layout)
        self.protocol_settings.addWidget(custom_widget)
        
        protocol_layout.addWidget(self.protocol_settings)
        protocol_group.setLayout(protocol_layout)
        layout.addWidget(protocol_group)
        
        # Data format group
        format_group = QGroupBox("数据格式")
        format_layout = QFormLayout()
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["JSON", "XML", "CSV", "自定义"])
        format_layout.addRow("数据格式:", self.format_combo)
        
        self.template_edit = QPlainTextEdit()
        self.template_edit.setPlaceholderText("数据模板，使用 ${variable} 作为变量占位符")
        format_layout.addRow("数据模板:", self.template_edit)
        
        format_group.setLayout(format_layout)
        layout.addWidget(format_group)
        
        # Forwarding rules group
        rules_group = QGroupBox("转发规则")
        rules_layout = QVBoxLayout()
        
        # Add rule button
        add_rule_btn = QPushButton("添加规则")
        add_rule_btn.clicked.connect(self.add_forwarding_rule)
        rules_layout.addWidget(add_rule_btn)
        
        # Rules list
        self.rules_list = QListWidget()
        rules_layout.addWidget(self.rules_list)
        
        rules_group.setLayout(rules_layout)
        layout.addWidget(rules_group)
        
        # Connect signals
        self.enable_forwarding.stateChanged.connect(self.toggle_forwarding)
        self.protocol_combo.currentIndexChanged.connect(self.protocol_settings.setCurrentIndex)
        
        self.setLayout(layout)
    
    def toggle_forwarding(self, state):
        """Enable or disable forwarding settings based on checkbox state."""
        enabled = bool(state)
        for widget in [self.protocol_combo, self.protocol_settings, 
                      self.format_combo, self.template_edit, self.rules_list]:
            widget.setEnabled(enabled)
    
    def add_forwarding_rule(self):
        """Add a new forwarding rule."""
        dialog = ForwardingRuleDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            rule = dialog.get_rule()
            item = QListWidgetItem(f"{rule['name']} - {rule['condition']}")
            item.setData(Qt.UserRole, rule)
            self.rules_list.addItem(item)
    
    def get_forwarding_config(self):
        """Get the current forwarding configuration."""
        config = {
            'enabled': self.enable_forwarding.isChecked(),
            'protocol': {
                'type': self.protocol_combo.currentText(),
                'settings': self.get_protocol_settings()
            },
            'format': {
                'type': self.format_combo.currentText(),
                'template': self.template_edit.toPlainText()
            },
            'rules': self.get_rules()
        }
        return config
    
    def get_protocol_settings(self):
        """Get the current protocol specific settings."""
        protocol = self.protocol_combo.currentText()
        settings = {}
        
        if protocol == "HTTP/HTTPS":
            settings = {
                'url': self.http_url.text(),
                'method': self.http_method.currentText(),
                'headers': self.parse_headers(self.http_headers.toPlainText())
            }
        elif protocol == "MQTT":
            settings = {
                'broker': self.mqtt_broker.text(),
                'port': self.mqtt_port.value(),
                'topic': self.mqtt_topic.text(),
                'username': self.mqtt_username.text(),
                'password': self.mqtt_password.text()
            }
        elif protocol == "WebSocket":
            settings = {
                'url': self.ws_url.text(),
                'protocol': self.ws_protocol.currentText()
            }
        elif protocol == "TCP/IP":
            settings = {
                'host': self.tcp_host.text(),
                'port': self.tcp_port.value()
            }
        elif protocol == "自定义":
            try:
                settings = json.loads(self.custom_config.toPlainText())
            except:
                settings = {}
        
        return settings
    
    def get_rules(self):
        """Get all forwarding rules."""
        rules = []
        for i in range(self.rules_list.count()):
            item = self.rules_list.item(i)
            rule = item.data(Qt.UserRole)
            rules.append(rule)
        return rules
    
    @staticmethod
    def parse_headers(headers_text):
        """Parse headers text into a dictionary."""
        headers = {}
        for line in headers_text.split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip()] = value.strip()
        return headers

class ForwardingRuleDialog(QDialog):
    """Dialog for adding or editing a forwarding rule."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("转发规则")
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QFormLayout()
        
        # Rule name
        self.name_edit = QLineEdit()
        layout.addRow("规则名称:", self.name_edit)
        
        # Condition
        self.condition_edit = QLineEdit()
        self.condition_edit.setPlaceholderText("例如: value > 100")
        layout.addRow("触发条件:", self.condition_edit)
        
        # Action
        self.action_combo = QComboBox()
        self.action_combo.addItems(["立即转发", "批量转发", "条件转发"])
        layout.addRow("动作:", self.action_combo)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
    def get_rule(self):
        """Get the rule configuration."""
        return {
            'name': self.name_edit.text(),
            'condition': self.condition_edit.text(),
            'action': self.action_combo.currentText()
        }

class VariableView(QWidget):
    """Widget for managing variables within a device."""
    
    variable_selected = pyqtSignal(object)  # Emitted when a variable is selected
    
    def __init__(self, project_manager, parent=None):
        super().__init__(parent)
        self.project_manager = project_manager
        self.current_device = None
        self.current_variable = None
        self.main_window = parent  # Store reference to parent window
        self.init_ui()
    
    def set_main_window(self, main_window):
        """Set the main window reference explicitly."""
        self.main_window = main_window
        logger.info("VariableView: Main window reference set explicitly")
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("变量管理")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Device info
        self.device_info = QLabel("当前设备: 未选择")
        layout.addWidget(self.device_info)
        
        # Create tab widget for variables and settings
        self.tab_widget = QTabWidget()
        
        # Variables tab
        variables_tab = QWidget()
        variables_layout = QVBoxLayout(variables_tab)
        
        # Variable buttons
        btn_layout = QHBoxLayout()
        
        self.add_variable_btn = QPushButton("添加变量")
        self.add_variable_btn.clicked.connect(self.show_add_variable_dialog)
        
        self.edit_variable_btn = QPushButton("编辑变量")
        self.edit_variable_btn.clicked.connect(self.edit_variable_wrapper)
        self.edit_variable_btn.setEnabled(False)
        
        self.delete_variable_btn = QPushButton("删除变量")
        self.delete_variable_btn.clicked.connect(self.delete_variable_wrapper)
        self.delete_variable_btn.setEnabled(False)
        
        self.batch_import_btn = QPushButton("批量导入")
        self.batch_import_btn.clicked.connect(self.show_batch_import_dialog)
        
        btn_layout.addWidget(self.add_variable_btn)
        btn_layout.addWidget(self.edit_variable_btn)
        btn_layout.addWidget(self.delete_variable_btn)
        btn_layout.addWidget(self.batch_import_btn)
        variables_layout.addLayout(btn_layout)
        
        # Variable table
        self.variable_model = VariableTableModel()
        self.variable_table = QTableView()
        self.variable_table.setModel(self.variable_model)
        self.variable_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.variable_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.variable_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.variable_table.selectionModel().selectionChanged.connect(self.on_variable_selection_changed)
        variables_layout.addWidget(self.variable_table)
        
        # Variable details
        details_group = QGroupBox("变量详情")
        details_layout = QFormLayout()
        
        self.variable_id_label = QLabel("未选择")
        details_layout.addRow("变量ID:", self.variable_id_label)
        
        self.variable_name_label = QLabel("未选择")
        details_layout.addRow("变量名:", self.variable_name_label)
        
        self.variable_type_label = QLabel("未选择")
        details_layout.addRow("数据类型:", self.variable_type_label)
        
        self.variable_address_label = QLabel("未选择")
        details_layout.addRow("地址:", self.variable_address_label)
        
        self.variable_value_label = QLabel("未知")
        details_layout.addRow("当前值:", self.variable_value_label)
        
        self.variable_status_label = QLabel("未知")
        details_layout.addRow("状态:", self.variable_status_label)
        
        self.variable_timestamp_label = QLabel("未知")
        details_layout.addRow("时间戳:", self.variable_timestamp_label)
        
        details_group.setLayout(details_layout)
        variables_layout.addWidget(details_group)
        
        # Add variables tab
        self.tab_widget.addTab(variables_tab, "变量列表")
        
        # Settings tab
        self.settings_widget = VariableSettingsWidget()
        self.settings_widget.settings_changed.connect(self.on_settings_changed)
        self.tab_widget.addTab(self.settings_widget, "采集设置")
        
        # Add data forwarding tab
        self.forwarding_widget = DataForwardingWidget()
        self.tab_widget.addTab(self.forwarding_widget, "数据转发")
        
        # Add tab widget to layout
        layout.addWidget(self.tab_widget)
        
        self.setLayout(layout)
    
    def update_device(self, device):
        """使用指定的设备更新视图。"""
        # 保存之前的设备引用
        previous_device = self.current_device
        
        # 更新当前设备
        self.current_device = device
        
        if device:
            # 更新设备信息
            self.device_info.setText(f"当前设备: {device.name}")
            
            # 更新变量表格
            self.variable_model.set_variables(device.variables)
            
            # 启用添加变量和批量导入按钮
            self.add_variable_btn.setEnabled(True)
            self.batch_import_btn.setEnabled(True)
            
            # 如果设备已更改，清除当前变量选择
            if previous_device != device:
                # 清除变量详情
                self.update_variable_details(None)
                
                # 禁用编辑和删除按钮
                self.edit_variable_btn.setEnabled(False)
                self.delete_variable_btn.setEnabled(False)
                
                # 清除当前变量引用
                self.current_variable = None
                
                # 如果设备有变量，选择第一个变量
                if device.variables:
                    # 选择第一个变量
                    self.select_variable(device.variables[0])
                    
                    # 记录日志
                    logger.info(f"设备已更改，自动选择第一个变量: {device.variables[0].name}")
        else:
            # 清除设备信息
            self.device_info.setText("当前设备: 未选择")
            
            # 清空变量表格
            self.variable_model.set_variables([])
            
            # 禁用所有按钮
            self.add_variable_btn.setEnabled(False)
            self.batch_import_btn.setEnabled(False)
            self.edit_variable_btn.setEnabled(False)
            self.delete_variable_btn.setEnabled(False)
            
            # 清除变量详情
            self.update_variable_details(None)
            
            # 清除当前变量引用
            self.current_variable = None
    
    def show_add_variable_dialog(self):
        """Show dialog for adding a new variable."""
        if not self.current_device:
            QMessageBox.warning(self, "警告", "请先选择一个设备")
            return False
        
        dialog = AddVariableDialog(self.current_device.device_type, self)
        if dialog.exec_() == QDialog.Accepted:
            variable = dialog.get_variable_data()
            
            # Add variable to current device
            success = self.current_device.add_variable(variable)
            
            if success:
                # Save the project
                self.project_manager.save_project(self.project_manager.current_project)
                
                # Update variable table
                self.variable_model.set_variables(self.current_device.variables)
                
                # Select the new variable
                self.select_variable(variable)
                
                # Refresh tree view with delay to ensure data is updated
                logger.info(f"变量 '{variable.name}' 已添加，准备刷新树形视图")
                QTimer.singleShot(200, lambda v=variable: self.refresh_hierarchy_tree(v))
                
                # Log the successful addition
                logger.info(f"Added variable '{variable.name}' to device '{self.current_device.name}'")
                
                # Return operation success
                return True
            else:
                QMessageBox.critical(self, "错误", "添加变量失败")
                return False
            
        # Return operation cancelled
        return False
    
    def edit_variable_wrapper(self):
        """Wrapper method for edit_variable_btn.clicked signal to prevent boolean value being passed to edit_variable method."""
        selected_indexes = self.variable_table.selectionModel().selectedRows()
        
        if selected_indexes:
            row = selected_indexes[0].row()
            variable = self.variable_model.get_variable(row)
            
            if variable:
                self.edit_variable(variable)
    
    def delete_variable_wrapper(self):
        """Wrapper method for delete_variable_btn.clicked signal to prevent boolean value being passed to delete_variable method."""
        selected_indexes = self.variable_table.selectionModel().selectedRows()
        
        if selected_indexes:
            row = selected_indexes[0].row()
            variable = self.variable_model.get_variable(row)
            
            if variable:
                self.delete_variable(variable)
    
    def edit_variable(self, variable):
        """Edit the selected variable or the provided variable.
        
        Args:
            variable (Variable): Variable to edit
        
        Returns:
            bool: True if successful, False otherwise
        """
        # 检查变量对象是否有效
        if variable is None:
            logger.warning("编辑变量失败：变量对象为空")
            return False
            
        if isinstance(variable, bool):
            # 处理传入布尔值的情况（可能是从信号连接传入的结果）
            logger.warning("编辑变量失败：传入了布尔值而非变量对象")
            return False
        
        # 确保当前设备已设置
        if not self.current_device:
            logger.warning("编辑变量失败：当前设备未设置")
            return False
        
        dialog = AddVariableDialog(self.current_device.device_type, self)
        dialog.setWindowTitle("编辑变量")
        
        # 设置对话框中的变量值
        dialog.name_edit.setText(variable.name)
        dialog.data_type_combo.setCurrentText(variable.data_type)
        dialog.address_edit.setText(variable.address)
        dialog.description_edit.setText(variable.description)
        dialog.units_edit.setText(variable.units if hasattr(variable, 'units') else "")
        
        # 设置阈值
        if hasattr(variable, 'threshold') and variable.threshold:
            dialog.threshold_enabled.setChecked(variable.threshold.enabled)
            if variable.threshold.warning_low is not None:
                dialog.warning_low.setValue(variable.threshold.warning_low)
            if variable.threshold.warning_high is not None:
                dialog.warning_high.setValue(variable.threshold.warning_high)
            if variable.threshold.alarm_low is not None:
                dialog.alarm_low.setValue(variable.threshold.alarm_low)
            if variable.threshold.alarm_high is not None:
                dialog.alarm_high.setValue(variable.threshold.alarm_high)
        
        # 显示对话框
        if dialog.exec_() == QDialog.Accepted:
            # 获取对话框中的变量数据
            updated_variable = dialog.get_variable_data()
            
            # 保留原始ID
            updated_variable.variable_id = variable.variable_id
            
            # 更新设备中的变量
            self.current_device.update_variable(updated_variable)
            
            # 保存项目
            self.project_manager.save_project(self.project_manager.current_project)
            
            # 更新表格
            self.variable_model.set_variables(self.current_device.variables)
            
            # 选择更新后的变量
            self.select_variable(updated_variable)
            
            # 刷新树形视图
            self.refresh_hierarchy_tree(updated_variable)
            
            logger.info(f"变量 '{updated_variable.name}' 已更新")
            return True
            
        return False
    
    def delete_variable(self, variable):
        """Delete the selected variable or the provided variable.
        
        Args:
            variable (Variable): Variable to delete
        
        Returns:
            bool: True if successful, False otherwise
        """
        # 检查变量对象是否有效
        if variable is None:
            logger.warning("删除变量失败：变量对象为空")
            return False
        
        if isinstance(variable, bool):
            # 处理传入布尔值的情况（可能是从信号连接传入的结果）
            logger.warning("删除变量失败：传入了布尔值而非变量对象")
            return False
        
        # 确保当前设备已设置
        if not self.current_device:
            logger.warning("删除变量失败：当前设备未设置")
            return False
        
        # 确认删除
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除变量 '{variable.name}' 吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 从设备中删除变量
            if self.current_device.remove_variable(variable):
                # 保存项目
                self.project_manager.save_project(self.project_manager.current_project)
                
                # 更新表格
                self.variable_model.set_variables(self.current_device.variables)
                
                # 清除变量详情
                self.update_variable_details(None)
                
                # 禁用编辑和删除按钮
                self.edit_variable_btn.setEnabled(False)
                self.delete_variable_btn.setEnabled(False)
                
                # 刷新树形视图
                self.refresh_hierarchy_tree()
                
                logger.info(f"变量 '{variable.name}' 已删除")
                return True
            else:
                logger.error(f"删除变量 '{variable.name}' 失败")
                return False
        
        return False
    
    def select_variable(self, variable):
        """在表格视图中选择一个变量。
        
        Args:
            variable (Variable): 要选择的变量
        
        Returns:
            bool: 如果变量被找到并选中则为True，否则为False
        """
        if not variable:
            logger.warning("select_variable: 变量参数为空")
            return False
            
        if not self.current_device:
            logger.warning("select_variable: 当前设备未设置")
            return False
            
        # 确保变量表格已经加载了当前设备的变量
        if len(self.variable_model.variables) != len(self.current_device.variables):
            logger.info("变量表格数据与当前设备不匹配，正在重新加载...")
            self.variable_model.set_variables(self.current_device.variables)
            
        # 查找变量在表格中的行
        found = False
        for row in range(self.variable_model.rowCount()):
            var = self.variable_model.get_variable(row)
            if var and var.variable_id == variable.variable_id:
                # 选中该行
                self.variable_table.selectRow(row)
                
                # 更新变量详情
                self.update_variable_details(var)
                
                # 存储当前变量
                self.current_variable = var
                
                # 启用编辑和删除按钮
                self.edit_variable_btn.setEnabled(True)
                self.delete_variable_btn.setEnabled(True)
                
                found = True
                break
        
        if not found:
            # 尝试通过名称匹配
            for row in range(self.variable_model.rowCount()):
                var = self.variable_model.get_variable(row)
                if var and var.name == variable.name:
                    # 选中该行
                    self.variable_table.selectRow(row)
                    
                    # 更新变量详情
                    self.update_variable_details(var)
                    
                    # 存储当前变量
                    self.current_variable = var
                    
                    # 启用编辑和删除按钮
                    self.edit_variable_btn.setEnabled(True)
                    self.delete_variable_btn.setEnabled(True)
                    
                    logger.info(f"通过名称匹配找到变量: {var.name}")
                    found = True
                    break
            
            if not found:
                logger.warning(f"无法在表格中找到变量: {variable.name}")
        
        return found
    
    def refresh_hierarchy_tree(self, variable=None):
        """刷新主窗口中的树形视图
        
        Args:
            variable (Variable, optional): 刷新后要选中的变量
        """
        # 优先使用明确设置的main_window引用
        if hasattr(self, 'main_window') and self.main_window is not None:
            if hasattr(self.main_window, 'hierarchy_tree'):
                logger.info("使用main_window.hierarchy_tree刷新树形视图")
                # 强制刷新树形视图
                self.main_window.hierarchy_tree.refresh_tree()
                
                # 如果有变量，选中它
                if variable and self.current_device and self.project_manager.current_project:
                    # 确保树形视图知道当前项目和设备上下文
                    self.main_window.hierarchy_tree.current_project = self.project_manager.current_project
                    self.main_window.hierarchy_tree.current_device = self.current_device
                    
                    # 使用延时确保树已完全刷新
                    QTimer.singleShot(100, lambda: self.main_window.hierarchy_tree.select_variable(
                        variable, 
                        self.current_device, 
                        self.project_manager.current_project
                    ))
            elif hasattr(self.main_window, 'refresh_tree_view'):
                logger.info("使用main_window.refresh_tree_view()刷新树形视图")
                if variable:
                    self.main_window.refresh_tree_view(variable)
                else:
                    self.main_window.refresh_tree_view()
            else:
                logger.warning("main_window没有hierarchy_tree或refresh_tree_view方法")
        else:
            # 回退到使用parent()
            parent = self.parent()
            if parent and hasattr(parent, "hierarchy_tree"):
                logger.info("使用parent.hierarchy_tree刷新树形视图")
                parent.hierarchy_tree.refresh_tree()
                if variable and self.current_device and self.project_manager.current_project:
                    QTimer.singleShot(100, lambda: parent.hierarchy_tree.select_variable(
                        variable, 
                        self.current_device, 
                        self.project_manager.current_project
                    ))
            elif parent and hasattr(parent, "refresh_tree_view"):
                logger.info("使用parent.refresh_tree_view()刷新树形视图")
                if variable:
                    parent.refresh_tree_view(variable)
                else:
                    parent.refresh_tree_view()
            else:
                logger.warning("无法找到树形视图引用，无法刷新树形视图")
    
    def on_variable_selection_changed(self):
        """Handle variable selection change."""
        selected_indexes = self.variable_table.selectionModel().selectedRows()
        
        if selected_indexes:
            row = selected_indexes[0].row()
            variable = self.variable_model.get_variable(row)
            
            if variable:
                # Update variable details
                self.update_variable_details(variable)
                
                # Store current variable
                self.current_variable = variable
                
                # Enable buttons
                self.edit_variable_btn.setEnabled(True)
                self.delete_variable_btn.setEnabled(True)
                return
        
        # No valid selection
        self.update_variable_details(None)
        self.current_variable = None
        self.edit_variable_btn.setEnabled(False)
        self.delete_variable_btn.setEnabled(False)
    
    def update_variable_details(self, variable):
        """Update the variable details display.
        
        Args:
            variable: Variable to display
        """
        if variable:
            self.variable_id_label.setText(variable.variable_id)
            self.variable_name_label.setText(variable.name)
            self.variable_type_label.setText(variable.data_type)
            self.variable_address_label.setText(variable.address)
            
            if variable.current_value is not None:
                value_str = str(variable.current_value)
                if hasattr(variable, 'units') and variable.units:
                    value_str += f" {variable.units}"
                self.variable_value_label.setText(value_str)
            else:
                self.variable_value_label.setText("未知")
            
            self.variable_status_label.setText(variable.status)
            
            if variable.last_updated:
                try:
                    # Handle both string ISO format and numeric timestamp
                    if isinstance(variable.last_updated, str):
                        timestamp = datetime.fromisoformat(variable.last_updated.replace('Z', '+00:00'))
                    else:
                        timestamp = datetime.fromtimestamp(variable.last_updated / 1000)
                    self.variable_timestamp_label.setText(timestamp.strftime("%Y-%m-%d %H:%M:%S"))
                except Exception as e:
                    logger.warning(f"Error formatting timestamp: {e}")
                    self.variable_timestamp_label.setText(str(variable.last_updated))
            else:
                self.variable_timestamp_label.setText("未知")
            
            # Update settings widget
            self.settings_widget.set_variable(variable)
        else:
            self.variable_id_label.setText("未选择")
            self.variable_name_label.setText("未选择")
            self.variable_type_label.setText("未选择")
            self.variable_address_label.setText("未选择")
            self.variable_value_label.setText("未知")
            self.variable_status_label.setText("未知")
            self.variable_timestamp_label.setText("未知")
            
            # Clear settings widget
            self.settings_widget.set_variable(None)
    
    def show_batch_import_dialog(self):
        """Show dialog for batch importing variables."""
        if not self.current_device:
            QMessageBox.warning(self, "警告", "请先选择一个设备")
            return False
        
        dialog = BatchImportVariableDialog(self.current_device.device_type, self)
        if dialog.exec_() == QDialog.Accepted:
            variables = dialog.get_variables()
            
            if not variables:
                QMessageBox.warning(self, "警告", "没有找到有效的变量数据")
                return False
            
            # Ask for confirmation
            reply = QMessageBox.question(
                self,
                "确认导入",
                f"确定要导入 {len(variables)} 个变量吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                # Import variables
                imported_count = 0
                skipped_count = 0
                
                for variable in variables:
                    # Check if variable with same name already exists
                    variable_exists = False
                    for existing_variable in self.current_device.variables:
                        if existing_variable.name == variable.name:
                            variable_exists = True
                            skipped_count += 1
                            break
                    
                    if not variable_exists:
                        # Add variable to device
                        self.current_device.add_variable(variable)
                        imported_count += 1
                
                # Save project
                self.project_manager.save_project(self.project_manager.current_project)
                
                # Update variable table
                self.variable_model.set_variables(self.current_device.variables)
                
                # Refresh tree view
                QTimer.singleShot(200, lambda: self.refresh_hierarchy_tree())
                
                # Show result
                QMessageBox.information(
                    self,
                    "导入结果",
                    f"成功导入 {imported_count} 个变量，跳过 {skipped_count} 个重复变量。"
                )
                
                return True
        
        return False 

    def on_settings_changed(self):
        """Handle settings changed event."""
        # Refresh the variable table to show updated settings
        if self.current_device:
            self.update_device(self.current_device)
        
        # If a variable is selected, update its details
        if self.current_variable:
            self.update_variable_details(self.current_variable) 