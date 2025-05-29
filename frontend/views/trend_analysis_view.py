#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
from datetime import datetime, timedelta
import random
import numpy as np
import pandas as pd
import pyqtgraph as pg
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QLabel, QComboBox, QLineEdit, QDateTimeEdit, 
    QPushButton, QTableView, QCheckBox, QFileDialog,
    QHeaderView, QSplitter, QMessageBox, QProgressBar,
    QToolButton, QColorDialog, QMenu, QAction, QListWidget,
    QListWidgetItem
)
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QDateTime, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QStandardItemModel, QStandardItem, QColor, QPen

from frontend.models.project_model import ProjectManager

logger = logging.getLogger(__name__)

class TrendAnalysisView(QWidget):
    """趋势分析视图，用于显示变量的趋势图表"""
    
    def __init__(self, project_manager, parent=None):
        super().__init__(parent)
        self.project_manager = project_manager
        self.main_window = parent
        self.selected_variables = []
        self.trend_data = {}  # 存储趋势数据，格式为 {variable_id: [(timestamp, value), ...], ...}
        self.variable_colors = {}  # 存储变量对应的曲线颜色
        self.init_ui()
        
        # 设置默认颜色列表
        self.default_colors = [
            (31, 119, 180),  # 蓝色
            (255, 127, 14),  # 橙色
            (44, 160, 44),   # 绿色
            (214, 39, 40),   # 红色
            (148, 103, 189), # 紫色
            (140, 86, 75),   # 棕色
            (227, 119, 194), # 粉色
            (127, 127, 127), # 灰色
            (188, 189, 34),  # 黄绿色
            (23, 190, 207)   # 青色
        ]
    
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
        title_label = QLabel("趋势分析")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(title_label)
        
        # 刷新按钮
        self.refresh_btn = QPushButton("刷新视图")
        self.refresh_btn.clicked.connect(self.refresh_variable_display)
        self.refresh_btn.setMaximumWidth(100)
        top_layout.addWidget(self.refresh_btn)
        
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
        
        # 分析参数
        params_layout = QHBoxLayout()
        
        # 采样间隔
        self.sampling_combo = QComboBox()
        self.sampling_combo.addItems(["原始数据", "1分钟", "5分钟", "15分钟", "1小时", "1天"])
        params_layout.addWidget(QLabel("采样间隔:"))
        params_layout.addWidget(self.sampling_combo)
        
        # 显示类型
        self.display_type_combo = QComboBox()
        self.display_type_combo.addItems(["折线图", "散点图", "柱状图", "面积图"])
        params_layout.addWidget(QLabel("显示类型:"))
        params_layout.addWidget(self.display_type_combo)
        
        # 趋势分析类型
        self.analysis_type_combo = QComboBox()
        self.analysis_type_combo.addItems(["原始数据", "平均值", "最大值", "最小值", "标准差"])
        params_layout.addWidget(QLabel("分析类型:"))
        params_layout.addWidget(self.analysis_type_combo)
        
        filter_layout.addLayout(params_layout)
        
        # 查询按钮
        button_layout = QHBoxLayout()
        
        self.query_btn = QPushButton("查询并生成趋势图")
        self.query_btn.clicked.connect(self.query_trend_data)
        button_layout.addWidget(self.query_btn)
        
        self.export_btn = QPushButton("导出图表")
        self.export_btn.clicked.connect(self.export_chart)
        self.export_btn.setEnabled(False)
        button_layout.addWidget(self.export_btn)
        
        self.clear_btn = QPushButton("清空结果")
        self.clear_btn.clicked.connect(self.clear_results)
        button_layout.addWidget(self.clear_btn)
        
        filter_layout.addLayout(button_layout)
        
        filter_panel.setLayout(filter_layout)
        layout.addWidget(filter_panel)
        
        # 创建分割器，左侧是变量列表，右侧是趋势图
        splitter = QSplitter(Qt.Horizontal)
        
        # 变量列表面板
        variables_panel = QGroupBox("变量列表")
        variables_layout = QVBoxLayout()
        
        # 添加一个变量计数标签
        self.variable_count_label = QLabel("总变量: 0")
        variables_layout.addWidget(self.variable_count_label)
        
        # 变量表格
        self.variable_model = QStandardItemModel()
        self.variable_model.setHorizontalHeaderLabels(["选择", "变量名", "设备", "数据类型", "地址"])
        
        self.variable_proxy_model = QSortFilterProxyModel()
        self.variable_proxy_model.setSourceModel(self.variable_model)
        self.variable_proxy_model.setFilterKeyColumn(1)  # 按变量名筛选
        
        self.variable_table = QTableView()
        self.variable_table.setModel(self.variable_proxy_model)
        
        # 设置列宽
        self.variable_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 选择列
        self.variable_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # 变量名列
        self.variable_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)  # 设备列
        self.variable_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 数据类型列
        self.variable_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)  # 地址列
        
        self.variable_table.setSelectionBehavior(QTableView.SelectRows)
        self.variable_table.setEditTriggers(QTableView.NoEditTriggers)
        self.variable_table.clicked.connect(self.on_variable_clicked)
        
        # 设置表格样式
        self.variable_table.setAlternatingRowColors(True)
        self.variable_table.verticalHeader().setVisible(False)  # 隐藏行号
        
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
        
        # 变量颜色设置面板
        color_panel = QGroupBox("变量颜色设置")
        color_layout = QVBoxLayout()
        
        self.selected_variable_list = QListWidget()
        self.selected_variable_list.itemClicked.connect(self.on_variable_list_clicked)
        color_layout.addWidget(self.selected_variable_list)
        
        color_panel.setLayout(color_layout)
        
        # 组合变量选择和颜色设置
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.addWidget(variables_panel)
        left_layout.addWidget(color_panel)
        left_panel.setLayout(left_layout)
        
        # 趋势图面板
        trend_panel = QGroupBox("趋势图")
        trend_layout = QVBoxLayout()
        
        # 创建PyQtGraph绘图区域
        pg.setConfigOptions(antialias=True)  # 开启抗锯齿
        
        # 创建绘图区域
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')  # 设置背景为白色
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel('left', 'Value')
        self.plot_widget.setLabel('bottom', 'Time')
        self.plot_widget.addLegend()
        
        # 添加图例
        self.legend = self.plot_widget.addLegend()
        
        trend_layout.addWidget(self.plot_widget)
        
        # 图表控制面板
        controls_layout = QHBoxLayout()
        
        # 缩放按钮
        self.zoom_in_btn = QPushButton("放大")
        self.zoom_in_btn.clicked.connect(lambda: self.zoom_plot(factor=0.5))
        controls_layout.addWidget(self.zoom_in_btn)
        
        self.zoom_out_btn = QPushButton("缩小")
        self.zoom_out_btn.clicked.connect(lambda: self.zoom_plot(factor=2.0))
        controls_layout.addWidget(self.zoom_out_btn)
        
        self.fit_view_btn = QPushButton("适应视图")
        self.fit_view_btn.clicked.connect(self.fit_view)
        controls_layout.addWidget(self.fit_view_btn)
        
        # 图表样式按钮
        self.line_style_btn = QPushButton("折线图")
        self.line_style_btn.clicked.connect(lambda: self.set_plot_style("折线图"))
        controls_layout.addWidget(self.line_style_btn)
        
        self.scatter_style_btn = QPushButton("散点图")
        self.scatter_style_btn.clicked.connect(lambda: self.set_plot_style("散点图"))
        controls_layout.addWidget(self.scatter_style_btn)
        
        trend_layout.addLayout(controls_layout)
        
        trend_panel.setLayout(trend_layout)
        
        # 将变量选择和趋势图添加到分割器
        splitter.addWidget(left_panel)
        splitter.addWidget(trend_panel)
        
        # 设置分割器初始大小比例
        splitter.setSizes([300, 700])
        
        layout.addWidget(splitter)
        
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
        
        logger.info(f"项目选择变化: 索引={index}, 文本={self.project_combo.currentText()}")
        
        project = self.project_combo.itemData(index)
        if not project:
            self.device_combo.clear()
            self.device_combo.setEnabled(False)
            self.clear_variable_table()
            return
        
        # 更新设备下拉框
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
    
    def update_variable_list(self):
        """更新变量列表"""
        # 清空当前表格
        self.clear_variable_table()
        
        # 获取当前项目
        project_index = self.project_combo.currentIndex()
        if project_index < 0:
            logger.warning("无法更新变量列表：未选择项目")
            return
        
        project = self.project_combo.itemData(project_index)
        if not project:
            logger.warning("无法更新变量列表：项目数据为空")
            return
        
        # 获取当前设备
        device_index = self.device_combo.currentIndex()
        if device_index < 0:
            logger.warning("无法更新变量列表：未选择设备")
            return
        
        device = self.device_combo.itemData(device_index)
        
        # 记录加载的变量数
        total_variables = 0
        
        try:
            if device:  # 选择了特定设备
                logger.info(f"正在加载设备 '{device.name}' 的变量")
                
                # 确保设备有变量列表
                if hasattr(device, 'variables') and device.variables:
                    for variable in device.variables:
                        self.add_variable_to_table(variable, device.name)
                        total_variables += 1
                else:
                    logger.warning(f"设备 '{device.name}' 没有变量或变量列表为空")
            else:  # "所有设备"选项
                logger.info(f"正在加载项目 '{project.name}' 的所有变量")
                
                # 遍历项目中的所有设备
                for dev in project.devices:
                    if hasattr(dev, 'variables') and dev.variables:
                        for variable in dev.variables:
                            self.add_variable_to_table(variable, dev.name)
                            total_variables += 1
            
            # 更新变量计数
            self.variable_count_label.setText(f"总变量: {total_variables}")
            
            # 更新数据类型筛选下拉框
            self.update_data_type_filter()
            
            # 强制更新表格视图
            self.variable_table.resizeColumnsToContents()
            self.variable_table.reset()
            self.variable_table.update()
            
            logger.info(f"变量列表更新完成，共加载 {total_variables} 个变量")
            
        except Exception as e:
            logger.error(f"更新变量列表时出错: {str(e)}")
            
        # 如果没有加载到任何变量，尝试添加测试数据
        if total_variables == 0:
            logger.info("未加载到变量，将添加测试数据")
            self.add_test_data_to_table()
    
    def add_variable_to_table(self, variable, device_name):
        """添加变量到表格中
        
        Args:
            variable: 变量对象
            device_name: 设备名称
        """
        try:
            # 创建复选框项
            checkbox_item = QStandardItem()
            checkbox_item.setCheckable(True)
            checkbox_item.setCheckState(Qt.Unchecked)
            checkbox_item.setData(variable.variable_id, Qt.UserRole)
            
            # 创建其他列
            name_item = QStandardItem(variable.name)
            device_item = QStandardItem(device_name)
            data_type_item = QStandardItem(variable.data_type)
            address_item = QStandardItem(variable.address)
            
            # 将项添加到模型
            row = self.variable_model.rowCount()
            self.variable_model.setItem(row, 0, checkbox_item)
            self.variable_model.setItem(row, 1, name_item)
            self.variable_model.setItem(row, 2, device_item)
            self.variable_model.setItem(row, 3, data_type_item)
            self.variable_model.setItem(row, 4, address_item)
        except Exception as e:
            logger.error(f"添加变量到表格时出错: {str(e)}")
    
    def clear_variable_table(self):
        """清空变量表格"""
        self.variable_model.removeRows(0, self.variable_model.rowCount())
        self.selected_variable_list.clear()
        self.selected_variables = []
        self.update_selected_count()
        
        # 重置变量颜色映射
        self.variable_colors = {}
    
    def update_data_type_filter(self):
        """更新数据类型筛选下拉框"""
        # 保存当前选择
        current_selection = self.data_type_combo.currentText()
        
        # 清空并添加"全部类型"选项
        self.data_type_combo.clear()
        self.data_type_combo.addItem("全部类型")
        
        # 收集所有不同的数据类型
        data_types = set()
        for row in range(self.variable_model.rowCount()):
            data_type = self.variable_model.item(row, 3).text()
            data_types.add(data_type)
        
        # 按字母顺序排序并添加到下拉框
        for data_type in sorted(data_types):
            self.data_type_combo.addItem(data_type)
        
        # 尝试恢复之前的选择
        index = self.data_type_combo.findText(current_selection)
        if index >= 0:
            self.data_type_combo.setCurrentIndex(index)
    
    def filter_variables(self):
        """根据搜索文本和数据类型筛选变量"""
        filter_text = self.variable_search.text().lower()
        filter_type = self.data_type_combo.currentText()
        
        # 只有当筛选类型不是"全部类型"时才按类型筛选
        if filter_type != "全部类型":
            # 先恢复所有行的可见性
            self.variable_proxy_model.setFilterFixedString("")
            
            # 然后手动隐藏不符合条件的行
            for row in range(self.variable_model.rowCount()):
                item_type = self.variable_model.item(row, 3).text()
                item_name = self.variable_model.item(row, 1).text().lower()
                
                # 同时匹配类型和名称
                visible = (item_type == filter_type) and (filter_text in item_name)
                
                # 获取代理模型中的行索引
                source_index = self.variable_model.index(row, 0)
                proxy_index = self.variable_proxy_model.mapFromSource(source_index)
                
                if proxy_index.isValid():
                    self.variable_table.setRowHidden(proxy_index.row(), not visible)
        else:
            # 只按名称筛选
            self.variable_proxy_model.setFilterFixedString(filter_text)
            
            # 确保所有行在类型筛选被清除后可见
            for row in range(self.variable_table.model().rowCount()):
                self.variable_table.setRowHidden(row, False)
    
    def on_variable_clicked(self, index):
        """处理变量点击事件"""
        try:
            # 获取源模型索引
            source_index = self.variable_proxy_model.mapToSource(index)
            
            # 如果点击的是复选框列
            if index.column() == 0:
                item = self.variable_model.item(source_index.row(), 0)
                
                # 切换复选框状态
                if item.checkState() == Qt.Checked:
                    item.setCheckState(Qt.Unchecked)
                else:
                    item.setCheckState(Qt.Checked)
                
                # 更新选中的变量
                self.update_selected_variables()
            else:
                # 如果点击的是其他列，也选中对应行的复选框
                item = self.variable_model.item(source_index.row(), 0)
                if item.checkState() == Qt.Checked:
                    item.setCheckState(Qt.Unchecked)
                else:
                    item.setCheckState(Qt.Checked)
                
                # 更新选中的变量
                self.update_selected_variables()
        except Exception as e:
            logger.error(f"处理变量点击时出错: {str(e)}")
    
    def on_variable_list_clicked(self, item):
        """处理已选变量列表中的点击事件"""
        # 弹出颜色对话框，让用户选择变量曲线的颜色
        variable_id = item.data(Qt.UserRole)
        if variable_id in self.variable_colors:
            current_color = self.variable_colors[variable_id]
            color = QColorDialog.getColor(QColor(*current_color), self, "选择变量曲线颜色")
            
            if color.isValid():
                # 更新颜色
                self.variable_colors[variable_id] = (color.red(), color.green(), color.blue())
                
                # 更新列表项的颜色指示器
                item.setBackground(color)
                
                # 如果已经有图表，更新曲线颜色
                self.update_plot_colors()
    
    def update_selected_variables(self):
        """更新选中的变量列表"""
        self.selected_variables = []
        self.selected_variable_list.clear()
        
        # 遍历所有变量项
        for row in range(self.variable_model.rowCount()):
            item = self.variable_model.item(row, 0)
            if item.checkState() == Qt.Checked:
                variable_id = item.data(Qt.UserRole)
                variable_name = self.variable_model.item(row, 1).text()
                device_name = self.variable_model.item(row, 2).text()
                
                # 收集选中的变量
                self.selected_variables.append({
                    'id': variable_id,
                    'name': variable_name,
                    'device': device_name,
                    'data_type': self.variable_model.item(row, 3).text(),
                    'address': self.variable_model.item(row, 4).text()
                })
                
                # 添加到变量列表
                list_item = QListWidgetItem(f"{variable_name} ({device_name})")
                list_item.setData(Qt.UserRole, variable_id)
                
                # 设置颜色
                if variable_id not in self.variable_colors:
                    # 分配一个默认颜色
                    color_index = len(self.variable_colors) % len(self.default_colors)
                    self.variable_colors[variable_id] = self.default_colors[color_index]
                
                color = QColor(*self.variable_colors[variable_id])
                list_item.setBackground(color)
                
                self.selected_variable_list.addItem(list_item)
        
        self.update_selected_count()
    
    def update_selected_count(self):
        """更新已选择的变量计数"""
        count = len(self.selected_variables)
        self.selected_count_label.setText(f"已选择: {count} 个变量")
        
        # 如果已选变量大于0，启用查询按钮
        self.query_btn.setEnabled(count > 0)
    
    def select_all_variables(self):
        """选择所有可见变量"""
        visible_rows = []
        
        # 收集所有可见行的源模型索引
        for proxy_row in range(self.variable_proxy_model.rowCount()):
            proxy_index = self.variable_proxy_model.index(proxy_row, 0)
            if not self.variable_table.isRowHidden(proxy_row):
                source_index = self.variable_proxy_model.mapToSource(proxy_index)
                visible_rows.append(source_index.row())
        
        # 勾选所有可见行
        for row in visible_rows:
            item = self.variable_model.item(row, 0)
            item.setCheckState(Qt.Checked)
        
        # 更新选中的变量
        self.update_selected_variables()
    
    def deselect_all_variables(self):
        """取消选择所有变量"""
        # 清除所有复选框
        for row in range(self.variable_model.rowCount()):
            item = self.variable_model.item(row, 0)
            item.setCheckState(Qt.Unchecked)
        
        # 更新选中的变量
        self.update_selected_variables()
    
    def apply_time_preset(self, preset):
        """应用时间预设"""
        if preset == "自定义":
            # 不做任何改变，让用户手动设置时间
            return
        
        now = QDateTime.currentDateTime()
        
        if preset == "最近1小时":
            start_time = now.addSecs(-3600)  # 减去1小时
        elif preset == "最近24小时":
            start_time = now.addDays(-1)
        elif preset == "最近7天":
            start_time = now.addDays(-7)
        elif preset == "最近30天":
            start_time = now.addDays(-30)
        else:
            return
        
        self.start_time.setDateTime(start_time)
        self.end_time.setDateTime(now)
    
    def go_back(self):
        """返回上一个视图，并恢复树形视图"""
        if self.main_window:
            # 清空结果以释放资源
            self.clear_results()
            
            # 确保树形视图可见
            if hasattr(self.main_window, 'hierarchy_tree') and not self.main_window.hierarchy_tree.isVisible():
                self.main_window.hierarchy_tree.setVisible(True)
                self.main_window.main_splitter.setSizes([300, 900])
            
            # 返回设备视图
            self.main_window.goto_devices()
    
    def zoom_plot(self, factor):
        """缩放图表"""
        if not hasattr(self, 'current_view_rect'):
            self.current_view_rect = self.plot_widget.viewRect()
        
        # 获取当前视图的中心点
        center_x = self.current_view_rect.center().x()
        center_y = self.current_view_rect.center().y()
        
        # 计算新的宽度和高度
        new_width = self.current_view_rect.width() * factor
        new_height = self.current_view_rect.height() * factor
        
        # 设置新的视图矩形
        new_rect = pg.QtCore.QRectF(
            center_x - new_width / 2,
            center_y - new_height / 2,
            new_width,
            new_height
        )
        
        self.current_view_rect = new_rect
        self.plot_widget.setRange(rect=new_rect, padding=0)
    
    def fit_view(self):
        """适应视图"""
        self.plot_widget.autoRange()
        self.current_view_rect = self.plot_widget.viewRect()
    
    def set_plot_style(self, style):
        """设置图表样式"""
        if not self.trend_data:
            QMessageBox.information(self, "提示", "请先查询数据")
            return
        
        self.update_plot(style=style)
    
    def update_plot_colors(self):
        """更新图表颜色"""
        if not self.trend_data:
            return
        
        self.update_plot(self.display_type_combo.currentText())
    
    def query_trend_data(self):
        """查询趋势数据并生成趋势图"""
        if not self.selected_variables:
            QMessageBox.warning(self, "警告", "请至少选择一个变量")
            return
        
        # 获取时间范围
        start_time = self.start_time.dateTime().toPyDateTime()
        end_time = self.end_time.dateTime().toPyDateTime()
        
        if start_time >= end_time:
            QMessageBox.warning(self, "警告", "开始时间必须早于结束时间")
            return
        
        # 清空现有数据
        self.trend_data = {}
        
        # 显示进度条
        progress = QProgressBar(self)
        progress.setWindowTitle("数据查询")
        progress.setRange(0, len(self.selected_variables))
        progress.setValue(0)
        progress.setGeometry(200, 200, 300, 20)
        progress.show()
        
        # 在实际项目中，这里应该从数据库查询历史数据
        # 本示例使用模拟数据进行演示
        for i, variable in enumerate(self.selected_variables):
            # 更新进度条
            progress.setValue(i + 1)
            self.generate_sample_data(variable, start_time, end_time)
        
        # 关闭进度条
        progress.close()
        
        # 生成趋势图
        self.update_plot()
        
        # 启用导出按钮
        self.export_btn.setEnabled(True)
    
    def generate_sample_data(self, variable, start_time, end_time):
        """生成样本数据
        
        Args:
            variable: 变量信息字典
            start_time: 开始时间
            end_time: 结束时间
        """
        # 根据采样间隔设置不同的点数
        sampling_text = self.sampling_combo.currentText()
        
        if sampling_text == "原始数据":
            # 原始数据，生成较多的点
            points = 500
        elif sampling_text == "1分钟":
            points = int((end_time - start_time).total_seconds() / 60)
        elif sampling_text == "5分钟":
            points = int((end_time - start_time).total_seconds() / 300)
        elif sampling_text == "15分钟":
            points = int((end_time - start_time).total_seconds() / 900)
        elif sampling_text == "1小时":
            points = int((end_time - start_time).total_seconds() / 3600)
        elif sampling_text == "1天":
            points = int((end_time - start_time).total_seconds() / 86400)
        else:
            points = 100
        
        # 至少生成10个点
        points = max(10, points)
        
        # 生成时间戳
        timestamps = [start_time + timedelta(seconds=(end_time - start_time).total_seconds() * i / (points - 1)) for i in range(points)]
        
        # 生成适合不同变量类型的数据
        data_type = variable['data_type']
        values = []
        
        if data_type == "BOOL":
            # 布尔值只有 0 和 1
            for _ in range(points):
                values.append(1 if random.random() > 0.5 else 0)
        elif data_type in ["INT", "DINT", "WORD", "DWORD"]:
            # 整数类型，生成在适当范围内的值
            # 为了使趋势更有意义，生成带有一些周期性和趋势性的数据
            base_value = random.randint(50, 200)
            amplitude = random.randint(10, 50)
            trend = random.uniform(-0.5, 0.5)  # 趋势斜率
            
            for i in range(points):
                t = i / points
                # 组合周期分量和趋势分量
                value = base_value + amplitude * np.sin(t * 8 * np.pi) + trend * i
                values.append(int(value))
        elif data_type in ["REAL", "FLOAT"]:
            # 浮点数类型，可以生成更平滑的曲线
            base_value = random.uniform(50, 200)
            amplitude = random.uniform(10, 50)
            trend = random.uniform(-0.5, 0.5)  # 趋势斜率
            
            for i in range(points):
                t = i / points
                # 组合多个周期分量和噪声
                value = base_value + amplitude * np.sin(t * 8 * np.pi) + trend * i + random.uniform(-5, 5)
                values.append(round(value, 2))
        else:
            # 对于其他类型，生成0-100之间的随机值
            for _ in range(points):
                values.append(random.uniform(0, 100))
        
        # 将数据转换为numpy数组，并进行适当的处理
        analysis_type = self.analysis_type_combo.currentText()
        
        if analysis_type == "平均值":
            # 计算移动平均
            window_size = min(5, len(values))
            values = np.convolve(values, np.ones(window_size)/window_size, mode='valid')
            # 调整时间戳以匹配处理后的数据长度
            timestamps = timestamps[window_size-1:]
        elif analysis_type == "最大值":
            # 计算移动最大值
            window_size = min(5, len(values))
            max_values = []
            for i in range(len(values) - window_size + 1):
                max_values.append(max(values[i:i+window_size]))
            values = max_values
            timestamps = timestamps[window_size-1:]
        elif analysis_type == "最小值":
            # 计算移动最小值
            window_size = min(5, len(values))
            min_values = []
            for i in range(len(values) - window_size + 1):
                min_values.append(min(values[i:i+window_size]))
            values = min_values
            timestamps = timestamps[window_size-1:]
        elif analysis_type == "标准差":
            # 计算移动标准差
            window_size = min(5, len(values))
            std_values = []
            for i in range(len(values) - window_size + 1):
                std_values.append(np.std(values[i:i+window_size]))
            values = std_values
            timestamps = timestamps[window_size-1:]
        
        # 存储趋势数据
        self.trend_data[variable['id']] = {
            'name': variable['name'],
            'device': variable['device'],
            'timestamps': timestamps,
            'values': values,
            'data_type': data_type
        }
    
    def update_plot(self, style=None):
        """更新趋势图
        
        Args:
            style: 图表样式，如果为None则使用下拉框中的选择
        """
        if not self.trend_data:
            return
        
        # 清空图表
        self.plot_widget.clear()
        
        # 确定使用的样式
        if style is None:
            style = self.display_type_combo.currentText()
        
        # 转换时间戳为可绘制的格式
        for variable_id, data in self.trend_data.items():
            timestamps = data['timestamps']
            values = data['values']
            name = f"{data['name']} ({data['device']})"
            
            # 将时间戳转换为相对于第一个时间点的秒数
            if timestamps:
                base_time = timestamps[0]
                x_values = [(t - base_time).total_seconds() for t in timestamps]
                
                # 获取变量的颜色
                if variable_id in self.variable_colors:
                    color = self.variable_colors[variable_id]
                else:
                    # 分配一个默认颜色
                    color_index = len(self.variable_colors) % len(self.default_colors)
                    color = self.default_colors[color_index]
                    self.variable_colors[variable_id] = color
                
                pen = pg.mkPen(color=color, width=2)
                
                # 根据样式绘制不同类型的图表
                if style == "折线图":
                    self.plot_widget.plot(x_values, values, name=name, pen=pen)
                elif style == "散点图":
                    scatter = pg.ScatterPlotItem(x=x_values, y=values, pen=pen, brush=color, size=8, name=name)
                    self.plot_widget.addItem(scatter)
                elif style == "柱状图":
                    # 创建柱状图（使用BarGraphItem）
                    bar_width = (x_values[-1] - x_values[0]) / len(x_values) * 0.8
                    bars = pg.BarGraphItem(x=x_values, height=values, width=bar_width, brush=color, name=name)
                    self.plot_widget.addItem(bars)
                elif style == "面积图":
                    # 创建面积图（使用填充曲线）
                    curve = self.plot_widget.plot(x_values, values, name=name, pen=pen)
                    # 添加填充区域
                    fill = pg.FillBetweenItem(
                        curve1=curve,
                        curve2=pg.PlotCurveItem(x_values, [0] * len(x_values)),
                        brush=pg.mkBrush(color[0], color[1], color[2], 50)  # 半透明填充
                    )
                    self.plot_widget.addItem(fill)
        
        # 更新x轴标签格式
        x_axis = self.plot_widget.getAxis('bottom')
        x_axis.setLabel('Time (seconds)')
        
        # 启用鼠标交互
        self.plot_widget.setMouseEnabled(x=True, y=True)
        self.plot_widget.enableAutoRange()
        
        # 保存当前视图区域
        self.current_view_rect = self.plot_widget.viewRect()
    
    def export_chart(self):
        """导出图表为图片"""
        if not self.trend_data:
            QMessageBox.warning(self, "警告", "没有数据可导出")
            return
        
        # 弹出文件保存对话框
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出趋势图",
            f"trend_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
            "图片文件 (*.png);;所有文件 (*)"
        )
        
        if not file_path:
            return
        
        # 确保文件路径有正确的扩展名
        if not file_path.lower().endswith('.png'):
            file_path += '.png'
        
        try:
            # 导出为图片
            exporter = pg.exporters.ImageExporter(self.plot_widget.plotItem)
            exporter.export(file_path)
            
            QMessageBox.information(self, "导出成功", f"趋势图已成功导出到\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出图表时出错: {str(e)}")
    
    def clear_results(self):
        """清空结果"""
        # 清空趋势数据
        self.trend_data = {}
        
        # 清空图表
        self.plot_widget.clear()
        
        # 禁用导出按钮
        self.export_btn.setEnabled(False)
    
    def showEvent(self, event):
        """当视图显示时调用"""
        super().showEvent(event)
        
        # 加载项目列表
        self.load_projects()
        
        # 延迟刷新变量列表，确保界面完全加载
        QTimer.singleShot(500, self.refresh_variable_display)
    
    def add_test_data_to_table(self):
        """添加测试数据到表格，用于调试"""
        # 只有在表格为空时添加测试数据
        if self.variable_model.rowCount() > 0:
            return
            
        logger.info("添加测试数据到变量表格")
        
        # 测试数据
        test_variables = [
            {"id": "test1", "name": "温度传感器", "device": "测试设备1", "data_type": "REAL", "address": "DB1.0"},
            {"id": "test2", "name": "压力传感器", "device": "测试设备1", "data_type": "REAL", "address": "DB1.4"},
            {"id": "test3", "name": "流量计", "device": "测试设备2", "data_type": "REAL", "address": "DB2.0"},
            {"id": "test4", "name": "电机状态", "device": "测试设备2", "data_type": "BOOL", "address": "M0.0"},
            {"id": "test5", "name": "生产计数", "device": "测试设备3", "data_type": "INT", "address": "DB3.0"}
        ]
        
        # 添加到表格
        for var in test_variables:
            # 创建复选框项
            checkbox_item = QStandardItem()
            checkbox_item.setCheckable(True)
            checkbox_item.setCheckState(Qt.Unchecked)
            checkbox_item.setData(var["id"], Qt.UserRole)
            
            # 创建其他列
            name_item = QStandardItem(var["name"])
            device_item = QStandardItem(var["device"])
            data_type_item = QStandardItem(var["data_type"])
            address_item = QStandardItem(var["address"])
            
            # 将项添加到模型
            row = self.variable_model.rowCount()
            self.variable_model.setItem(row, 0, checkbox_item)
            self.variable_model.setItem(row, 1, name_item)
            self.variable_model.setItem(row, 2, device_item)
            self.variable_model.setItem(row, 3, data_type_item)
            self.variable_model.setItem(row, 4, address_item)
        
        # 更新变量计数
        self.variable_count_label.setText(f"总变量: {self.variable_model.rowCount()}")
        logger.info(f"已添加 {len(test_variables)} 个测试变量到表格")
        
    def refresh_variable_display(self):
        """强制刷新变量显示"""
        try:
            logger.info("正在强制刷新变量显示...")
            
            if self.project_combo.currentIndex() >= 0:
                # 先清除筛选条件
                self.variable_search.clear()
                self.data_type_combo.setCurrentIndex(0)
                
                # 更新变量列表
                self.update_variable_list()
                
                # 如果变量列表为空，添加测试数据
                if self.variable_model.rowCount() == 0:
                    self.add_test_data_to_table()
                
                # 更新数据类型筛选下拉框
                self.update_data_type_filter()
                
                # 调试输出
                self.debug_variable_display()
                
                # 显示提示消息
                if self.variable_model.rowCount() > 0:
                    logger.info("变量加载成功")
                else:
                    logger.warning("未加载到任何变量，请检查项目或设备是否包含变量")
            else:
                logger.warning("无法刷新变量：未选择项目")
        except Exception as e:
            logger.error(f"刷新变量显示时出错: {str(e)}")
            
    def debug_variable_display(self):
        """打印变量表状态，用于调试"""
        try:
            source_rows = self.variable_model.rowCount()
            proxy_rows = self.variable_proxy_model.rowCount()
            visible_rows = sum(1 for i in range(proxy_rows) if not self.variable_table.isRowHidden(i))
            
            logger.info(f"变量表调试信息:")
            logger.info(f"  源模型行数: {source_rows}")
            logger.info(f"  代理模型行数: {proxy_rows}")
            logger.info(f"  可见行数: {visible_rows}")
            logger.info(f"  当前项目: {self.project_combo.currentText()}")
            logger.info(f"  当前设备: {self.device_combo.currentText()}")
            
            # 检查表格大小
            table_width = self.variable_table.width()
            table_height = self.variable_table.height()
            logger.info(f"  表格尺寸: {table_width}x{table_height}")
            
            if proxy_rows > 0 and visible_rows == 0:
                # 尝试修复显示问题
                self.variable_table.reset()
                self.variable_table.update()
        except Exception as e:
            logger.error(f"调试变量表时出错: {str(e)}")
