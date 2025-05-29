#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import time
from datetime import datetime
import pandas as pd
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QLabel, QPushButton, QComboBox, QCheckBox,
    QTableWidget, QTableWidgetItem, QHeaderView, 
    QTabWidget, QSplitter, QGroupBox, QFrame,
    QFileDialog, QMessageBox, QTableView, QFormLayout,
    QSpinBox, QLineEdit
)
from PyQt5.QtCore import Qt, QTimer, pyqtSlot, QAbstractTableModel, QModelIndex, QVariant
from PyQt5.QtGui import QColor, QFont, QIcon

from backend.data_fetcher import DataFetcher
from frontend.models.variable_model import Variable

logger = logging.getLogger(__name__)

class MonitoringTableModel(QAbstractTableModel):
    """用于显示监控数据的表格模型"""

    def __init__(self):
    # def __init__(self, parent=None):
        super().__init__()
        self.variables = []
        self.filtered_variables = []  # 筛选后的变量列表
        self.headers = ["变量名", "设备", "数据类型", "当前值", "状态", "更新时间", "地址"]
        
        # 筛选条件
        self.filter_text = ""
        self.filter_status = "全部"
        self.filter_data_type = "全部"
    
    def rowCount(self, parent=QModelIndex()):
        return len(self.filtered_variables)
    
    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)
    
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self.filtered_variables)):
            return QVariant()
        
        variable = self.filtered_variables[index.row()]
        column = index.column()
        
        if role == Qt.DisplayRole:
            if column == 0:  # 变量名
                return variable.name
            elif column == 1:  # 设备名
                return variable.device_name if hasattr(variable, 'device_name') else "未知设备"
            elif column == 2:  # 数据类型
                return variable.data_type
            elif column == 3:  # 当前值
                if variable.current_value is None:
                    return "未知"
                value_str = str(variable.current_value)
                if hasattr(variable, 'units') and variable.units:
                    value_str += f" {variable.units}"
                return value_str
            elif column == 4:  # 状态
                return variable.status
            elif column == 5:  # 更新时间
                if variable.last_updated:
                    try:
                        # 尝试将时间戳转换为可读格式
                        if isinstance(variable.last_updated, str):
                            dt = datetime.fromisoformat(variable.last_updated.replace('Z', '+00:00'))
                        else:
                            dt = datetime.fromtimestamp(variable.last_updated / 1000)
                        return dt.strftime("%Y-%m-%d %H:%M:%S")
                    except Exception as e:
                        logger.warning(f"Error formatting timestamp: {e}")
                        return str(variable.last_updated)
                return "未知"
            elif column == 6:  # 地址
                return variable.address
        
        elif role == Qt.BackgroundRole:
            # 根据状态设置背景色
            if column == 4:  # 状态列
                if variable.status == "报警":
                    return QColor(255, 100, 100, 150)  # 红色表示报警
                elif variable.status == "警告":
                    return QColor(255, 200, 50, 150)   # 黄色表示警告
                else:
                    return QColor(100, 255, 100, 100)  # 绿色表示正常
            
            # 交替行颜色，提高可读性
            if index.row() % 2 == 0:
                return QColor(240, 240, 240, 40)
        
        return QVariant()
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return QVariant()
    
    def set_variables(self, variables):
        """设置要显示的变量列表"""
        self.beginResetModel()
        self.variables = variables
        self.apply_filters()  # 应用筛选
        self.endResetModel()
    
    def update_variable(self, variable):
        """更新单个变量的数据"""
        for i, var in enumerate(self.variables):
            if var.variable_id == variable.variable_id:
                self.variables[i] = variable
                break
        
        # 更新筛选后的列表
        self.apply_filters()
        self.layoutChanged.emit()
    
    def set_filter(self, filter_text="", filter_status="全部", filter_data_type="全部"):
        """设置筛选条件
        
        Args:
            filter_text (str): 搜索文本
            filter_status (str): 状态筛选
            filter_data_type (str): 数据类型筛选
        """
        self.filter_text = filter_text.lower()
        self.filter_status = filter_status
        self.filter_data_type = filter_data_type
        self.apply_filters()
        self.layoutChanged.emit()
    
    def apply_filters(self):
        """应用筛选条件"""
        self.filtered_variables = []
        
        for var in self.variables:
            # 检查是否符合所有筛选条件
            matches = True
            
            # 文本搜索筛选
            if self.filter_text:
                text_match = False
                # 搜索变量名
                if var.name and self.filter_text in var.name.lower():
                    text_match = True
                # 搜索设备名
                elif hasattr(var, 'device_name') and var.device_name and self.filter_text in var.device_name.lower():
                    text_match = True
                # 搜索地址
                elif hasattr(var, 'address') and var.address and self.filter_text in var.address.lower():
                    text_match = True
                
                if not text_match:
                    matches = False
            
            # 状态筛选
            if self.filter_status != "全部" and var.status != self.filter_status:
                matches = False
            
            # 数据类型筛选
            if self.filter_data_type != "全部" and var.data_type != self.filter_data_type:
                matches = False
            
            # 如果符合所有条件，添加到筛选结果
            if matches:
                self.filtered_variables.append(var)

class MonitoringView(QWidget):
    """监控视图，用于实时显示变量数据"""
    
    def __init__(self, project_manager, parent=None):
        super().__init__(parent)
        self.project_manager = project_manager
        self.main_window = parent
        self.monitored_variables = []
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_variables)
        self.update_interval = 1000  # 默认更新间隔1秒
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
        title_label = QLabel("实时数据监控")
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
        
        # 控制面板
        control_panel = QGroupBox("监控控制")
        control_layout = QHBoxLayout()
        
        # 项目选择
        self.project_combo = QComboBox()
        self.project_combo.currentIndexChanged.connect(self.on_project_changed)
        control_layout.addWidget(QLabel("项目:"))
        control_layout.addWidget(self.project_combo)
        
        # 设备选择
        self.device_combo = QComboBox()
        self.device_combo.currentIndexChanged.connect(self.on_device_changed)
        control_layout.addWidget(QLabel("设备:"))
        control_layout.addWidget(self.device_combo)
        
        # 更新间隔
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(100, 10000)  # 100ms到10s
        self.interval_spin.setValue(self.update_interval)
        self.interval_spin.setSingleStep(100)
        self.interval_spin.setSuffix(" ms")
        self.interval_spin.valueChanged.connect(self.set_update_interval)
        control_layout.addWidget(QLabel("更新间隔:"))
        control_layout.addWidget(self.interval_spin)
        
        # 自动刷新开关
        self.auto_refresh = QCheckBox("自动刷新")
        self.auto_refresh.setChecked(False)
        self.auto_refresh.stateChanged.connect(self.toggle_auto_refresh)
        control_layout.addWidget(self.auto_refresh)
        
        # 手动刷新按钮
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.update_variables)
        control_layout.addWidget(self.refresh_btn)
        
        # 监控所有变量按钮
        self.monitor_all_btn = QPushButton("监控所有变量")
        self.monitor_all_btn.clicked.connect(self.monitor_all_variables)
        control_layout.addWidget(self.monitor_all_btn)
        
        # 清除按钮
        self.clear_btn = QPushButton("清除数据")
        self.clear_btn.clicked.connect(self.clear_monitoring_data)
        control_layout.addWidget(self.clear_btn)
        
        # 导出按钮
        self.export_btn = QPushButton("导出数据")
        self.export_btn.clicked.connect(self.export_data)
        control_layout.addWidget(self.export_btn)
        
        control_panel.setLayout(control_layout)
        layout.addWidget(control_panel)
        
        # 添加筛选面板
        filter_panel = QGroupBox("变量筛选")
        filter_layout = QHBoxLayout()
        
        # 搜索框
        self.search_label = QLabel("搜索:")
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入变量名、设备名或地址...")
        self.search_edit.textChanged.connect(self.apply_filters)
        
        # 状态筛选
        self.status_label = QLabel("状态:")
        self.status_combo = QComboBox()
        self.status_combo.addItems(["全部", "正常", "警告", "报警"])
        self.status_combo.currentTextChanged.connect(self.apply_filters)
        
        # 数据类型筛选
        self.data_type_label = QLabel("数据类型:")
        self.data_type_combo = QComboBox()
        self.data_type_combo.addItem("全部")
        self.data_type_combo.addItems(["BOOL", "BYTE", "WORD", "DWORD", "INT", "DINT", "REAL", "STRING"])
        self.data_type_combo.currentTextChanged.connect(self.apply_filters)
        
        # 清除筛选按钮
        self.clear_filter_btn = QPushButton("清除筛选")
        self.clear_filter_btn.clicked.connect(self.clear_filters)
        
        # 筛选结果计数
        self.filter_count_label = QLabel("显示: 0/0")
        
        # 添加到筛选面板布局
        filter_layout.addWidget(self.search_label)
        filter_layout.addWidget(self.search_edit, 2)  # 搜索框占据更多空间
        filter_layout.addWidget(self.status_label)
        filter_layout.addWidget(self.status_combo)
        filter_layout.addWidget(self.data_type_label)
        filter_layout.addWidget(self.data_type_combo)
        filter_layout.addWidget(self.clear_filter_btn)
        filter_layout.addWidget(self.filter_count_label)
        
        filter_panel.setLayout(filter_layout)
        layout.addWidget(filter_panel)
        
        # 创建表格视图
        self.table_model = MonitoringTableModel()
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSortingEnabled(True)
        
        # 添加表格到布局
        layout.addWidget(self.table_view)
        
        # 状态信息
        self.status_label = QLabel("就绪")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # 加载项目列表
        self.load_projects()
    
    def load_projects(self):
        """加载项目列表到下拉框"""
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
        self.update_data_type_filter_options()
    
    def on_device_changed(self, index):
        """处理设备选择变化"""
        self.update_variable_list()
    
    def update_variable_list(self):
        """更新变量列表"""
        self.monitored_variables = []
        
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
                # 添加设备名称属性
                variable.device_name = device.name
                self.monitored_variables.append(variable)
        else:  # "所有设备"选项
            for device in project.devices:
                for variable in device.variables:
                    # 添加设备名称属性
                    variable.device_name = device.name
                    self.monitored_variables.append(variable)
        
        # 更新表格
        self.table_model.set_variables(self.monitored_variables)
        
        # 更新筛选结果计数
        self.update_filter_count()
        
        # 更新状态信息
        self.status_label.setText(f"监控 {len(self.monitored_variables)} 个变量")
    
    def set_update_interval(self, value):
        """设置更新间隔"""
        self.update_interval = value
        
        # 如果定时器正在运行，重新启动它
        if self.update_timer.isActive():
            self.update_timer.stop()
            self.update_timer.start(self.update_interval)
    
    def toggle_auto_refresh(self, state):
        """切换自动刷新状态"""
        if state == Qt.Checked:
            self.update_timer.start(self.update_interval)
            self.refresh_btn.setEnabled(False)
            self.status_label.setText(f"自动刷新中，间隔 {self.update_interval} ms")
        else:
            self.update_timer.stop()
            self.refresh_btn.setEnabled(True)
            self.status_label.setText(f"监控 {len(self.monitored_variables)} 个变量")
    
    def update_variables(self):
        """更新变量数据"""
        if not self.monitored_variables:
            return
        
        try:
            # 在实际应用中，这里应该从设备读取实时数据
            # 在模拟模式下，我们可以随机更新一些值
            import random
            from datetime import datetime
            
            for variable in self.monitored_variables:
                # 模拟值变化
                if variable.data_type == "BOOL":
                    if random.random() > 0.8:  # 20%概率改变布尔值
                        variable.current_value = not variable.current_value
                elif variable.data_type in ["INT", "DINT", "WORD", "DWORD"]:
                    # 在当前值附近波动
                    if variable.current_value is not None:
                        base = variable.current_value
                        variable.current_value = max(0, int(base + random.uniform(-base*0.05, base*0.05)))
                    else:
                        variable.current_value = random.randint(0, 1000)
                elif variable.data_type in ["REAL", "FLOAT"]:
                    # 在当前值附近波动
                    if variable.current_value is not None:
                        base = variable.current_value
                        variable.current_value = max(0, round(base + random.uniform(-base*0.05, base*0.05), 2))
                    else:
                        variable.current_value = round(random.uniform(0, 100), 2)
                
                # 更新时间戳
                variable.last_updated = datetime.now().isoformat()
                
                # 检查阈值并更新状态
                if hasattr(variable, 'threshold') and variable.threshold:
                    variable.status = variable.threshold.check_value(variable.current_value)
            
            # 更新表格，应用筛选条件
            self.table_model.set_variables(self.monitored_variables)
            
            # 更新筛选结果计数
            self.update_filter_count()
            
            # 更新状态栏
            now = datetime.now().strftime("%H:%M:%S")
            if self.auto_refresh.isChecked():
                self.status_label.setText(f"自动刷新中，上次更新: {now}")
            else:
                total_count = len(self.monitored_variables)
                filtered_count = len(self.table_model.filtered_variables)
                if filtered_count < total_count:
                    self.status_label.setText(f"筛选显示 {filtered_count}/{total_count} 个变量，时间: {now}")
                else:
                    self.status_label.setText(f"已更新 {total_count} 个变量，时间: {now}")
                
        except Exception as e:
            logger.error(f"更新变量数据时出错: {str(e)}")
            self.status_label.setText(f"更新失败: {str(e)}")
    
    def monitor_all_variables(self):
        """监控所有项目中的所有变量"""
        self.monitored_variables = []
        
        for project in self.project_manager.projects:
            for device in project.devices:
                for variable in device.variables:
                    # 添加设备名称属性
                    variable.device_name = device.name
                    # 添加项目名称属性
                    variable.project_name = project.name
                    self.monitored_variables.append(variable)
        
        # 更新表格
        self.table_model.set_variables(self.monitored_variables)
        
        # 更新筛选结果计数
        self.update_filter_count()
        
        # 更新状态信息
        self.status_label.setText(f"监控所有项目中的 {len(self.monitored_variables)} 个变量")
        
        # 如果启用了自动刷新，立即更新一次
        if self.auto_refresh.isChecked():
            self.update_variables()
    
    def showEvent(self, event):
        """当视图显示时调用"""
        super().showEvent(event)
        
        # 重新加载项目列表
        self.load_projects()
        
        # 更新数据类型筛选下拉框
        self.update_data_type_filter_options()
        
        # 如果启用了自动刷新，启动定时器
        if self.auto_refresh.isChecked():
            self.update_timer.start(self.update_interval)
    
    def hideEvent(self, event):
        """当视图隐藏时调用"""
        super().hideEvent(event)
        
        # 停止定时器
        if self.update_timer.isActive():
            self.update_timer.stop()
    
    def export_data(self):
        """Export monitoring data to a CSV file."""
        if not self.monitored_variables:
            QMessageBox.warning(self, "导出失败", "没有可导出的数据")
            return
        
        # Create a DataFrame from the monitoring data
        data = []
        columns = ["设备", "变量名", "数据类型", "当前值", "状态", "更新时间", "地址"]
        
        for variable in self.monitored_variables:
            # Skip if no data
            if variable.current_value is None:
                continue
            
            # Format the timestamp
            timestamp = ""
            if variable.last_updated:
                try:
                    if isinstance(variable.last_updated, str):
                        dt = datetime.fromisoformat(variable.last_updated.replace('Z', '+00:00'))
                        timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        timestamp = str(variable.last_updated)
                except Exception:
                    timestamp = str(variable.last_updated)
            
            # Add data row
            data.append([
                variable.device_name if hasattr(variable, 'device_name') else "未知设备",
                variable.name,
                variable.data_type,
                str(variable.current_value),
                variable.status if hasattr(variable, 'status') else "正常",
                timestamp,
                variable.address if hasattr(variable, 'address') else ""
            ])
        
        if not data:
            QMessageBox.warning(self, "导出失败", "没有有效数据可供导出")
            return
        
        # Create DataFrame
        df = pd.DataFrame(data, columns=columns)
        
        # Get export path
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出数据",
            f"monitoring_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        # Export to CSV
        try:
            df.to_csv(file_path, index=False, encoding="utf-8-sig")
            QMessageBox.information(self, "导出成功", f"数据已成功导出到\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"数据导出失败：{str(e)}")
    
    def clear_monitoring_data(self):
        """Clear all monitoring data."""
        # 停止自动刷新
        if self.auto_refresh.isChecked():
            self.auto_refresh.setChecked(False)
        
        # 清空变量列表
        self.monitored_variables = []
        
        # 更新表格
        self.table_model.set_variables(self.monitored_variables)
        
        # 更新状态信息
        self.status_label.setText("监控数据已清除")
    
    def apply_filters(self):
        """应用筛选条件"""
        filter_text = self.search_edit.text()
        filter_status = self.status_combo.currentText()
        filter_data_type = self.data_type_combo.currentText()
        
        # 应用筛选
        self.table_model.set_filter(filter_text, filter_status, filter_data_type)
        
        # 更新筛选结果计数
        self.update_filter_count()
    
    def clear_filters(self):
        """清除所有筛选条件"""
        self.search_edit.clear()
        self.status_combo.setCurrentIndex(0)  # "全部"
        self.data_type_combo.setCurrentIndex(0)  # "全部"
        
        # 应用筛选（实际上是清除筛选）
        self.apply_filters()
    
    def update_filter_count(self):
        """更新筛选结果计数"""
        total_count = len(self.monitored_variables)
        filtered_count = len(self.table_model.filtered_variables)
        
        self.filter_count_label.setText(f"显示: {filtered_count}/{total_count}")
        
        # 如果有筛选，更新状态栏
        if filtered_count < total_count:
            self.status_label.setText(f"筛选显示 {filtered_count}/{total_count} 个变量")
        else:
            self.status_label.setText(f"监控 {total_count} 个变量")
    
    def update_data_type_filter_options(self):
        """更新数据类型筛选下拉框，只显示当前监控变量中存在的数据类型"""
        # 保存当前选择
        current_selection = self.data_type_combo.currentText()
        
        # 清空并添加"全部"选项
        self.data_type_combo.clear()
        self.data_type_combo.addItem("全部")
        
        # 收集所有不同的数据类型
        data_types = set()
        for variable in self.monitored_variables:
            if variable.data_type:
                data_types.add(variable.data_type)
        
        # 按字母顺序排序并添加到下拉框
        for data_type in sorted(data_types):
            self.data_type_combo.addItem(data_type)
        
        # 尝试恢复之前的选择
        index = self.data_type_combo.findText(current_selection)
        if index >= 0:
            self.data_type_combo.setCurrentIndex(index)
        else:
            self.data_type_combo.setCurrentIndex(0)  # 默认选择"全部"
    
    def go_back(self):
        """返回上一个视图，并恢复树形视图"""
        if self.main_window:
            # 停止自动刷新
            if self.auto_refresh.isChecked():
                self.auto_refresh.setChecked(False)
                
            # 返回到设备视图
            self.main_window.goto_devices() 