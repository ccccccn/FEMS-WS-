#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import csv
import io

import requests
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTableView, QHeaderView, QDialog,
    QFormLayout, QLineEdit, QTextEdit, QDialogButtonBox,
    QMessageBox, QGroupBox, QSplitter, QComboBox,
    QSpinBox, QTabWidget, QStackedWidget, QAbstractItemView,
    QFileDialog, QPlainTextEdit, QCheckBox
)
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QColor

from frontend.models.device_model import Device

logger = logging.getLogger(__name__)


class DeviceTableModel(QAbstractTableModel):
    """Table model for displaying devices."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.devices = []
        self.headers = ["设备ID", "设备名称", "类型", "IP地址", "端口", "变量数量", "状态"]

    def rowCount(self, parent=QModelIndex()):
        return len(self.devices)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self.devices)):
            return QVariant()

        device = self.devices[index.row()]
        column = index.column()

        if role == Qt.DisplayRole:
            if column == 0:
                return device.device_id[:8] + "..."  # Truncate long ID
            elif column == 1:
                return device.name
            elif column == 2:
                return device.device_type
            elif column == 3:
                return device.ip_address
            elif column == 4:
                return str(device.port)
            elif column == 5:
                return str(len(device.variables))
            elif column == 6:
                return "已连接" if device.is_connected else "未连接"

        elif role == Qt.BackgroundRole:
            # Alternate row colors for better readability
            if index.row() % 2 == 0:
                return QColor(240, 240, 240, 40)

        return QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return QVariant()

    def set_devices(self, devices):
        """Set the devices to display."""
        self.beginResetModel()
        self.devices = devices
        self.endResetModel()

    def get_device(self, row):
        """Get the device at the specified row."""
        if 0 <= row < len(self.devices):
            return self.devices[row]
        return None


class AddDeviceDialog(QDialog):
    """Dialog for adding a new device."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加设备")
        self.setMinimumWidth(500)
        self.init_ui()

    def init_ui(self):
        """Initialize the dialog UI."""
        layout = QVBoxLayout()

        # Create form layout for device properties
        form_layout = QFormLayout()

        # Device name
        self.name_edit = QLineEdit()
        form_layout.addRow("设备名称:", self.name_edit)

        # Device type (protocol)
        self.device_type_combo = QComboBox()
        self.device_type_combo.addItems(["S7-1200", "Modbus", "CAN", "GOOSE"])
        self.device_type_combo.currentTextChanged.connect(self.device_type_changed)
        form_layout.addRow("设备类型:", self.device_type_combo)

        # IP address
        self.ip_address_edit = QLineEdit()
        self.ip_address_edit.setText("127.0.0.1")
        form_layout.addRow("IP地址:", self.ip_address_edit)

        # Port
        self.port_spin = QSpinBox()
        self.port_spin.setRange(0, 65535)
        self.port_spin.setValue(102)  # Default S7 port
        form_layout.addRow("端口:", self.port_spin)

        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        form_layout.addRow("设备描述:", self.description_edit)

        # Protocol specific settings
        self.protocol_settings = QTabWidget()

        # S7 settings
        s7_widget = QWidget()
        s7_layout = QFormLayout(s7_widget)

        self.s7_rack_spin = QSpinBox()
        self.s7_rack_spin.setRange(0, 7)
        self.s7_rack_spin.setValue(0)
        s7_layout.addRow("机架号:", self.s7_rack_spin)

        self.s7_slot_spin = QSpinBox()
        self.s7_slot_spin.setRange(0, 31)
        self.s7_slot_spin.setValue(1)
        s7_layout.addRow("插槽号:", self.s7_slot_spin)

        # Modbus settings
        modbus_widget = QWidget()
        modbus_layout = QFormLayout(modbus_widget)

        self.modbus_type_combo = QComboBox()
        self.modbus_type_combo.addItems(["TCP", "RTU"])
        modbus_layout.addRow("Modbus类型:", self.modbus_type_combo)

        self.modbus_unit_id_spin = QSpinBox()
        self.modbus_unit_id_spin.setRange(0, 247)
        self.modbus_unit_id_spin.setValue(1)
        modbus_layout.addRow("Unit ID:", self.modbus_unit_id_spin)

        # CAN settings
        can_widget = QWidget()
        can_layout = QFormLayout(can_widget)

        self.can_interface_edit = QLineEdit()
        self.can_interface_edit.setText("can0")
        can_layout.addRow("接口:", self.can_interface_edit)

        self.can_bitrate_combo = QComboBox()
        self.can_bitrate_combo.addItems(["125000", "250000", "500000", "1000000"])
        self.can_bitrate_combo.setCurrentText("500000")
        can_layout.addRow("比特率:", self.can_bitrate_combo)

        # GOOSE settings
        goose_widget = QWidget()
        goose_layout = QFormLayout(goose_widget)

        self.goose_interface_edit = QLineEdit()
        self.goose_interface_edit.setText("eth0")
        goose_layout.addRow("接口:", self.goose_interface_edit)

        self.goose_appid_edit = QLineEdit()
        goose_layout.addRow("AppID:", self.goose_appid_edit)

        self.goose_mac_edit = QLineEdit()
        self.goose_mac_edit.setText("01:0C:CD:01:00:00")
        goose_layout.addRow("MAC地址:", self.goose_mac_edit)

        # Add tabs to tab widget
        self.protocol_settings.addTab(s7_widget, "S7设置")
        self.protocol_settings.addTab(modbus_widget, "Modbus设置")
        self.protocol_settings.addTab(can_widget, "CAN设置")
        self.protocol_settings.addTab(goose_widget, "GOOSE设置")

        # Initial selection
        self.device_type_changed(self.device_type_combo.currentText())

        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        # Add layouts to main layout
        layout.addLayout(form_layout)
        layout.addWidget(self.protocol_settings)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def device_type_changed(self, device_type):
        """Handle device type change."""
        # Update port based on device type
        if device_type == "S7":
            self.port_spin.setValue(102)
            self.protocol_settings.setCurrentIndex(0)
        elif device_type == "Modbus":
            self.port_spin.setValue(502)
            self.protocol_settings.setCurrentIndex(1)
        elif device_type == "CAN":
            self.port_spin.setValue(0)  # Not applicable for CAN
            self.protocol_settings.setCurrentIndex(2)
        elif device_type == "GOOSE":
            self.port_spin.setValue(0)  # Not applicable for GOOSE
            self.protocol_settings.setCurrentIndex(3)

    def get_device_data(self):
        """Get device data from the dialog."""
        device_type = self.device_type_combo.currentText()

        device = Device(
            name=self.name_edit.text(),
            device_type=device_type,
            ip_address=self.ip_address_edit.text(),
            port=self.port_spin.value(),
            description=self.description_edit.toPlainText()
        )

        # Set protocol-specific settings
        if device_type == "S7":
            device.set_s7_settings(
                rack=self.s7_rack_spin.value(),
                slot=self.s7_slot_spin.value()
            )
        elif device_type == "Modbus":
            device.set_modbus_settings(
                modbus_type=self.modbus_type_combo.currentText(),
                unit_id=self.modbus_unit_id_spin.value()
            )
        elif device_type == "CAN":
            device.set_can_settings(
                interface=self.can_interface_edit.text(),
                bitrate=int(self.can_bitrate_combo.currentText())
            )
        elif device_type == "GOOSE":
            device.set_goose_settings(
                interface=self.goose_interface_edit.text(),
                appid=self.goose_appid_edit.text(),
                mac=self.goose_mac_edit.text()
            )

        return device


class BatchImportDeviceDialog(QDialog):
    """Dialog for batch importing devices."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("批量导入设备")
        self.setMinimumSize(800, 600)
        self.devices = []
        self.init_ui()

    def init_ui(self):
        """Initialize the dialog UI."""
        layout = QVBoxLayout()

        # Instructions
        instructions = QLabel("您可以通过以下两种方式批量导入设备：")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # File import section
        file_group = QGroupBox("从CSV文件导入")
        file_layout = QVBoxLayout()

        file_help = QLabel("CSV文件应包含以下列：name,device_type,ip_address,port,description")
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

        text_help = QLabel("请输入CSV格式的文本，每行一个设备，列应为：name,device_type,ip_address,port,description")
        text_help.setWordWrap(True)
        text_layout.addWidget(text_help)

        self.csv_text_edit = QPlainTextEdit()
        self.csv_text_edit.setPlaceholderText(
            "例如：\nPLC1,S7,192.168.1.10,102,西区PLC控制器\nPLC2,Modbus,192.168.1.11,502,东区PLC控制器")
        text_layout.addWidget(self.csv_text_edit)

        text_group.setLayout(text_layout)
        layout.addWidget(text_group)

        # Options
        options_layout = QHBoxLayout()

        self.has_header_checkbox = QCheckBox("CSV包含表头")
        self.has_header_checkbox.setChecked(True)
        options_layout.addWidget(self.has_header_checkbox)

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
        """Preview the devices to be imported."""
        try:
            # Get CSV content
            csv_content = self.csv_text_edit.toPlainText()
            if not csv_content.strip():
                self.preview_label.setText("没有数据可预览")
                return

            # Parse CSV
            self.devices = self.parse_csv(csv_content)

            if not self.devices:
                self.preview_label.setText("没有找到有效的设备数据")
                return

            # Generate preview text
            preview_text = f"找到 {len(self.devices)} 个设备：\n\n"
            for i, device in enumerate(self.devices[:5]):  # Show first 5 devices
                preview_text += f"{i + 1}. {device['name']} ({device['device_type']}) - {device['ip_address']}:{device['port']}\n"

            if len(self.devices) > 5:
                preview_text += f"...以及 {len(self.devices) - 5} 个更多设备"

            self.preview_label.setText(preview_text)
        except Exception as e:
            QMessageBox.critical(self, "预览错误", f"预览数据时出错: {str(e)}")
            self.preview_label.setText(f"预览失败: {str(e)}")

    def parse_csv(self, csv_content):
        """Parse CSV content and return a list of device dictionaries."""
        devices = []

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
                    required_fields = ["name", "device_type", "ip_address", "port"]

                    # Check if header contains required fields (case-insensitive)
                    header_lower = [h.lower() for h in header] if header else []
                    missing_fields = [f for f in required_fields if f.lower() not in header_lower]

                    if missing_fields:
                        raise ValueError(f"CSV头部缺少必要字段: {', '.join(missing_fields)}")
                except StopIteration:
                    raise ValueError("CSV文件为空或格式错误")

            # Process rows
            for row in reader:
                if not row or len(row) < 4:  # Need at least name, type, IP, port
                    continue

                try:
                    # Validate and convert port to integer
                    port = int(row[3]) if row[3].strip().isdigit() else 0

                    device = {
                        "name": row[0].strip(),
                        "device_type": row[1].strip(),
                        "ip_address": row[2].strip(),
                        "port": port,
                        "description": row[4].strip() if len(row) > 4 else ""
                    }

                    # Add optional connection settings if available
                    if len(row) > 5:
                        if device["device_type"] == "S7":
                            device["rack"] = int(row[5]) if len(row) > 5 and row[5].strip().isdigit() else 0
                            device["slot"] = int(row[6]) if len(row) > 6 and row[6].strip().isdigit() else 1
                        elif device["device_type"] == "Modbus":
                            device["modbus_type"] = row[5].strip() if len(row) > 5 else "TCP"
                            device["unit_id"] = int(row[6]) if len(row) > 6 and row[6].strip().isdigit() else 1
                        elif device["device_type"] == "CAN":
                            device["interface"] = row[5].strip() if len(row) > 5 else "can0"
                            device["bitrate"] = int(row[6]) if len(row) > 6 and row[6].strip().isdigit() else 500000
                        elif device["device_type"] == "GOOSE":
                            device["interface"] = row[5].strip() if len(row) > 5 else "eth0"
                            device["appid"] = row[6].strip() if len(row) > 6 else ""
                            device["mac"] = row[7].strip() if len(row) > 7 else ""

                    devices.append(device)
                except (ValueError, IndexError) as e:
                    logger.warning(f"跳过无效行: {row}. 错误: {str(e)}")
                    continue

        except Exception as e:
            raise ValueError(f"解析CSV时出错: {str(e)}")

        return devices

    def get_devices(self):
        """Get the parsed devices."""
        return self.devices

    def download_template(self):
        """Generate and download a template CSV file for device import."""
        try:
            # Ask user where to save the template
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "保存设备导入模板",
                "设备导入模板.csv",
                "CSV文件 (*.csv);;所有文件 (*)"
            )

            if not file_path:
                return  # User cancelled

            # Ensure file has .csv extension
            if not file_path.lower().endswith('.csv'):
                file_path += '.csv'

            # Create template content
            template_content = [
                # Header row
                ["name", "device_type", "ip_address", "port", "description", "rack", "slot", "modbus_type", "unit_id",
                 "interface", "bitrate", "appid", "mac"],
                # Example S7 device
                ["PLC1", "S7", "192.168.1.10", "102", "西区S7 PLC控制器", "0", "1", "", "", "", "", "", ""],
                # Example Modbus device
                ["ModbusDevice1", "Modbus", "192.168.1.11", "502", "东区Modbus设备", "", "", "TCP", "1", "", "", "",
                 ""],
                # Example CAN device
                ["CANDevice1", "CAN", "192.168.1.12", "0", "CAN总线设备", "", "", "", "", "can0", "500000", "", ""],
                # Example GOOSE device
                ["GOOSEDevice1", "GOOSE", "192.168.1.13", "0", "GOOSE设备", "", "", "", "", "eth0", "", "1000",
                 "01:0C:CD:01:00:01"]
            ]

            # Write to CSV file with UTF-8-BOM encoding for better Excel compatibility
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerows(template_content)

            # Show success message
            QMessageBox.information(
                self,
                "模板已保存",
                f"设备导入模板已保存到：\n{file_path}\n\n请按照模板格式填写您的设备信息。"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "保存模板失败",
                f"保存模板时出错：{str(e)}"
            )


class DeviceView(QWidget):
    """Widget for managing devices within a project."""

    device_selected = pyqtSignal(object)  # Emitted when a device is selected

    def __init__(self, project_manager, parent=None):
        super().__init__(parent)
        self.project_manager = project_manager
        self.main_window = parent  # Store reference to parent window
        self.init_ui()

    def set_main_window(self, main_window):
        """Set the main window reference explicitly."""
        self.main_window = main_window
        logger.info("DeviceView: Main window reference set explicitly")

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()

        # Title
        title_layout = QHBoxLayout()

        self.title_label = QLabel("设备管理")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        self.title_label.setFont(title_font)

        self.project_label = QLabel("")

        title_layout.addWidget(self.title_label)
        title_layout.addStretch(1)
        title_layout.addWidget(self.project_label)

        # Device table
        self.device_table = QTableView()
        self.device_model = DeviceTableModel()
        self.device_table.setModel(self.device_model)
        self.device_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.device_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.device_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.device_table.selectionModel().selectionChanged.connect(self.on_device_selection_changed)
        self.device_table.setAlternatingRowColors(True)

        # Device buttons
        btn_layout = QHBoxLayout()

        self.add_device_btn = QPushButton("添加设备")
        self.add_device_btn.clicked.connect(self.show_add_device_dialog)

        self.batch_import_btn = QPushButton("批量导入")
        self.batch_import_btn.clicked.connect(self.show_batch_import_dialog)

        self.edit_device_btn = QPushButton("编辑设备")
        self.edit_device_btn.clicked.connect(self.edit_device)
        self.edit_device_btn.setEnabled(False)

        self.delete_device_btn = QPushButton("删除设备")
        self.delete_device_btn.clicked.connect(self.delete_device)
        self.delete_device_btn.setEnabled(False)

        btn_layout.addWidget(self.add_device_btn)
        btn_layout.addWidget(self.batch_import_btn)
        btn_layout.addWidget(self.edit_device_btn)
        btn_layout.addWidget(self.delete_device_btn)

        # Device details section
        self.device_details = QGroupBox("设备详情")
        details_layout = QVBoxLayout()

        # General details
        general_info = QFormLayout()
        self.device_id_label = QLabel("设备ID: ")
        self.device_name_label = QLabel("设备名称: ")
        self.device_type_label = QLabel("设备类型: ")
        self.ip_address_label = QLabel("IP地址: ")
        self.port_label = QLabel("端口: ")
        self.variable_count_label = QLabel("变量数量: 0")

        general_info.addRow("设备ID:", self.device_id_label)
        general_info.addRow("设备名称:", self.device_name_label)
        general_info.addRow("设备类型:", self.device_type_label)
        general_info.addRow("IP地址:", self.ip_address_label)
        general_info.addRow("端口:", self.port_label)
        general_info.addRow("变量数量:", self.variable_count_label)

        # Actions
        action_layout = QHBoxLayout()

        self.connect_device_btn = QPushButton("连接设备")
        self.connect_device_btn.clicked.connect(self.connect_device)
        self.connect_device_btn.setEnabled(False)

        self.add_variable_btn = QPushButton("添加变量")
        self.add_variable_btn.clicked.connect(self.add_variable)
        self.add_variable_btn.setEnabled(False)

        action_layout.addWidget(self.connect_device_btn)
        action_layout.addWidget(self.add_variable_btn)

        details_layout.addLayout(general_info)
        details_layout.addLayout(action_layout)
        self.device_details.setLayout(details_layout)

        # Create splitter for device list and details
        splitter = QSplitter(Qt.Vertical)

        # Create containers for the table and details
        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        table_layout.addWidget(self.device_table)
        table_layout.addLayout(btn_layout)

        # Add widgets to splitter
        splitter.addWidget(table_container)
        splitter.addWidget(self.device_details)

        # Set initial sizes
        splitter.setSizes([400, 200])

        # Add all widgets to main layout
        layout.addLayout(title_layout)
        layout.addWidget(splitter)

        self.setLayout(layout)

    def update_project(self, project):
        """Update the view with the specified project."""
        if project:
            self.project_label.setText(f"项目: {project.name}")
            self.device_model.set_devices(project.devices)
            self.add_device_btn.setEnabled(True)
        else:
            self.project_label.setText("")
            self.device_model.set_devices([])
            self.add_device_btn.setEnabled(False)
            self.edit_device_btn.setEnabled(False)
            self.delete_device_btn.setEnabled(False)
            self.connect_device_btn.setEnabled(False)
            self.add_variable_btn.setEnabled(False)
            self.update_device_details(None)

    def show_add_device_dialog(self):
        """Show dialog for adding a new device."""
        if not self.project_manager.current_project:
            QMessageBox.warning(self, "警告", "请先选择一个项目")
            return False

        dialog = AddDeviceDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            device = dialog.get_device_data()

            # Add device to current project
            self.project_manager.current_project.add_device(device)

            # Save project
            self.project_manager.save_project(self.project_manager.current_project)

            # Update device list
            self.update_project(self.project_manager.current_project)

            # Select the new device
            self.select_new_device(device)

            # 确保主窗口知道当前项目
            parent = self.parent()
            if parent:
                # 确保主窗口的当前项目是正确的
                if hasattr(parent, "project_manager"):
                    parent.project_manager.current_project = self.project_manager.current_project

                # 确保树形视图知道当前项目
                if hasattr(parent, "hierarchy_tree"):
                    parent.hierarchy_tree.current_project = self.project_manager.current_project

            # 刷新树形视图
            self.refresh_hierarchy_tree(device)

            # 记录日志
            logger.info(f"已添加设备: {device.name} 到项目: {self.project_manager.current_project.name}")

            # 返回操作成功
            return True

        # 返回操作取消
        return False

    def edit_device(self):
        """Edit the selected device."""
        selected_indexes = self.device_table.selectionModel().selectedRows()
        if not selected_indexes:
            return

        row = selected_indexes[0].row()
        device = self.device_model.get_device(row)
        if not device:
            return

        dialog = AddDeviceDialog(self)
        dialog.setWindowTitle("编辑设备")

        # Set dialog values
        dialog.name_edit.setText(device.name)
        dialog.device_type_combo.setCurrentText(device.device_type)
        dialog.ip_address_edit.setText(device.ip_address)
        dialog.port_spin.setValue(device.port)
        dialog.description_edit.setPlainText(device.description)

        # Set protocol-specific settings
        if device.device_type == "S7":
            dialog.s7_rack_spin.setValue(device.connection_settings.get("rack", 0))
            dialog.s7_slot_spin.setValue(device.connection_settings.get("slot", 1))
        elif device.device_type == "Modbus":
            dialog.modbus_type_combo.setCurrentText(device.connection_settings.get("modbus_type", "TCP"))
            dialog.modbus_unit_id_spin.setValue(device.connection_settings.get("unit_id", 1))
        elif device.device_type == "CAN":
            dialog.can_interface_edit.setText(device.connection_settings.get("interface", "can0"))
            dialog.can_bitrate_combo.setCurrentText(str(device.connection_settings.get("bitrate", 500000)))
        elif device.device_type == "GOOSE":
            dialog.goose_interface_edit.setText(device.connection_settings.get("interface", "eth0"))
            dialog.goose_appid_edit.setText(str(device.connection_settings.get("appid", "")))
            dialog.goose_mac_edit.setText(device.connection_settings.get("mac", ""))

        if dialog.exec_() == QDialog.Accepted:
            # Get updated device
            updated_device = dialog.get_device_data()

            # Preserve ID and variables
            updated_device.device_id = device.device_id
            updated_device.variables = device.variables

            # Update device in project
            for i, d in enumerate(self.project_manager.current_project.devices):
                if d.device_id == device.device_id:
                    self.project_manager.current_project.devices[i] = updated_device
                    break

            # Save project
            self.project_manager.save_project(self.project_manager.current_project)

            # Update the device list
            self.update_project(self.project_manager.current_project)

            # Select the updated device
            self.select_device(updated_device)

            # 刷新树形视图
            self.refresh_hierarchy_tree(updated_device)

    def delete_device(self):
        """Delete the selected device."""
        selected_indexes = self.device_table.selectionModel().selectedRows()
        if not selected_indexes:
            return False

        row = selected_indexes[0].row()
        device = self.device_model.get_device(row)
        if not device:
            return False

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除设备 '{device.name}' 吗？此操作无法撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Delete device from project
            self.project_manager.current_project.remove_device(device.device_id)

            # Save project
            self.project_manager.save_project(self.project_manager.current_project)

            # Update device list
            self.update_project(self.project_manager.current_project)

            # Clear device details
            self.update_device_details(None)

            # Disable buttons
            self.edit_device_btn.setEnabled(False)
            self.delete_device_btn.setEnabled(False)
            self.connect_device_btn.setEnabled(False)
            self.add_variable_btn.setEnabled(False)

            # 刷新树形视图
            self.refresh_hierarchy_tree()

            return True

        return False

    def select_new_device(self, device):
        """Select a newly added device in the table."""
        for row in range(self.device_model.rowCount()):
            if self.device_model.devices[row].device_id == device.device_id:
                self.device_table.selectRow(row)
                break

    def refresh_hierarchy_tree(self, device=None):
        """刷新主窗口中的树形视图"""
        parent = self.parent()
        if parent and hasattr(parent, "hierarchy_tree"):
            # 强制刷新树形视图
            parent.hierarchy_tree.refresh_tree()

            # 如果有设备且有当前项目，则选中该设备
            if device and self.project_manager.current_project:
                # 先设置当前项目，确保树形视图能正确识别项目上下文
                parent.hierarchy_tree.current_project = self.project_manager.current_project
                parent.hierarchy_tree.select_device(device, self.project_manager.current_project)
            # 如果没有设备但有当前项目，则选中当前项目
            elif self.project_manager.current_project:
                parent.hierarchy_tree.current_project = self.project_manager.current_project
                parent.hierarchy_tree.select_project(self.project_manager.current_project)

    def on_device_selection_changed(self):
        """Handle device selection change."""
        selected_indexes = self.device_table.selectionModel().selectedRows()

        if selected_indexes:
            row = selected_indexes[0].row()
            device = self.device_model.get_device(row)

            if device:
                # Update device details
                self.update_device_details(device)

                # Enable buttons
                self.edit_device_btn.setEnabled(True)
                self.delete_device_btn.setEnabled(True)
                self.connect_device_btn.setEnabled(True)
                self.add_variable_btn.setEnabled(True)

                # Emit signal
                self.device_selected.emit(device)
                return

        # No valid selection
        self.update_device_details(None)
        self.edit_device_btn.setEnabled(False)
        self.delete_device_btn.setEnabled(False)
        self.connect_device_btn.setEnabled(False)
        self.add_variable_btn.setEnabled(False)
        self.device_selected.emit(None)

    def update_device_details(self, device):
        """Update the device details display."""
        if device:
            self.device_id_label.setText(device.device_id)
            self.device_name_label.setText(device.name)
            self.device_type_label.setText(device.device_type)
            self.ip_address_label.setText(device.ip_address)
            self.port_label.setText(str(device.port))
            self.variable_count_label.setText(str(len(device.variables)))

            # Update connect button text based on connection status
            if device.is_connected:
                self.connect_device_btn.setText("断开连接")
            else:
                self.connect_device_btn.setText("连接设备")
        else:
            self.device_id_label.setText("")
            self.device_name_label.setText("")
            self.device_type_label.setText("")
            self.ip_address_label.setText("")
            self.port_label.setText("")
            self.variable_count_label.setText("0")
            self.connect_device_btn.setText("连接设备")

    def connect_device(self):
        """Connect to or disconnect from the selected device."""
        selected_indexes = self.device_table.selectionModel().selectedRows()
        if not selected_indexes:
            return

        row = selected_indexes[0].row()
        device = self.device_model.get_device(row)

        if not device:
            return

        url = "http://192.168.97.125:10002/DeviceConnect/"
        payload = {
            "device_type": device.device_type,
            "ip": device.ip_address,
            "port": device.port
        }
        headers = {
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(url=url, json=payload, timeout=5)
            data = response.json()
            if data.get("status") == "success":
                device.is_connected = not device.is_connected
            else:
                import json
                print(f'ip{payload.get("ip")}连接失败,原因：{json.loads(response.text).get("message")}')
                QMessageBox.information(self,'提示',f'ip{payload.get("ip")}连接失败,原因：{json.loads(response.text).get("message")}')
                return
        except Exception as e:
            logger.error(msg=f'{payload.get("ip")}连接失败：{e}')
        # Toggle connection statu


        # Update UI
        self.update_device_details(device)

        # Save project
        self.project_manager.save_project(self.project_manager.current_project)

        # Refresh device table
        self.device_model.dataChanged.emit(
            self.device_model.index(row, 0),
            self.device_model.index(row, self.device_model.columnCount() - 1)
        )

    def add_variable(self):
        """Add variable to the selected device."""
        selected_indexes = self.device_table.selectionModel().selectedRows()
        if not selected_indexes:
            QMessageBox.warning(self, "警告", "请先选择一个设备")
            return

        # Get selected device
        row = selected_indexes[0].row()
        device = self.device_model.get_device(row)

        if not device:
            QMessageBox.warning(self, "警告", "无效的设备")
            return

        # Try different ways to access the main window
        main_window = None

        # First try the stored main_window attribute
        if hasattr(self, 'main_window') and self.main_window is not None:
            main_window = self.main_window
            logger.info("使用stored main_window属性")

        # If not available, try to get from parent()
        if main_window is None:
            parent = self.parent()
            if parent:
                main_window = parent
                logger.info("使用parent()获取main_window")

        # Check if we have a valid main window with the required method
        if main_window and hasattr(main_window, "add_variable_to_device"):
            try:
                # Log the main window object to help with debugging
                logger.info(f"Main window object: {main_window}")
                logger.info(
                    f"Main window has add_variable_to_device method: {hasattr(main_window, 'add_variable_to_device')}")

                # 尝试调用主窗口的方法
                success = main_window.add_variable_to_device(device)

                # Update variable count in device details if successful
                if success and device:
                    self.variable_count_label.setText(str(len(device.variables)))

                    # Update device table to reflect the new variable count
                    self.device_model.dataChanged.emit(
                        self.device_model.index(row, 0),
                        self.device_model.index(row, self.device_model.columnCount() - 1)
                    )

                    # 刷新树形视图以显示新变量
                    self.refresh_hierarchy_tree(device)

                    # 记录日志
                    logger.info(f"已添加变量到设备: {device.name}")
            except Exception as e:
                # 记录错误
                logger.error(f"添加变量时发生错误: {str(e)}")
                QMessageBox.critical(self, "错误", f"添加变量时发生错误: {str(e)}")
        else:
            # 如果无法获取主窗口或主窗口没有提供添加变量方法，则直接跳转到变量视图
            logger.warning("无法获取主窗口或主窗口未提供add_variable_to_device方法，尝试直接跳转")

            # 尝试直接切换到变量视图
            if main_window and hasattr(main_window, "stacked_widget") and hasattr(main_window, "variable_view"):
                try:
                    # 切换到变量视图
                    main_window.stacked_widget.setCurrentIndex(2)
                    # 更新变量视图的当前设备
                    main_window.variable_view.update_device(device)
                    # 显示添加变量对话框
                    main_window.variable_view.show_add_variable_dialog()
                except Exception as e:
                    logger.error(f"直接跳转到变量视图失败: {str(e)}")
                    QMessageBox.critical(self, "错误", f"跳转到变量视图失败: {str(e)}")
            else:
                QMessageBox.warning(self, "警告", "无法添加变量，请使用菜单栏中的'变量'→'添加变量'功能")

    def select_device(self, device):
        """Select a device in the table view."""
        if not device:
            return

        # Find the row index for the device
        for row in range(self.device_model.rowCount()):
            if self.device_model.devices[row].device_id == device.device_id:
                # Select the row
                index = self.device_model.index(row, 0)
                self.device_table.selectRow(row)

                # Update device details
                self.update_device_details(device)

                # Emit device selected signal
                self.device_selected.emit(device)
                break

    def show_batch_import_dialog(self):
        """Show dialog for batch importing devices."""
        if not self.project_manager.current_project:
            QMessageBox.warning(self, "警告", "请先选择一个项目")
            return False

        dialog = BatchImportDeviceDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            devices_data = dialog.get_devices()

            if not devices_data:
                QMessageBox.warning(self, "警告", "没有找到有效的设备数据")
                return False

            # Ask for confirmation
            reply = QMessageBox.question(
                self,
                "确认导入",
                f"确定要导入 {len(devices_data)} 个设备吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )

            if reply == QMessageBox.Yes:
                # Import devices
                imported_count = 0
                skipped_count = 0

                for device_data in devices_data:
                    # Create device
                    from frontend.models.device_model import Device

                    device = Device(
                        name=device_data["name"],
                        device_type=device_data["device_type"],
                        ip_address=device_data["ip_address"],
                        port=device_data["port"],
                        description=device_data.get("description", "")
                    )

                    # Set protocol-specific settings
                    if device.device_type == "S7" and "rack" in device_data and "slot" in device_data:
                        device.set_s7_settings(
                            rack=device_data["rack"],
                            slot=device_data["slot"]
                        )
                    elif device.device_type == "Modbus" and "modbus_type" in device_data and "unit_id" in device_data:
                        device.set_modbus_settings(
                            modbus_type=device_data["modbus_type"],
                            unit_id=device_data["unit_id"]
                        )
                    elif device.device_type == "CAN" and "interface" in device_data and "bitrate" in device_data:
                        device.set_can_settings(
                            interface=device_data["interface"],
                            bitrate=device_data["bitrate"]
                        )
                    elif device.device_type == "GOOSE" and "interface" in device_data:
                        device.set_goose_settings(
                            interface=device_data["interface"],
                            appid=device_data.get("appid", ""),
                            mac=device_data.get("mac", "")
                        )

                    # Check if device with same name already exists
                    device_exists = False
                    for existing_device in self.project_manager.current_project.devices:
                        if existing_device.name == device.name:
                            device_exists = True
                            skipped_count += 1
                            break

                    if not device_exists:
                        # Add device to project
                        self.project_manager.current_project.add_device(device)
                        imported_count += 1

                # Save project
                self.project_manager.save_project(self.project_manager.current_project)

                # Update device list
                self.update_project(self.project_manager.current_project)

                # Refresh tree view
                self.refresh_hierarchy_tree()

                # Show result
                QMessageBox.information(
                    self,
                    "导入结果",
                    f"成功导入 {imported_count} 个设备，跳过 {skipped_count} 个重复设备。"
                )

                return True

        return False
