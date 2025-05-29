from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                           QLineEdit, QTreeWidget, QTreeWidgetItem, QPushButton,
                           QWidget, QSpacerItem, QSizePolicy, QGroupBox, QComboBox,
                           QMessageBox, QSplitter, QTableWidget, QTableWidgetItem,
                           QHeaderView, QCheckBox, QAbstractItemView, QFrame, QGridLayout)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QColor, QFont

from frontend.models.forwarding_model import (
    ForwardingManager, ForwardingConfig, ForwardingProtocol, ForwardingVariable
)


class ForwardingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("数据转发配置")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Name field
        name_layout = QHBoxLayout()
        name_label = QLabel("名称:")
        self.name_edit = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        # Description field
        desc_layout = QHBoxLayout()
        desc_label = QLabel("描述:")
        self.desc_edit = QLineEdit()
        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(self.desc_edit)
        layout.addLayout(desc_layout)

        # Buttons
        button_layout = QHBoxLayout()
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        button_layout.addItem(spacer)
        
        self.ok_button = QPushButton("确定")
        self.ok_button.setFixedSize(90, 30)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setFixedSize(90, 30)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Connect signals
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)


class ProtocolDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("转发协议配置")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Protocol Type
        type_layout = QHBoxLayout()
        type_label = QLabel("协议类型:")
        self.type_combo = QComboBox()
        self.type_combo.addItems(["MQTT", "HTTP/REST", "WebSocket", "TCP/IP", "UDP", "OPC UA", "Kafka"])
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)

        # Protocol Settings
        settings_group = QGroupBox("协议设置")
        settings_layout = QVBoxLayout()

        # Host
        host_layout = QHBoxLayout()
        host_label = QLabel("主机地址:")
        self.host_edit = QLineEdit()
        host_layout.addWidget(host_label)
        host_layout.addWidget(self.host_edit)
        settings_layout.addLayout(host_layout)

        # Port
        port_layout = QHBoxLayout()
        port_label = QLabel("端口:")
        self.port_edit = QLineEdit()
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.port_edit)
        settings_layout.addLayout(port_layout)

        # Topic/Path (for MQTT/HTTP)
        topic_layout = QHBoxLayout()
        self.topic_label = QLabel("主题/路径:")
        self.topic_edit = QLineEdit()
        topic_layout.addWidget(self.topic_label)
        topic_layout.addWidget(self.topic_edit)
        settings_layout.addLayout(topic_layout)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # Name field
        name_layout = QHBoxLayout()
        name_label = QLabel("名称:")
        self.name_edit = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        # Description field
        desc_layout = QHBoxLayout()
        desc_label = QLabel("描述:")
        self.desc_edit = QLineEdit()
        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(self.desc_edit)
        layout.addLayout(desc_layout)

        # Buttons
        button_layout = QHBoxLayout()
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        button_layout.addItem(spacer)
        
        self.ok_button = QPushButton("确定")
        self.ok_button.setFixedSize(90, 30)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setFixedSize(90, 30)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Connect signals
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        self.type_combo.currentTextChanged.connect(self.on_protocol_type_changed)

    def on_protocol_type_changed(self, protocol_type):
        """根据协议类型更新UI显示"""
        if protocol_type == "MQTT":
            self.topic_label.setText("主题:")
            self.topic_label.setVisible(True)
            self.topic_edit.setVisible(True)
        elif protocol_type == "HTTP/REST":
            self.topic_label.setText("路径:")
            self.topic_label.setVisible(True)
            self.topic_edit.setVisible(True)
        elif protocol_type in ["WebSocket", "TCP/IP", "UDP"]:
            self.topic_label.setVisible(False)
            self.topic_edit.setVisible(False)
        elif protocol_type == "OPC UA":
            self.topic_label.setText("节点ID:")
            self.topic_label.setVisible(True)
            self.topic_edit.setVisible(True)
        elif protocol_type == "Kafka":
            self.topic_label.setText("主题:")
            self.topic_label.setVisible(True)
            self.topic_edit.setVisible(True)


class VariableDialog(QDialog):
    def __init__(self, project_manager, parent=None):
        super().__init__(parent)
        self.project_manager = project_manager
        self.setWindowTitle("变量配置")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        self.setup_ui()
        self.setup_connections()
        self.load_variables()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Search and Filter
        filter_layout = QHBoxLayout()
        
        # Device filter
        device_layout = QHBoxLayout()
        device_label = QLabel("设备:")
        self.device_combo = QComboBox()
        device_layout.addWidget(device_label)
        device_layout.addWidget(self.device_combo)
        filter_layout.addLayout(device_layout)
        
        # Search box
        search_layout = QHBoxLayout()
        search_label = QLabel("搜索:")
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入变量名称或描述进行搜索...")
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        filter_layout.addLayout(search_layout)
        
        layout.addLayout(filter_layout)

        # Variables Table
        self.table_widget = QTableWidget()
        self.table_widget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(["选择", "设备", "变量名", "数据类型", "描述"])
        
        # Set column widths
        self.table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table_widget.setColumnWidth(0, 50)
        self.table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table_widget.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table_widget.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table_widget.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        
        layout.addWidget(self.table_widget)

        # Description field
        desc_layout = QHBoxLayout()
        desc_label = QLabel("转发描述:")
        self.desc_edit = QLineEdit()
        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(self.desc_edit)
        layout.addLayout(desc_layout)

        # Buttons
        button_layout = QHBoxLayout()
        
        # Select All / Deselect All
        select_layout = QHBoxLayout()
        self.select_all_btn = QPushButton("全选")
        self.deselect_all_btn = QPushButton("取消全选")
        select_layout.addWidget(self.select_all_btn)
        select_layout.addWidget(self.deselect_all_btn)
        button_layout.addLayout(select_layout)
        
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        button_layout.addItem(spacer)
        
        self.ok_button = QPushButton("确定")
        self.ok_button.setFixedSize(90, 30)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setFixedSize(90, 30)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def setup_connections(self):
        # Connect signals
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        self.select_all_btn.clicked.connect(self.select_all_variables)
        self.deselect_all_btn.clicked.connect(self.deselect_all_variables)
        
        # Setup delayed search
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.filter_variables)
        self.search_edit.textChanged.connect(self.on_search_text_changed)
        
        # Device filter
        self.device_combo.currentTextChanged.connect(self.filter_variables)

    def on_search_text_changed(self):
        """Delayed search to avoid too frequent updates"""
        self.search_timer.start(300)  # 300ms delay

    def load_variables(self):
        """加载当前项目中的所有变量"""
        self.table_widget.setRowCount(0)
        self.device_combo.clear()
        self.device_combo.addItem("全部")
        
        if not self.project_manager.current_project:
            return
            
        devices = set()
        row = 0
        
        for device in self.project_manager.current_project.devices:
            devices.add(device.name)
            for variable in device.variables:
                self.table_widget.insertRow(row)
                
                # Checkbox
                checkbox = QTableWidgetItem()
                checkbox.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                checkbox.setCheckState(Qt.Unchecked)
                self.table_widget.setItem(row, 0, checkbox)
                
                # Device name
                self.table_widget.setItem(row, 1, QTableWidgetItem(device.name))
                
                # Variable name
                self.table_widget.setItem(row, 2, QTableWidgetItem(variable.name))
                
                # Data type
                self.table_widget.setItem(row, 3, QTableWidgetItem(variable.data_type))
                
                # Description
                self.table_widget.setItem(row, 4, QTableWidgetItem(variable.description))
                
                row += 1
        
        # Add devices to combo box
        self.device_combo.addItems(sorted(devices))

    def filter_variables(self):
        """根据搜索文本和设备过滤变量"""
        search_text = self.search_edit.text().lower()
        selected_device = self.device_combo.currentText()
        
        for row in range(self.table_widget.rowCount()):
            device = self.table_widget.item(row, 1).text()
            variable = self.table_widget.item(row, 2).text().lower()
            description = self.table_widget.item(row, 4).text().lower()
            
            # Check if row matches filter criteria
            device_match = selected_device == "全部" or device == selected_device
            search_match = (not search_text or 
                          search_text in variable or 
                          search_text in description)
            
            self.table_widget.setRowHidden(row, not (device_match and search_match))

    def select_all_variables(self):
        """选择所有可见的变量"""
        for row in range(self.table_widget.rowCount()):
            if not self.table_widget.isRowHidden(row):
                self.table_widget.item(row, 0).setCheckState(Qt.Checked)

    def deselect_all_variables(self):
        """取消选择所有变量"""
        for row in range(self.table_widget.rowCount()):
            self.table_widget.item(row, 0).setCheckState(Qt.Unchecked)

    def get_selected_variables(self):
        """获取所有选中的变量"""
        selected_variables = []
        for row in range(self.table_widget.rowCount()):
            if self.table_widget.item(row, 0).checkState() == Qt.Checked:
                selected_variables.append({
                    'device': self.table_widget.item(row, 1).text(),
                    'name': self.table_widget.item(row, 2).text(),
                    'data_type': self.table_widget.item(row, 3).text(),
                    'description': self.table_widget.item(row, 4).text()
                })
        return selected_variables


class DataForwardingView(QWidget):
    def __init__(self, project_manager, parent=None):
        super().__init__(parent)
        self.project_manager = project_manager
        self.forwarding_manager = ForwardingManager()
        self.monitoring_timer = QTimer()
        self.monitoring_timer.timeout.connect(self.update_monitoring_data)
        self.monitoring_timer.setInterval(1000)  # 1秒更新一次
        self.setup_ui()
        self.setup_connections()
        self.apply_tech_theme()
        self.load_saved_configs()

    def apply_tech_theme(self):
        """Apply modern tech theme styling to the view"""
        # 设置科技感字体
        tech_font = QFont("Segoe UI", 9)
        self.setFont(tech_font)
        
        # 应用现代科技感样式
        self.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QTreeWidget {
                background-color: #333333;
                border: 1px solid #555555;
                border-radius: 3px;
            }
            QTreeWidget::item {
                height: 25px;
                color: #ffffff;
            }
            QTreeWidget::item:selected {
                background-color: #2a82da;
            }
            QPushButton {
                background-color: #2a5a8a;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 6px 12px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #3a6a9a;
            }
            QPushButton:pressed {
                background-color: #1a4a7a;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
            QLineEdit, QComboBox {
                background-color: #333333;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 4px;
                min-height: 25px;
            }
            QComboBox::drop-down {
                border: none;
                background-color: #2a5a8a;
                width: 25px;
            }
            QComboBox::down-arrow {
                image: url(resources/icons/down_arrow.png);
            }
            QGroupBox {
                border: 1px solid #555555;
                border-radius: 3px;
                margin-top: 10px;
                font-weight: bold;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel {
                color: #ffffff;
            }
            QSplitter::handle {
                background-color: #444444;
            }
            QSplitter::handle:horizontal {
                width: 2px;
            }
            QSplitter::handle:vertical {
                height: 2px;
            }
        """)

    def setup_ui(self):
        """Setup the user interface with modern layout and components"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 顶部工具栏
        toolbar = QHBoxLayout()
        
        # 左侧按钮组
        left_buttons = QHBoxLayout()
        self.add_btn = QPushButton("添加转发")
        self.add_btn.setIcon(QIcon("resources/icons/add.png"))
        self.edit_btn = QPushButton("编辑")
        self.edit_btn.setIcon(QIcon("resources/icons/edit.png"))
        self.delete_btn = QPushButton("删除")
        self.delete_btn.setIcon(QIcon("resources/icons/delete.png"))
        
        left_buttons.addWidget(self.add_btn)
        left_buttons.addWidget(self.edit_btn)
        left_buttons.addWidget(self.delete_btn)

        # 中间筛选控件组
        filter_layout = QHBoxLayout()
        
        # 转发项筛选
        self.forwarding_filter = QLineEdit()
        self.forwarding_filter.setPlaceholderText("筛选转发项...")
        self.forwarding_filter.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(QLabel("转发项:"))
        filter_layout.addWidget(self.forwarding_filter)
        
        # 协议筛选
        self.protocol_filter = QComboBox()
        self.protocol_filter.addItems(["全部", "MQTT", "HTTP/REST", "WebSocket", "TCP/IP", "OPC UA", "Kafka"])
        self.protocol_filter.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(QLabel("协议:"))
        filter_layout.addWidget(self.protocol_filter)
        
        # 变量筛选
        self.variable_filter = QLineEdit()
        self.variable_filter.setPlaceholderText("筛选变量...")
        self.variable_filter.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(QLabel("变量:"))
        filter_layout.addWidget(self.variable_filter)
        
        # 右侧按钮组
        right_buttons = QHBoxLayout()
        self.start_btn = QPushButton("启动")
        self.start_btn.setIcon(QIcon("resources/icons/start.png"))
        self.stop_btn = QPushButton("停止")
        self.stop_btn.setIcon(QIcon("resources/icons/stop.png"))
        
        right_buttons.addWidget(self.start_btn)
        right_buttons.addWidget(self.stop_btn)
        
        # 添加所有布局到工具栏
        toolbar.addLayout(left_buttons)
        toolbar.addSpacing(20)
        toolbar.addLayout(filter_layout)
        toolbar.addSpacing(20)
        toolbar.addLayout(right_buttons)
        
        main_layout.addLayout(toolbar)

        # 主分割器
        self.main_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧转发配置树
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["转发配置"])
        self.tree_widget.setColumnCount(1)
        self.tree_widget.setMinimumWidth(250)
        self.tree_widget.setAlternatingRowColors(True)
        
        # 右侧信息面板
        self.info_panel = QWidget()
        info_layout = QVBoxLayout(self.info_panel)
        
        # 基本信息组
        basic_group = QGroupBox("基本信息")
        basic_layout = QGridLayout()
        self.name_label = QLabel("名称：")
        self.name_value = QLabel()
        self.desc_label = QLabel("描述：")
        self.desc_value = QLabel()
        self.status_label = QLabel("状态：")
        self.status_value = QLabel()
        
        basic_layout.addWidget(self.name_label, 0, 0)
        basic_layout.addWidget(self.name_value, 0, 1)
        basic_layout.addWidget(self.desc_label, 1, 0)
        basic_layout.addWidget(self.desc_value, 1, 1)
        basic_layout.addWidget(self.status_label, 2, 0)
        basic_layout.addWidget(self.status_value, 2, 1)
        basic_group.setLayout(basic_layout)
        
        # 协议配置组
        protocol_group = QGroupBox("协议配置")
        protocol_layout = QVBoxLayout()
        
        protocol_toolbar = QHBoxLayout()
        self.add_protocol_btn = QPushButton("添加协议")
        self.edit_protocol_btn = QPushButton("编辑协议")
        self.delete_protocol_btn = QPushButton("删除协议")
        
        protocol_toolbar.addWidget(self.add_protocol_btn)
        protocol_toolbar.addWidget(self.edit_protocol_btn)
        protocol_toolbar.addWidget(self.delete_protocol_btn)
        protocol_toolbar.addStretch()
        
        self.protocol_table = QTableWidget()
        self.protocol_table.setColumnCount(4)
        self.protocol_table.setHorizontalHeaderLabels(["协议类型", "主机地址", "端口", "状态"])
        self.protocol_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        protocol_layout.addLayout(protocol_toolbar)
        protocol_layout.addWidget(self.protocol_table)
        protocol_group.setLayout(protocol_layout)
        
        # 变量配置组
        variable_group = QGroupBox("变量配置")
        variable_layout = QVBoxLayout()
        
        variable_toolbar = QHBoxLayout()
        self.add_variable_btn = QPushButton("添加变量")
        self.edit_variable_btn = QPushButton("编辑变量")
        self.delete_variable_btn = QPushButton("删除变量")
        
        variable_toolbar.addWidget(self.add_variable_btn)
        variable_toolbar.addWidget(self.edit_variable_btn)
        variable_toolbar.addWidget(self.delete_variable_btn)
        variable_toolbar.addStretch()
        
        self.variable_table = QTableWidget()
        self.variable_table.setColumnCount(5)  # 增加一列用于显示实时值
        self.variable_table.setHorizontalHeaderLabels(["变量名", "设备", "数据类型", "采集周期", "实时值"])
        self.variable_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        variable_layout.addLayout(variable_toolbar)
        variable_layout.addWidget(self.variable_table)
        variable_group.setLayout(variable_layout)
        
        # 添加所有组到信息面板
        info_layout.addWidget(basic_group)
        info_layout.addWidget(protocol_group)
        info_layout.addWidget(variable_group)
        
        # 添加组件到分割器
        self.main_splitter.addWidget(self.tree_widget)
        self.main_splitter.addWidget(self.info_panel)
        self.main_splitter.setStretchFactor(0, 1)
        self.main_splitter.setStretchFactor(1, 2)
        
        main_layout.addWidget(self.main_splitter)

        # 初始状态
        self.update_button_states()
        
    def setup_connections(self):
        """Setup signal connections for all interactive elements"""
        self.tree_widget.itemSelectionChanged.connect(self.on_selection_changed)
        self.add_btn.clicked.connect(self.add_forwarding)
        self.edit_btn.clicked.connect(self.edit_forwarding)
        self.delete_btn.clicked.connect(self.delete_forwarding)
        self.start_btn.clicked.connect(self.start_forwarding)
        self.stop_btn.clicked.connect(self.stop_forwarding)
        
        self.add_protocol_btn.clicked.connect(self.add_protocol)
        self.edit_protocol_btn.clicked.connect(self.edit_protocol)
        self.delete_protocol_btn.clicked.connect(self.delete_protocol)
        
        self.add_variable_btn.clicked.connect(self.add_variable)
        self.edit_variable_btn.clicked.connect(self.edit_variable)
        self.delete_variable_btn.clicked.connect(self.delete_variable)

    def on_selection_changed(self):
        selected = self.tree_widget.selectedItems()
        if selected:
            self.update_info_panel(selected[0])
        else:
            self.update_info_panel(None)
        self.update_button_states()

    def update_button_states(self):
        selected = self.tree_widget.selectedItems()
        has_selection = len(selected) > 0
        
        # Disable all buttons by default
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        
        self.add_protocol_btn.setEnabled(False)
        self.edit_protocol_btn.setEnabled(False)
        self.delete_protocol_btn.setEnabled(False)
        
        self.add_variable_btn.setEnabled(False)
        self.edit_variable_btn.setEnabled(False)
        self.delete_variable_btn.setEnabled(False)

        if has_selection:
            item = selected[0]
            item_type = item.data(0, Qt.UserRole)
            
            if item_type == "forwarding":
                self.edit_btn.setEnabled(True)
                self.delete_btn.setEnabled(True)
                if item.text(2) == "未启动":
                    self.start_btn.setEnabled(True)
                else:
                    self.stop_btn.setEnabled(True)
            
            elif item_type == "protocols_group":
                self.add_protocol_btn.setEnabled(True)
            
            elif item_type == "protocol":
                self.edit_protocol_btn.setEnabled(True)
                self.delete_protocol_btn.setEnabled(True)
                self.add_variable_btn.setEnabled(True)
            
            elif item_type == "variable":
                self.edit_variable_btn.setEnabled(True)
                self.delete_variable_btn.setEnabled(True)

    def load_saved_configs(self):
        """加载保存的转发配置"""
        configs = self.forwarding_manager.get_all_configs()
        for config in configs:
            self.add_forwarding_to_tree(config)

    def add_forwarding_to_tree(self, config: ForwardingConfig):
        """将转发配置添加到树视图"""
        item = QTreeWidgetItem(self.tree_widget)
        item.setText(0, config.name)
        item.setText(1, config.description)
        item.setText(2, config.status)
        item.setData(0, Qt.UserRole, "forwarding")
        
        # 添加协议组
        protocols_group = QTreeWidgetItem(item)
        protocols_group.setText(0, "协议")
        protocols_group.setText(1, "转发协议配置组")
        protocols_group.setData(0, Qt.UserRole, "protocols_group")
        
        # 添加协议
        for protocol in config.protocols:
            protocol_item = QTreeWidgetItem(protocols_group)
            protocol_item.setText(0, protocol.name)
            protocol_item.setText(1, f"{protocol.type} - {protocol.description}")
            protocol_item.setText(2, protocol.status)
            protocol_item.setData(0, Qt.UserRole, "protocol")
        
        self.tree_widget.addTopLevelItem(item)
        item.setExpanded(True)
        protocols_group.setExpanded(True)

    def save_current_config(self):
        """保存当前选中的转发配置"""
        selected = self.tree_widget.selectedItems()
        if not selected or selected[0].data(0, Qt.UserRole) != "forwarding":
            return
            
        item = selected[0]
        protocols = []
        variables = []
        
        # 收集协议信息
        protocols_group = None
        for i in range(item.childCount()):
            if item.child(i).data(0, Qt.UserRole) == "protocols_group":
                protocols_group = item.child(i)
                break
        
        if protocols_group:
            for i in range(protocols_group.childCount()):
                protocol_item = protocols_group.child(i)
                protocol_info = protocol_item.text(1).split(" - ")
                protocol_type = protocol_info[0]
                protocol_desc = protocol_info[1] if len(protocol_info) > 1 else ""
                
                # 从协议表格获取详细信息
                protocol = None
                for row in range(self.protocol_table.rowCount()):
                    if self.protocol_table.item(row, 0).text() == protocol_type:
                        protocol = ForwardingProtocol(
                            name=protocol_item.text(0),
                            type=protocol_type,
                            host=self.protocol_table.item(row, 1).text(),
                            port=self.protocol_table.item(row, 2).text(),
                            topic="",  # 从对话框中获取
                            description=protocol_desc,
                            status=protocol_item.text(2)
                        )
                        break
                if protocol:
                    protocols.append(protocol)
        
        # 收集变量信息
        for row in range(self.variable_table.rowCount()):
            variable = ForwardingVariable(
                name=self.variable_table.item(row, 0).text(),
                device=self.variable_table.item(row, 1).text(),
                data_type=self.variable_table.item(row, 2).text(),
                sampling_rate=self.variable_table.item(row, 3).text(),
                description="",  # 从变量对话框中获取
                status="已配置"
            )
            variables.append(variable)
        
        # 创建配置对象
        config = ForwardingConfig(
            name=item.text(0),
            description=item.text(1),
            status=item.text(2),
            protocols=protocols,
            variables=variables
        )
        
        # 获取配置在列表中的索引
        index = self.tree_widget.indexOfTopLevelItem(item)
        if index >= 0:
            self.forwarding_manager.update_config(index, config)
        else:
            self.forwarding_manager.add_config(config)

    def add_forwarding(self):
        dialog = ForwardingDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # 创建新的转发配置
            config = ForwardingConfig(
                name=dialog.name_edit.text(),
                description=dialog.desc_edit.text(),
                status="未启动",
                protocols=[],
                variables=[]
            )
            
            # 添加到树视图
            self.add_forwarding_to_tree(config)
            
            # 保存配置
            self.forwarding_manager.add_config(config)

    def edit_forwarding(self):
        item = self.tree_widget.selectedItems()[0]
        dialog = ForwardingDialog(self)
        dialog.name_edit.setText(item.text(0))
        dialog.desc_edit.setText(item.text(1))
        if dialog.exec_() == QDialog.Accepted:
            item.setText(0, dialog.name_edit.text())
            item.setText(1, dialog.desc_edit.text())
            self.save_current_config()

    def delete_forwarding(self):
        item = self.tree_widget.selectedItems()[0]
        index = self.tree_widget.indexOfTopLevelItem(item)
        if index >= 0:
            self.forwarding_manager.delete_config(index)
        self.tree_widget.takeTopLevelItem(index)

    def start_forwarding(self):
        """启动转发并开始监测实时数据"""
        item = self.tree_widget.selectedItems()[0]
        item.setText(2, "运行中")
        self.update_button_states()
        
        # 启动实时数据监测定时器
        self.monitoring_timer.start()
        
        # 更新协议状态
        for row in range(self.protocol_table.rowCount()):
            status_item = QTableWidgetItem("已连接")
            status_item.setForeground(QColor("#00FF00"))  # 绿色表示运行中
            self.protocol_table.setItem(row, 3, status_item)
        
        # 保存状态
        self.save_current_config()

    def stop_forwarding(self):
        """停止转发和实时数据监测"""
        item = self.tree_widget.selectedItems()[0]
        item.setText(2, "未启动")
        self.update_button_states()
        
        # 停止实时数据监测定时器
        self.monitoring_timer.stop()
        
        # 更新协议状态
        for row in range(self.protocol_table.rowCount()):
            status_item = QTableWidgetItem("未连接")
            status_item.setForeground(QColor("#FF0000"))  # 红色表示停止
            self.protocol_table.setItem(row, 3, status_item)
        
        # 保存状态
        self.save_current_config()

    def add_protocol(self):
        if not self.tree_widget.selectedItems():
            return
            
        selected_item = self.tree_widget.selectedItems()[0]
        
        # 找到协议组
        if selected_item.data(0, Qt.UserRole) == "protocols_group":
            protocols_group = selected_item
        else:
            # 遍历查找协议组
            for i in range(selected_item.childCount()):
                if selected_item.child(i).data(0, Qt.UserRole) == "protocols_group":
                    protocols_group = selected_item.child(i)
                    break
            else:
                return
            
        dialog = ProtocolDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            protocol_item = QTreeWidgetItem(protocols_group)
            protocol_item.setText(0, dialog.name_edit.text())
            protocol_item.setText(1, f"{dialog.type_combo.currentText()} - {dialog.desc_edit.text()}")
            protocol_item.setText(2, "未配置")
            protocol_item.setData(0, Qt.UserRole, "protocol")
            protocols_group.setExpanded(True)
            
            # 更新协议表格
            row = self.protocol_table.rowCount()
            self.protocol_table.insertRow(row)
            self.protocol_table.setItem(row, 0, QTableWidgetItem(dialog.type_combo.currentText()))
            self.protocol_table.setItem(row, 1, QTableWidgetItem(dialog.host_edit.text()))
            self.protocol_table.setItem(row, 2, QTableWidgetItem(dialog.port_edit.text()))
            self.protocol_table.setItem(row, 3, QTableWidgetItem("未连接"))
            
            # 保存配置
            self.save_current_config()

    def edit_protocol(self):
        item = self.tree_widget.selectedItems()[0]
        dialog = ProtocolDialog(self)
        dialog.name_edit.setText(item.text(0))
        desc = item.text(1).split(" - ")[1] if " - " in item.text(1) else ""
        dialog.desc_edit.setText(desc)
        if dialog.exec_() == QDialog.Accepted:
            item.setText(0, dialog.name_edit.text())
            item.setText(1, f"{dialog.type_combo.currentText()} - {dialog.desc_edit.text()}")
            
            # 更新协议表格
            for row in range(self.protocol_table.rowCount()):
                if self.protocol_table.item(row, 0).text() == dialog.type_combo.currentText():
                    self.protocol_table.setItem(row, 1, QTableWidgetItem(dialog.host_edit.text()))
                    self.protocol_table.setItem(row, 2, QTableWidgetItem(dialog.port_edit.text()))
                    break
            
            # 保存配置
            self.save_current_config()

    def delete_protocol(self):
        item = self.tree_widget.selectedItems()[0]
        if item.childCount() > 0:
            QMessageBox.warning(self, "警告", "请先删除所有变量")
            return
            
        # 从协议表格中删除
        protocol_type = item.text(1).split(" - ")[0]
        for row in range(self.protocol_table.rowCount()):
            if self.protocol_table.item(row, 0).text() == protocol_type:
                self.protocol_table.removeRow(row)
                break
        
        # 从树中删除
        parent = item.parent()
        if parent:
            parent.removeChild(item)
        
        # 保存配置
        self.save_current_config()

    def add_variable(self):
        if not self.tree_widget.selectedItems():
            return
            
        selected_item = self.tree_widget.selectedItems()[0]
        item_type = selected_item.data(0, Qt.UserRole)
        
        if item_type not in ["protocol"]:
            return
            
        dialog = VariableDialog(self.project_manager, self)
        if dialog.exec_() == QDialog.Accepted:
            selected_variables = dialog.get_selected_variables()
            for var in selected_variables:
                # 添加到树视图
                item = QTreeWidgetItem(selected_item)
                item.setText(0, var['name'])
                item.setText(1, f"{var['device']}/{var['name']} - {var['description']}")
                item.setText(2, "未配置")
                item.setData(0, Qt.UserRole, "variable")
                
                # 添加到变量表格
                row = self.variable_table.rowCount()
                self.variable_table.insertRow(row)
                self.variable_table.setItem(row, 0, QTableWidgetItem(var['name']))
                self.variable_table.setItem(row, 1, QTableWidgetItem(var['device']))
                self.variable_table.setItem(row, 2, QTableWidgetItem(var['data_type']))
                self.variable_table.setItem(row, 3, QTableWidgetItem("1000"))  # 默认采样率1秒
                self.variable_table.setItem(row, 4, QTableWidgetItem(""))  # 实时值列
            
            selected_item.setExpanded(True)
            
            # 保存配置
            self.save_current_config()

    def edit_variable(self):
        item = self.tree_widget.selectedItems()[0]
        dialog = VariableDialog(self.project_manager, self)
        if dialog.exec_() == QDialog.Accepted:
            selected_variables = dialog.get_selected_variables()
            if selected_variables:
                var = selected_variables[0]
                item.setText(0, var['name'])
                item.setText(1, f"{var['device']}/{var['name']} - {var['description']}")
                
                # 更新变量表格
                for row in range(self.variable_table.rowCount()):
                    if self.variable_table.item(row, 0).text() == var['name']:
                        self.variable_table.setItem(row, 1, QTableWidgetItem(var['device']))
                        self.variable_table.setItem(row, 2, QTableWidgetItem(var['data_type']))
                        break
                
                # 保存配置
                self.save_current_config()

    def delete_variable(self):
        item = self.tree_widget.selectedItems()[0]
        
        # 从变量表格中删除
        variable_name = item.text(0)
        for row in range(self.variable_table.rowCount()):
            if self.variable_table.item(row, 0).text() == variable_name:
                self.variable_table.removeRow(row)
                break
        
        # 从树中删除
        parent = item.parent()
        if parent:
            parent.removeChild(item)
        
        # 保存配置
        self.save_current_config()

    def update_info_panel(self, item=None):
        if not item:
            # Clear all labels if no item selected
            self.name_label.setText("名称：")
            self.desc_label.setText("描述：")
            self.status_label.setText("状态：")
            self.name_value.setText("")
            self.desc_value.setText("")
            self.status_value.setText("")
            return

        item_type = item.data(0, Qt.UserRole)
        self.name_label.setText(f"名称：")
        self.desc_label.setText(f"描述：")
        self.status_label.setText(f"状态：")
        self.name_value.setText(item.text(0))
        self.desc_value.setText(item.text(1))
        self.status_value.setText(item.text(2))
        
        type_text = ""
        if item_type == "forwarding":
            type_text = "数据转发"
        elif item_type == "protocol":
            type_text = "协议"
        
        self.name_label.setText(f"名称：{item.text(0)}")
        self.desc_label.setText(f"描述：{item.text(1)}")
        self.status_label.setText(f"状态：{item.text(2)}")

    def update_monitoring_data(self):
        """更新变量的实时数据"""
        if not self.tree_widget.selectedItems():
            return
            
        selected_item = self.tree_widget.selectedItems()[0]
        if selected_item.data(0, Qt.UserRole) != "forwarding":
            return
            
        # 更新变量表中的实时值
        for row in range(self.variable_table.rowCount()):
            device_name = self.variable_table.item(row, 1).text()
            variable_name = self.variable_table.item(row, 0).text()
            
            # 从项目管理器获取实时值
            device = next((dev for dev in self.project_manager.current_project.devices 
                         if dev.name == device_name), None)
            if device:
                variable = next((var for var in device.variables 
                               if var.name == variable_name), None)
                if variable:
                    # 获取实时值并更新表格
                    real_time_value = variable.get_real_time_value()  # 这个方法需要在变量类中实现
                    value_item = QTableWidgetItem(str(real_time_value))
                    self.variable_table.setItem(row, 4, value_item)

    def apply_filters(self):
        """应用筛选条件到转发配置树"""
        forwarding_text = self.forwarding_filter.text().lower()
        protocol_text = self.protocol_filter.currentText()
        variable_text = self.variable_filter.text().lower()
        
        # 遍历所有顶层项目（转发配置）
        for i in range(self.tree_widget.topLevelItemCount()):
            forwarding_item = self.tree_widget.topLevelItem(i)
            forwarding_visible = not forwarding_text or forwarding_text in forwarding_item.text(0).lower()
            
            # 检查协议组
            protocol_group = None
            for j in range(forwarding_item.childCount()):
                if forwarding_item.child(j).data(0, Qt.UserRole) == "protocols_group":
                    protocol_group = forwarding_item.child(j)
                    break
            
            if protocol_group:
                # 检查协议
                protocol_match = False
                for j in range(protocol_group.childCount()):
                    protocol_item = protocol_group.child(j)
                    protocol_visible = (protocol_text == "全部" or 
                                     protocol_text in protocol_item.text(1))
                    protocol_item.setHidden(not protocol_visible)
                    
                    if protocol_visible:
                        protocol_match = True
                        
                        # 检查变量
                        for k in range(protocol_item.childCount()):
                            variable_item = protocol_item.child(k)
                            variable_visible = not variable_text or variable_text in variable_item.text(0).lower()
                            variable_item.setHidden(not variable_visible)
                            
                            # 如果有任何可见的变量，保持协议可见
                            if variable_visible:
                                protocol_visible = True
                    
                    protocol_item.setHidden(not protocol_visible)
                
                protocol_group.setHidden(not protocol_match)
            
            # 设置转发配置的可见性
            forwarding_item.setHidden(not (forwarding_visible and (not protocol_text or protocol_match)))
