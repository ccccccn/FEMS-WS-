#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
from datetime import datetime, timedelta
import pandas as pd
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QLabel, QComboBox, QLineEdit, QDateTimeEdit, 
    QPushButton, QTableView, QCheckBox, QFileDialog,
    QHeaderView, QSplitter, QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QDateTime, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QStandardItemModel, QStandardItem

from frontend.models.project_model import ProjectManager

logger = logging.getLogger(__name__)

class HistoryView(QWidget):
    """历史数据查询视图，用于查询和显示历史数据"""
    
    def __init__(self, project_manager, parent=None):
        super().__init__(parent)
        self.project_manager = project_manager
        self.main_window = parent
        self.selected_variables = []
        self.history_data = []
        self.init_ui()
    
    def set_main_window(self, main_window):
        """设置主窗口引用"""
        self.main_window = main_window
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout()
        
        # 顶部布局，包含标题和返回按钮
        top_layout = QHBoxLayout()
        
        # 返回按钮
        self.back_btn = QPushButton("返回")
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.setMaximumWidth(100)
        top_layout.addWidget(self.back_btn)
        
        # 标题
        title_label = QLabel("历史数据查询")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(title_label)
        
        # 添加一个空白widget以保持布局对称
        empty_widget = QWidget()
        empty_widget.setMaximumWidth(100)
        top_layout.addWidget(empty_widget)
        
        layout.addLayout(top_layout)
        
        # 创建筛选面板
        filter_panel = QGroupBox("查询条件")
        filter_layout = QVBoxLayout()
        
        # 项目和设备选择
        project_device_layout = QHBoxLayout()
        
        # 项目选择
        self.project_combo = QComboBox()
        self.project_combo.currentIndexChanged.connect(self.on_project_changed)
        project_device_layout.addWidget(QLabel("项目:"))
        project_device_layout.addWidget(self.project_combo)
        
        # 设备选择
        self.device_combo = QComboBox()
        self.device_combo.currentIndexChanged.connect(self.on_device_changed)
        project_device_layout.addWidget(QLabel("设备:"))
        project_device_layout.addWidget(self.device_combo)
        
        filter_layout.addLayout(project_device_layout)
        
        # 变量筛选
        variable_filter_layout = QHBoxLayout()
        
        # 变量搜索
        self.variable_search = QLineEdit()
        self.variable_search.setPlaceholderText("输入变量名称进行筛选...")
        self.variable_search.textChanged.connect(self.filter_variables)
        variable_filter_layout.addWidget(QLabel("变量筛选:"))
        variable_filter_layout.addWidget(self.variable_search)
        
        # 数据类型筛选
        self.data_type_combo = QComboBox()
        self.data_type_combo.addItem("全部类型")
        self.data_type_combo.currentTextChanged.connect(self.filter_variables)
        variable_filter_layout.addWidget(QLabel("数据类型:"))
        variable_filter_layout.addWidget(self.data_type_combo)
        
        filter_layout.addLayout(variable_filter_layout)
        
        # 时间范围选择
        time_range_layout = QHBoxLayout()
        
        # 开始时间
        self.start_time = QDateTimeEdit()
        self.start_time.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.start_time.setDateTime(QDateTime.currentDateTime().addDays(-1))
        self.start_time.setCalendarPopup(True)
        time_range_layout.addWidget(QLabel("开始时间:"))
        time_range_layout.addWidget(self.start_time)
        
        # 结束时间
        self.end_time = QDateTimeEdit()
        self.end_time.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.end_time.setDateTime(QDateTime.currentDateTime())
        self.end_time.setCalendarPopup(True)
        time_range_layout.addWidget(QLabel("结束时间:"))
        time_range_layout.addWidget(self.end_time)
        
        # 快速时间选择
        self.time_preset_combo = QComboBox()
        self.time_preset_combo.addItems(["自定义", "最近1小时", "最近24小时", "最近7天", "最近30天"])
        self.time_preset_combo.currentTextChanged.connect(self.apply_time_preset)
        time_range_layout.addWidget(QLabel("快速选择:"))
        time_range_layout.addWidget(self.time_preset_combo)
        
        filter_layout.addLayout(time_range_layout)
        
        # 查询按钮
        button_layout = QHBoxLayout()
        
        self.query_btn = QPushButton("查询数据")
        self.query_btn.clicked.connect(self.query_history_data)
        button_layout.addWidget(self.query_btn)
        
        self.export_btn = QPushButton("导出数据")
        self.export_btn.clicked.connect(self.export_data)
        self.export_btn.setEnabled(False)
        button_layout.addWidget(self.export_btn)
        
        self.clear_btn = QPushButton("清空结果")
        self.clear_btn.clicked.connect(self.clear_results)
        button_layout.addWidget(self.clear_btn)
        
        filter_layout.addLayout(button_layout)
        
        filter_panel.setLayout(filter_layout)
        layout.addWidget(filter_panel)
        
        # 创建分割器，上方是变量列表，下方是数据表格
        splitter = QSplitter(Qt.Vertical)
        
        # 变量列表面板
        variables_panel = QGroupBox("变量列表")
        variables_layout = QVBoxLayout()
        
        # 变量表格
        self.variable_model = QStandardItemModel()
        self.variable_model.setHorizontalHeaderLabels(["选择", "变量名", "设备", "数据类型", "地址"])
        
        self.variable_proxy_model = QSortFilterProxyModel()
        self.variable_proxy_model.setSourceModel(self.variable_model)
        self.variable_proxy_model.setFilterKeyColumn(1)  # 按变量名筛选
        
        self.variable_table = QTableView()
        self.variable_table.setModel(self.variable_proxy_model)
        self.variable_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.variable_table.setSelectionBehavior(QTableView.SelectRows)
        self.variable_table.setEditTriggers(QTableView.NoEditTriggers)
        self.variable_table.clicked.connect(self.on_variable_clicked)
        
        variables_layout.addWidget(self.variable_table)
        
        # 全选/取消全选
        select_layout = QHBoxLayout()
        self.select_all_btn = QPushButton("全选")
        self.select_all_btn.clicked.connect(self.select_all_variables)
        select_layout.addWidget(self.select_all_btn)
        
        self.deselect_all_btn = QPushButton("取消全选")
        self.deselect_all_btn.clicked.connect(self.deselect_all_variables)
        select_layout.addWidget(self.deselect_all_btn)
        
        self.selected_count_label = QLabel("已选择: 0 个变量")
        select_layout.addWidget(self.selected_count_label)
        
        variables_layout.addLayout(select_layout)
        
        variables_panel.setLayout(variables_layout)
        splitter.addWidget(variables_panel)
        
        # 数据表格面板
        data_panel = QGroupBox("历史数据")
        data_layout = QVBoxLayout()
        
        # 数据表格
        self.data_model = QStandardItemModel()
        self.data_table = QTableView()
        self.data_table.setModel(self.data_model)
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.data_table.setEditTriggers(QTableView.NoEditTriggers)
        
        data_layout.addWidget(self.data_table)
        
        # 状态信息
        self.status_label = QLabel("就绪")
        data_layout.addWidget(self.status_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        data_layout.addWidget(self.progress_bar)
        
        data_panel.setLayout(data_layout)
        splitter.addWidget(data_panel)
        
        # 设置分割器初始比例
        splitter.setSizes([300, 500])
        
        layout.addWidget(splitter)
        
        self.setLayout(layout)
        
        # 加载项目列表
        self.load_projects()
    
    def load_projects(self):
        """加载项目列表"""
        self.project_combo.clear()
        
        if not self.project_manager.projects:
            self.project_combo.addItem("无项目")
            self.project_combo.setEnabled(False)
            return
        
        self.project_combo.setEnabled(True)
        for project in self.project_manager.projects:
            self.project_combo.addItem(project.name, project)
        
        # 如果有当前项目，选择它
        if self.project_manager.current_project:
            for i in range(self.project_combo.count()):
                project = self.project_combo.itemData(i)
                if project and project.project_id == self.project_manager.current_project.project_id:
                    self.project_combo.setCurrentIndex(i)
                    break
    
    def on_project_changed(self, index):
        """处理项目选择变化"""
        if index < 0:
            return
        
        project = self.project_combo.itemData(index)
        if not project:
            self.device_combo.clear()
            self.device_combo.setEnabled(False)
            self.clear_variable_table()
            return
        
        # 加载设备列表
        self.device_combo.clear()
        self.device_combo.setEnabled(True)
        
        # 添加"所有设备"选项
        self.device_combo.addItem("所有设备", None)
        
        for device in project.devices:
            self.device_combo.addItem(device.name, device)
        
        # 更新变量列表
        self.update_variable_list()
        
        # 更新数据类型筛选下拉框
        self.update_data_type_filter()
    
    def on_device_changed(self, index):
        """处理设备选择变化"""
        self.update_variable_list()
        self.update_data_type_filter()
    
    def update_variable_list(self):
        """更新变量列表"""
        self.clear_variable_table()
        
        project_index = self.project_combo.currentIndex()
        if project_index < 0:
            return
        
        project = self.project_combo.itemData(project_index)
        if not project:
            return
        
        device_index = self.device_combo.currentIndex()
        if device_index < 0:
            return
        
        device = self.device_combo.itemData(device_index)
        
        if device:  # 选择了特定设备
            for variable in device.variables:
                self.add_variable_to_table(variable, device.name)
        else:  # "所有设备"选项
            for device in project.devices:
                for variable in device.variables:
                    self.add_variable_to_table(variable, device.name)
        
        # 更新状态信息
        total_variables = self.variable_model.rowCount()
        self.status_label.setText(f"共 {total_variables} 个变量可供查询")
    
    def add_variable_to_table(self, variable, device_name):
        """添加变量到表格"""
        # 创建复选框项
        checkbox_item = QStandardItem()
        checkbox_item.setCheckable(True)
        checkbox_item.setCheckState(Qt.Unchecked)
        
        # 创建其他列
        name_item = QStandardItem(variable.name)
        device_item = QStandardItem(device_name)
        data_type_item = QStandardItem(variable.data_type)
        address_item = QStandardItem(variable.address if hasattr(variable, 'address') else "")
        
        # 添加到模型
        row = self.variable_model.rowCount()
        self.variable_model.setItem(row, 0, checkbox_item)
        self.variable_model.setItem(row, 1, name_item)
        self.variable_model.setItem(row, 2, device_item)
        self.variable_model.setItem(row, 3, data_type_item)
        self.variable_model.setItem(row, 4, address_item)
        
        # 存储变量对象引用
        name_item.setData(variable)
    
    def clear_variable_table(self):
        """清空变量表格"""
        self.variable_model.clear()
        self.variable_model.setHorizontalHeaderLabels(["选择", "变量名", "设备", "数据类型", "地址"])
        self.selected_variables = []
        self.update_selected_count()
    
    def update_data_type_filter(self):
        """更新数据类型筛选下拉框"""
        self.data_type_combo.clear()
        self.data_type_combo.addItem("全部类型")
        
        data_types = set()
        
        for row in range(self.variable_model.rowCount()):
            data_type = self.variable_model.item(row, 3).text()
            data_types.add(data_type)
        
        for data_type in sorted(data_types):
            self.data_type_combo.addItem(data_type)
    
    def filter_variables(self):
        """筛选变量列表"""
        search_text = self.variable_search.text().lower()
        data_type = self.data_type_combo.currentText()
        
        for row in range(self.variable_model.rowCount()):
            variable_name = self.variable_model.item(row, 1).text().lower()
            variable_data_type = self.variable_model.item(row, 3).text()
            
            name_match = search_text in variable_name
            type_match = data_type == "全部类型" or data_type == variable_data_type
            
            self.variable_table.setRowHidden(row, not (name_match and type_match))
    
    def on_variable_clicked(self, index):
        """处理变量表格点击事件"""
        if index.column() != 0:  # 如果不是点击复选框列，则忽略
            source_index = self.variable_proxy_model.mapToSource(index)
            row = source_index.row()
            checkbox_item = self.variable_model.item(row, 0)
            
            # 切换复选框状态
            new_state = Qt.Checked if checkbox_item.checkState() == Qt.Unchecked else Qt.Unchecked
            checkbox_item.setCheckState(new_state)
            
            # 更新选中变量列表
            self.update_selected_variables()
    
    def update_selected_variables(self):
        """更新选中的变量列表"""
        self.selected_variables = []
        
        for row in range(self.variable_model.rowCount()):
            checkbox_item = self.variable_model.item(row, 0)
            if checkbox_item and checkbox_item.checkState() == Qt.Checked:
                variable = self.variable_model.item(row, 1).data()
                device_name = self.variable_model.item(row, 2).text()
                if variable:
                    self.selected_variables.append((variable, device_name))
        
        self.update_selected_count()
    
    def update_selected_count(self):
        """更新选中变量计数"""
        count = len(self.selected_variables)
        self.selected_count_label.setText(f"已选择: {count} 个变量")
        
        # 根据是否有选中变量启用或禁用查询按钮
        self.query_btn.setEnabled(count > 0)
    
    def select_all_variables(self):
        """选择所有变量"""
        for row in range(self.variable_model.rowCount()):
            if not self.variable_table.isRowHidden(row):
                source_row = self.variable_proxy_model.mapToSource(
                    self.variable_proxy_model.index(row, 0)
                ).row()
                checkbox_item = self.variable_model.item(source_row, 0)
                if checkbox_item:
                    checkbox_item.setCheckState(Qt.Checked)
        
        self.update_selected_variables()
    
    def deselect_all_variables(self):
        """取消选择所有变量"""
        for row in range(self.variable_model.rowCount()):
            checkbox_item = self.variable_model.item(row, 0)
            if checkbox_item:
                checkbox_item.setCheckState(Qt.Unchecked)
        
        self.update_selected_variables()
    
    def apply_time_preset(self, preset):
        """应用时间预设"""
        if preset == "自定义":
            return
        
        now = QDateTime.currentDateTime()
        
        if preset == "最近1小时":
            self.start_time.setDateTime(now.addSecs(-3600))
        elif preset == "最近24小时":
            self.start_time.setDateTime(now.addDays(-1))
        elif preset == "最近7天":
            self.start_time.setDateTime(now.addDays(-7))
        elif preset == "最近30天":
            self.start_time.setDateTime(now.addDays(-30))
        
        self.end_time.setDateTime(now)
    
    def query_history_data(self):
        """查询历史数据"""
        if not self.selected_variables:
            QMessageBox.warning(self, "警告", "请至少选择一个变量")
            return
        
        start_time = self.start_time.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        end_time = self.end_time.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        
        if self.start_time.dateTime() > self.end_time.dateTime():
            QMessageBox.warning(self, "警告", "开始时间不能晚于结束时间")
            return
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("正在查询历史数据...")
        
        # 清空数据表格
        self.data_model.clear()
        
        # 在实际应用中，这里应该调用后端API获取历史数据
        # 这里使用模拟数据进行演示
        self.history_data = self.generate_sample_data(start_time, end_time)
        
        # 设置表头
        headers = ["时间戳"]
        for variable, device_name in self.selected_variables:
            headers.append(f"{device_name} - {variable.name}")
        self.data_model.setHorizontalHeaderLabels(headers)
        
        # 填充数据
        for i, data_point in enumerate(self.history_data):
            row = []
            # 添加时间戳
            row.append(QStandardItem(data_point["timestamp"]))
            
            # 添加各变量的值
            for variable, _ in self.selected_variables:
                value = data_point.get(variable.name, "")
                row.append(QStandardItem(str(value)))
            
            self.data_model.appendRow(row)
            
            # 更新进度条
            progress = int((i + 1) / len(self.history_data) * 100)
            self.progress_bar.setValue(progress)
        
        # 更新状态
        self.status_label.setText(f"查询完成，共 {len(self.history_data)} 条记录")
        self.progress_bar.setVisible(False)
        
        # 启用导出按钮
        self.export_btn.setEnabled(True)
    
    def generate_sample_data(self, start_time, end_time):
        """生成样本数据（实际应用中应替换为真实数据查询）"""
        import random
        from datetime import datetime, timedelta
        
        # 将字符串转换为datetime对象
        start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        
        # 计算时间范围内的点数（每10分钟一个点）
        time_delta = end_dt - start_dt
        total_minutes = time_delta.total_seconds() / 60
        num_points = min(int(total_minutes / 10) + 1, 1000)  # 最多1000个点
        
        # 生成时间点
        time_points = []
        if num_points > 1:
            interval = time_delta / (num_points - 1)
            for i in range(num_points):
                time_points.append(start_dt + interval * i)
        else:
            time_points.append(start_dt)
        
        # 生成数据
        data = []
        for time_point in time_points:
            data_point = {"timestamp": time_point.strftime("%Y-%m-%d %H:%M:%S")}
            
            for variable, _ in self.selected_variables:
                # 根据变量类型生成不同的随机数据
                if variable.data_type.lower() in ["int", "integer", "word", "dword"]:
                    data_point[variable.name] = random.randint(0, 100)
                elif variable.data_type.lower() in ["float", "real", "double"]:
                    data_point[variable.name] = round(random.uniform(0, 100), 2)
                elif variable.data_type.lower() in ["bool", "boolean", "bit"]:
                    data_point[variable.name] = random.choice([True, False])
                else:
                    data_point[variable.name] = f"Value-{random.randint(1, 100)}"
            
            data.append(data_point)
        
        return data
    
    def export_data(self):
        """导出数据为CSV或Excel文件"""
        if not self.history_data:
            QMessageBox.warning(self, "警告", "没有可导出的数据")
            return
        
        # 创建文件保存对话框
        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setNameFilter("CSV 文件 (*.csv);;Excel 文件 (*.xlsx)")
        file_dialog.setDefaultSuffix("csv")
        
        if not file_dialog.exec_():
            return
        
        file_path = file_dialog.selectedFiles()[0]
        file_format = "csv" if file_path.endswith(".csv") else "xlsx"
        
        try:
            # 创建DataFrame
            df = pd.DataFrame(self.history_data)
            
            # 导出数据
            if file_format == "csv":
                df.to_csv(file_path, index=False, encoding="utf-8-sig")
            else:
                df.to_excel(file_path, index=False)
            
            QMessageBox.information(self, "导出成功", f"数据已成功导出到\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出数据时发生错误：{str(e)}")
    
    def clear_results(self):
        """清空查询结果"""
        self.data_model.clear()
        self.data_model.setHorizontalHeaderLabels(["时间戳"])
        self.history_data = []
        self.status_label.setText("已清空查询结果")
        self.export_btn.setEnabled(False)
    
    def showEvent(self, event):
        """当视图显示时调用"""
        super().showEvent(event)
        
        # 重新加载项目列表
        self.load_projects()
        
        # 更新数据类型筛选下拉框
        self.update_data_type_filter() 
    
    def go_back(self):
        """返回上一个视图，并恢复树形视图"""
        if self.main_window:
            # 返回到设备视图
            self.main_window.goto_devices() 