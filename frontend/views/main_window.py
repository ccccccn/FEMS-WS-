#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os

import requests
from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QAction, QMessageBox,
    QFileDialog, QVBoxLayout, QWidget, QStyleFactory,
    QApplication, QStackedWidget, QSplitter, QLabel
)
from PyQt5.QtGui import QIcon, QPalette, QColor, QFont
from PyQt5.QtCore import Qt, QSize, QTimer

from frontend.models.project_model import ProjectManager
from frontend.views.project_view import ProjectView
from frontend.views.device_view import DeviceView
from frontend.views.variable_view import VariableView
from frontend.views.monitoring_view import MonitoringView
from frontend.views.history_view import HistoryView
from frontend.views.trend_analysis_view import TrendAnalysisView
from frontend.views.tree_view import HierarchyTree
from frontend.views.data_forwarding_view import DataForwardingView

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window with hierarchical interface for project, device, and variable management."""

    def __init__(self):
        super().__init__()

        # 初始化项目管理器
        self.project_manager = ProjectManager()
        self.project_manager.load_projects()

        self.apply_tech_theme()
        self.init_ui()

    def apply_tech_theme(self):
        """Apply a modern tech-inspired dark theme to the application."""
        # 设置应用程序样式为Fusion（现代外观）
        app_instance = QApplication.instance()
        if app_instance:
            app_instance.setStyle(QStyleFactory.create("Fusion"))

            # 创建暗色调技术感调色板
            dark_palette = QPalette()

            # 基础颜色
            dark_color = QColor(45, 45, 45)
            disabled_color = QColor(70, 70, 70)
            text_color = QColor(200, 200, 200)
            highlight_color = QColor(42, 130, 218)
            accent_color = QColor(0, 188, 212)  # 科技蓝

            # 设置调色板颜色
            dark_palette.setColor(QPalette.Window, dark_color)
            dark_palette.setColor(QPalette.WindowText, text_color)
            dark_palette.setColor(QPalette.Base, QColor(32, 32, 32))
            dark_palette.setColor(QPalette.AlternateBase, dark_color)
            dark_palette.setColor(QPalette.ToolTipBase, highlight_color)
            dark_palette.setColor(QPalette.ToolTipText, text_color)
            dark_palette.setColor(QPalette.Text, text_color)
            dark_palette.setColor(QPalette.Disabled, QPalette.Text, disabled_color)
            dark_palette.setColor(QPalette.Button, dark_color)
            dark_palette.setColor(QPalette.ButtonText, text_color)
            dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, disabled_color)
            dark_palette.setColor(QPalette.BrightText, Qt.red)
            dark_palette.setColor(QPalette.Link, accent_color)
            dark_palette.setColor(QPalette.Highlight, highlight_color)
            dark_palette.setColor(QPalette.HighlightedText, Qt.black)
            dark_palette.setColor(QPalette.Disabled, QPalette.HighlightedText, disabled_color)

            # 应用调色板
            app_instance.setPalette(dark_palette)

            # 设置科技感字体
            tech_font = QFont("Segoe UI", 9)
            app_instance.setFont(tech_font)

            # 设置样式表，添加更多科技感细节
            stylesheet = """
                QMainWindow {
                    border: none;
                }
                QTabWidget::pane {
                    border: 1px solid #333;
                    border-radius: 3px;
                    background-color: #2d2d2d;
                }
                QTabBar::tab {
                    background-color: #222;
                    color: #aaa;
                    padding: 8px 16px;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background-color: #2a82da;
                    color: white;
                }
                QPushButton {
                    background-color: #2a5a8a;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 6px 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #3a6a9a;
                }
                QPushButton:pressed {
                    background-color: #1a4a7a;
                }
                QPushButton:disabled {
                    background-color: #555;
                    color: #888;
                }
                QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                    background-color: #333;
                    color: #ddd;
                    border: 1px solid #555;
                    border-radius: 3px;
                    padding: 4px;
                }
                QTableView {
                    alternate-background-color: #353535;
                    background-color: #2d2d2d;
                    gridline-color: #444;
                    selection-background-color: #2a82da;
                    selection-color: white;
                }
                QHeaderView::section {
                    background-color: #222;
                    color: white;
                    padding: 5px;
                    border: 1px solid #444;
                }
                QStatusBar {
                    background-color: #1e1e1e;
                    color: #00bcd4;
                }
                QMenuBar {
                    background-color: #1e1e1e;
                    color: white;
                }
                QMenuBar::item:selected {
                    background-color: #2a82da;
                }
                QMenu {
                    background-color: #2d2d2d;
                    color: white;
                    border: 1px solid #555;
                }
                QMenu::item:selected {
                    background-color: #2a82da;
                }
                QGroupBox {
                    border: 1px solid #555;
                    border-radius: 3px;
                    margin-top: 10px;
                    font-weight: bold;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    padding: 0 5px;
                }
                QSplitter::handle {
                    background-color: #444;
                }
                QSplitter::handle:horizontal {
                    width: 2px;
                }
                QSplitter::handle:vertical {
                    height: 2px;
                }
                QListWidget {
                    background-color: #2d2d2d;
                    alternate-background-color: #353535;
                    color: white;
                    border: 1px solid #555;
                    border-radius: 3px;
                }
                QListWidget::item:selected {
                    background-color: #2a82da;
                }
                QCheckBox {
                    color: white;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                }
                QCheckBox::indicator:unchecked {
                    background-color: #333;
                    border: 1px solid #555;
                    border-radius: 2px;
                }
                QCheckBox::indicator:checked {
                    background-color: #2a82da;
                    border: 1px solid #555;
                    border-radius: 2px;
                }
            """
            app_instance.setStyleSheet(stylesheet)

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("数据采集系统")
        self.setMinimumSize(1200, 800)

        # 创建主分割器，用于树形视图和内容区域
        self.main_splitter = QSplitter(Qt.Horizontal)

        # 创建树形视图，用于层次导航
        self.hierarchy_tree = HierarchyTree(self.project_manager, self)
        self.hierarchy_tree.project_selected.connect(self.on_tree_project_selected)
        self.hierarchy_tree.device_selected.connect(self.on_tree_device_selected)
        self.hierarchy_tree.variable_selected.connect(self.on_tree_variable_selected)

        # 创建堆叠窗口，用于不同视图
        self.stacked_widget = QStackedWidget()

        # 创建项目视图
        self.project_view = ProjectView(self.project_manager, self)
        # 连接项目视图信号
        self.project_view.project_selected.connect(self.on_project_selected)

        # 创建设备视图
        self.device_view = DeviceView(self.project_manager, self)
        # 连接设备视图信号
        self.device_view.device_selected.connect(self.on_device_selected)

        # 创建变量视图
        self.variable_view = VariableView(self.project_manager, self)

        # 创建监控视图
        self.monitoring_view = MonitoringView(self.project_manager, self)

        # 创建数据转发视图
        self.data_forwarding_view = DataForwardingView(self.project_manager, self)

        # 创建历史数据视图
        self.history_view = HistoryView(self.project_manager, self)

        # 创建趋势分析视图
        self.trend_analysis_view = TrendAnalysisView(self.project_manager, self)

        # 添加视图到堆叠窗口
        self.stacked_widget.addWidget(self.project_view)  # 索引 0
        self.stacked_widget.addWidget(self.device_view)  # 索引 1
        self.stacked_widget.addWidget(self.variable_view)  # 索引 2
        self.stacked_widget.addWidget(self.monitoring_view)  # 索引 3
        self.stacked_widget.addWidget(self.data_forwarding_view)  # 索引 4
        self.stacked_widget.addWidget(self.history_view)  # 索引 5
        self.stacked_widget.addWidget(self.trend_analysis_view)  # 索引 6

        # 显式设置主窗口引用
        if hasattr(self.hierarchy_tree, 'set_main_window'):
            self.hierarchy_tree.set_main_window(self)

        if hasattr(self.project_view, 'set_main_window'):
            self.project_view.set_main_window(self)

        if hasattr(self.device_view, 'set_main_window'):
            self.device_view.set_main_window(self)

        if hasattr(self.variable_view, 'set_main_window'):
            self.variable_view.set_main_window(self)

        if hasattr(self.monitoring_view, 'set_main_window'):
            self.monitoring_view.set_main_window(self)

        if hasattr(self.history_view, 'set_main_window'):
            self.history_view.set_main_window(self)

        if hasattr(self.trend_analysis_view, 'set_main_window'):
            self.trend_analysis_view.set_main_window(self)

        # 将树形视图和堆叠窗口添加到主分割器
        self.main_splitter.addWidget(self.hierarchy_tree)
        self.main_splitter.addWidget(self.stacked_widget)

        # 设置分割器初始大小比例
        self.main_splitter.setSizes([300, 900])

        # 设置主窗口的中央部件
        self.setCentralWidget(self.main_splitter)

        # 创建菜单栏和工具栏
        self.create_menu_bar()
        self.create_tool_bar()

        # 创建状态栏
        self.statusBar().showMessage("就绪")

        # 刷新树形视图
        self.hierarchy_tree.refresh_tree()

        # 使用延时自动展开树节点
        QTimer.singleShot(500, self.expand_tree_nodes)

        # 记录初始化完成
        logger.info("主窗口初始化完成，已设置所有视图的main_window引用")

    def expand_tree_nodes(self):
        """自动展开树节点，使用户可以直接看到所有项目和设备。"""
        try:
            # 如果项目数量较少，直接全部展开
            if len(self.project_manager.projects) <= 3:
                self.hierarchy_tree.tree.expandAll()
                logger.info("已自动展开所有树节点")
            else:
                # 如果项目较多，只展开项目节点
                for i in range(self.hierarchy_tree.tree.topLevelItemCount()):
                    project_item = self.hierarchy_tree.tree.topLevelItem(i)
                    self.hierarchy_tree.tree.expandItem(project_item)

                    # 如果该项目只有一个设备，也展开它
                    if project_item.childCount() == 1:
                        self.hierarchy_tree.tree.expandItem(project_item.child(0))

                logger.info("已自动展开项目节点")
        except Exception as e:
            logger.error(f"自动展开树节点时出错: {str(e)}")

    def create_menu_bar(self):
        """Create the main menu bar."""
        menubar = self.menuBar()

        # 图标目录
        icons_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resources", "icons")

        # 项目菜单
        project_menu = menubar.addMenu("项目")

        new_project_action = QAction(
            QIcon(os.path.join(icons_dir, "new.png") if os.path.exists(os.path.join(icons_dir, "new.png")) else ""),
            "新建项目", self)
        new_project_action.setShortcut("Ctrl+N")
        new_project_action.triggered.connect(self.new_project)
        project_menu.addAction(new_project_action)

        project_menu.addSeparator()

        goto_projects_action = QAction("项目管理", self)
        goto_projects_action.triggered.connect(self.goto_projects)
        project_menu.addAction(goto_projects_action)

        # 添加设备和变量管理到项目菜单
        project_menu.addSeparator()

        manage_devices_action = QAction("设备管理", self)
        manage_devices_action.triggered.connect(self.goto_devices)
        project_menu.addAction(manage_devices_action)

        manage_variables_action = QAction("变量管理", self)
        manage_variables_action.triggered.connect(self.goto_variables)
        project_menu.addAction(manage_variables_action)

        # 监控菜单
        monitoring_menu = menubar.addMenu("监控")

        start_monitoring_action = QAction(
            QIcon(os.path.join(icons_dir, "start.png") if os.path.exists(os.path.join(icons_dir, "start.png")) else ""),
            "启动监控", self)
        start_monitoring_action.triggered.connect(self.start_monitoring)
        monitoring_menu.addAction(start_monitoring_action)

        goto_monitoring_action = QAction("实时数据", self)
        goto_monitoring_action.triggered.connect(self.goto_monitoring)
        monitoring_menu.addAction(goto_monitoring_action)

        # 数据转发菜单项（从监控菜单移到菜单栏）
        data_forwarding_action = QAction('数据转发', self)
        data_forwarding_action.triggered.connect(self.goto_data_forwarding)
        menubar.addAction(data_forwarding_action)

        # 历史数据菜单
        history_menu = menubar.addMenu("历史数据")

        history_view_action = QAction(QIcon(
            os.path.join(icons_dir, "history.png") if os.path.exists(os.path.join(icons_dir, "history.png")) else ""),
            "历史查询", self)
        history_view_action.setToolTip("查询历史数据（支持变量筛选和时间筛选）")
        history_view_action.triggered.connect(self.goto_history)
        history_menu.addAction(history_view_action)

        history_menu.addSeparator()

        export_data_action = QAction("数据导出", self)
        export_data_action.setToolTip("导出历史数据为CSV或Excel格式")
        export_data_action.triggered.connect(self.export_history_data)
        history_menu.addAction(export_data_action)

        export_chart_action = QAction("曲线导出", self)
        export_chart_action.setToolTip("导出趋势曲线为图片格式")
        export_chart_action.triggered.connect(self.export_history_chart)
        history_menu.addAction(export_chart_action)

        # 趋势分析菜单 - 添加到菜单栏
        trend_menu = menubar.addMenu("趋势分析")

        trend_view_action = QAction("趋势分析", self)
        trend_view_action.setToolTip("显示历史数据趋势曲线")
        trend_view_action.triggered.connect(self.goto_trend_analysis)
        trend_menu.addAction(trend_view_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助")

        about_action = QAction(
            QIcon(os.path.join(icons_dir, "about.png") if os.path.exists(os.path.join(icons_dir, "about.png")) else ""),
            "关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_tool_bar(self):
        """Create the main toolbar."""
        # Add an empty toolbar to maintain the UI structure
        toolbar = self.addToolBar("主工具栏")
        toolbar.setMovable(False)
        # Hide the empty toolbar
        toolbar.setVisible(False)

    # Tree view event handlers
    def on_tree_project_selected(self, project):
        """Handle project selection from tree."""
        self.project_manager.current_project = project
        self.goto_projects()
        self.project_view.select_project(project)
        self.statusBar().showMessage(f"已选择项目: {project.name}")

    def on_tree_device_selected(self, device, project):
        """Handle device selection from tree."""
        self.project_manager.current_project = project
        self.goto_devices()
        self.device_view.select_device(device)
        self.statusBar().showMessage(f"已选择设备: {device.name}")

    def on_tree_variable_selected(self, variable, device, project):
        """处理从树形视图中选择变量。"""
        if not variable or not device or not project:
            logger.warning("无效的变量选择：变量、设备或项目对象为空")
            return

        try:
            # 设置当前项目
            self.project_manager.current_project = project

            # 切换到变量视图
            self.goto_variables()

            # 更新变量视图的设备
            self.variable_view.update_device(device)

            # 在变量视图中选择变量
            selected = self.variable_view.select_variable(variable)
            if not selected:
                logger.warning(f"无法在变量视图中选择变量: {variable.name}")
                # 尝试强制刷新变量表格后再次选择
                self.variable_view.variable_model.set_variables(device.variables)
                QTimer.singleShot(100, lambda: self.variable_view.select_variable(variable))

            # 更新状态栏
            self.statusBar().showMessage(f"已选择变量: {variable.name}")
        except Exception as e:
            logger.error(f"处理变量选择时发生错误: {str(e)}")
            QMessageBox.critical(self, "错误", f"处理变量选择时发生错误: {str(e)}")

    # 导航方法
    def goto_projects(self):
        """Switch to project view."""
        self.restore_tree_view()
        self.stacked_widget.setCurrentIndex(0)
        self.statusBar().showMessage("项目管理")

    def goto_devices(self):
        """Switch to device view."""
        self.restore_tree_view()
        if not self.project_manager.current_project:
            logger.warning("goto_devices: 当前项目未选择")
            QMessageBox.warning(self, "警告", "请先选择一个项目")
            self.goto_projects()
            return

        logger.info(f"goto_devices: 切换到项目 '{self.project_manager.current_project.name}' 的设备视图")
        # 直接设置当前索引
        self.stacked_widget.setCurrentIndex(1)

        # 更新设备视图的项目
        self.device_view.update_project(self.project_manager.current_project)

        # 更新状态栏
        self.statusBar().showMessage(f"设备管理 - 项目: {self.project_manager.current_project.name}")

    def goto_variables(self):
        """Switch to variable view."""
        self.restore_tree_view()
        if not self.project_manager.current_project:
            QMessageBox.warning(self, "警告", "请先选择一个项目")
            self.goto_projects()
            return

        # Find first device in current project
        if self.project_manager.current_project.devices:
            self.stacked_widget.setCurrentIndex(2)
            first_device = self.project_manager.current_project.devices[0]
            self.variable_view.update_device(first_device)
            self.statusBar().showMessage(f"变量管理 - 设备: {first_device.name}")
        else:
            QMessageBox.warning(self, "警告", "当前项目没有设备，请先添加设备")
            self.goto_devices()

    def goto_monitoring(self):
        """Switch to monitoring view."""
        if not self.project_manager.current_project:
            QMessageBox.warning(self, "警告", "请先选择一个项目")
            self.goto_projects()
            return

        # 隐藏树形视图，使监控视图占满整个窗口
        self.hierarchy_tree.setVisible(False)

        self.stacked_widget.setCurrentIndex(3)

        # 更新监控视图的项目列表
        self.monitoring_view.load_projects()

        # 如果有当前项目，自动选择它
        if self.project_manager.current_project:
            for i in range(self.monitoring_view.project_combo.count()):
                project = self.monitoring_view.project_combo.itemData(i)
                if project and project.project_id == self.project_manager.current_project.project_id:
                    self.monitoring_view.project_combo.setCurrentIndex(i)
                    break

        self.statusBar().showMessage(f"实时数据监控 - 项目: {self.project_manager.current_project.name}")

    def goto_history(self):
        """切换到历史数据视图"""
        if not self.project_manager.current_project:
            QMessageBox.warning(self, "警告", "请先选择一个项目")
            self.goto_projects()
            return

        # 隐藏树形视图，使历史数据视图占满整个窗口
        self.hierarchy_tree.setVisible(False)

        self.stacked_widget.setCurrentIndex(5)  # 历史数据视图的索引

        # 更新历史数据视图的项目列表
        if hasattr(self.history_view, 'load_projects'):
            self.history_view.load_projects()

            # 如果有当前项目，自动选择它
            if self.project_manager.current_project:
                for i in range(self.history_view.project_combo.count()):
                    project = self.history_view.project_combo.itemData(i)
                    if project and project.project_id == self.project_manager.current_project.project_id:
                        self.history_view.project_combo.setCurrentIndex(i)
                        break

        self.statusBar().showMessage(f"历史数据查询 - 项目: {self.project_manager.current_project.name}")

    def goto_trend_analysis(self):
        """切换到趋势分析视图"""
        if not self.project_manager.current_project:
            QMessageBox.warning(self, "警告", "请先选择一个项目")
            self.goto_projects()
            return

        # 隐藏树形视图，使趋势分析视图占满整个窗口
        self.hierarchy_tree.setVisible(False)

        self.stacked_widget.setCurrentIndex(6)  # 趋势分析视图的索引

        # 更新趋势分析视图的项目列表
        if hasattr(self.trend_analysis_view, 'load_projects'):
            self.trend_analysis_view.load_projects()

            # 如果有当前项目，自动选择它
            if self.project_manager.current_project:
                for i in range(self.trend_analysis_view.project_combo.count()):
                    project = self.trend_analysis_view.project_combo.itemData(i)
                    if project and project.project_id == self.project_manager.current_project.project_id:
                        self.trend_analysis_view.project_combo.setCurrentIndex(i)
                        break

        self.statusBar().showMessage(f"趋势分析 - 项目: {self.project_manager.current_project.name}")

    def export_history_data(self):
        """导出历史数据"""
        if not self.project_manager.current_project:
            QMessageBox.warning(self, "警告", "请先选择一个项目")
            self.goto_projects()
            return

        # 切换到历史数据视图
        self.goto_history()

        # 调用历史数据视图的导出功能
        if hasattr(self.history_view, 'export_data'):
            # 如果有数据可导出，直接调用导出功能
            if hasattr(self.history_view, 'history_data') and self.history_view.history_data:
                self.history_view.export_data()
            else:
                # 否则提示用户需要先查询数据
                QMessageBox.information(self, "导出历史数据", "请先查询历史数据，然后再导出")
        else:
            QMessageBox.information(self, "导出历史数据", "历史数据导出功能开发中...")

    def export_history_chart(self):
        """导出历史数据曲线"""
        if not self.project_manager.current_project:
            QMessageBox.warning(self, "警告", "请先选择一个项目")
            self.goto_projects()
            return

        # 切换到趋势分析视图
        self.goto_trend_analysis()

        # 如果已有趋势数据，则导出图表
        if hasattr(self.trend_analysis_view, 'trend_data') and self.trend_analysis_view.trend_data:
            self.trend_analysis_view.export_chart()
        else:
            # 提示用户需要先查询数据
            QMessageBox.information(self, "导出趋势曲线", "请先查询趋势数据，然后再导出图表")

    def create_placeholder_view(self, title):
        """创建占位视图，用于尚未实现的功能
        
        Args:
            title (str): 视图标题
            
        Returns:
            QWidget: 占位视图
        """
        view = QWidget()
        layout = QVBoxLayout()

        # 标题
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # 创建功能描述
        description = ""
        if "历史数据" in title:
            description = """
            <p>历史数据查询功能将支持：</p>
            <ul>
                <li>按变量名、设备名和数据类型筛选</li>
                <li>设置时间范围（开始时间和结束时间）</li>
                <li>查看历史数据表格</li>
                <li>导出数据为CSV或Excel格式</li>
            </ul>
            """
        elif "趋势分析" in title:
            description = """
            <p>趋势分析功能将支持：</p>
            <ul>
                <li>选择多个变量进行对比</li>
                <li>设置时间范围和采样间隔</li>
                <li>显示趋势曲线图</li>
                <li>导出曲线为图片格式</li>
                <li>缩放和平移曲线</li>
            </ul>
            """

        if description:
            desc_label = QLabel(description)
            desc_label.setAlignment(Qt.AlignLeft)
            desc_label.setStyleSheet("font-size: 11pt; color: #aaa; margin: 20px;")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

        # 开发中提示
        info_label = QLabel("该功能正在开发中...")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("font-size: 12pt; color: #888; margin-top: 30px;")
        layout.addWidget(info_label)

        view.setLayout(layout)
        return view

    # 事件处理方法
    def on_project_selected(self, project):
        """Handle project selection."""
        if project:
            self.project_manager.current_project = project
            self.hierarchy_tree.select_project(project)
            self.statusBar().showMessage(f"已选择项目: {project.name}")
        else:
            self.project_manager.current_project = None
            self.refresh_tree_view()
            self.statusBar().showMessage("未选择项目")

    def on_device_selected(self, device):
        """Handle device selection."""
        if device:
            self.hierarchy_tree.select_device(device, self.project_manager.current_project)
            self.statusBar().showMessage(f"已选择设备: {device.name}")
        else:
            self.refresh_tree_view()
            self.statusBar().showMessage(f"项目: {self.project_manager.current_project.name}")

    # 操作方法
    def new_project(self):
        """Create a new project - redirects to project view."""
        self.goto_projects()
        result = self.project_view.show_add_project_dialog()
        # 强制刷新树形视图
        if result:
            self.refresh_tree_view()

    def add_device(self):
        """Add a device to the current project."""
        if not self.project_manager.current_project:
            QMessageBox.warning(self, "警告", "请先选择一个项目")
            self.goto_projects()
            return

        self.goto_devices()
        result = self.device_view.show_add_device_dialog()
        # 强制刷新树形视图
        if result:
            self.refresh_tree_view()

    def add_device_to_project(self):
        """Add a device to the current project (called from project view)."""
        if not self.project_manager.current_project:
            QMessageBox.warning(self, "警告", "请先选择一个项目")
            return

        # 输出调试信息
        logger.info(f"添加设备到项目: {self.project_manager.current_project.name}")

        try:
            # 确保已选中项目
            project = self.project_manager.current_project

            # 切换到设备视图
            self.stacked_widget.setCurrentIndex(1)  # 直接通过索引切换，避免使用goto_devices

            # 强制刷新设备视图的当前项目
            self.device_view.update_project(project)

            # 显示添加设备对话框
            result = self.device_view.show_add_device_dialog()

            # 强制刷新树形视图
            if result:
                self.refresh_tree_view()
        except Exception as e:
            logger.error(f"添加设备时发生错误: {str(e)}")
            QMessageBox.critical(self, "错误", f"添加设备时发生错误: {str(e)}")

    def refresh_tree_view(self, selected_item=None):
        """Refresh the tree view.
        
        Args:
            selected_item (Device or Variable, optional): Item to select after refresh
        """
        # 保存当前选中的项
        current_device = self.hierarchy_tree.current_device
        current_variable = self.hierarchy_tree.current_variable

        # 刷新树形视图
        self.hierarchy_tree.refresh_tree()

        # 如果提供了要选择的项，选择它
        if selected_item:
            if hasattr(selected_item, 'variables'):  # 是设备
                self.hierarchy_tree.select_device(selected_item)
            else:  # 是变量
                if current_device:
                    self.hierarchy_tree.select_device(current_device)
                    self.hierarchy_tree.select_variable(selected_item)
        # 否则尝试选择之前选中的项
        elif current_device:
            self.hierarchy_tree.select_device(current_device)
            if current_variable:
                self.hierarchy_tree.select_variable(current_variable)

    def add_variable(self):
        """Add a variable to the selected device."""
        if not self.project_manager.current_project:
            QMessageBox.warning(self, "警告", "请先选择一个项目")
            self.goto_projects()
            return

        if not self.project_manager.current_project.devices:
            QMessageBox.warning(self, "警告", "当前项目没有设备，请先添加设备")
            self.goto_devices()
            return

        self.goto_variables()
        result = self.variable_view.show_add_variable_dialog()
        # 强制刷新树形视图
        if result:
            self.refresh_tree_view()

    def add_variable_to_device(self, device):
        """Add a variable to the specified device (called from device view)."""
        try:
            if not device:
                logger.warning("add_variable_to_device: 设备为空")
                return False

            # 确保当前项目已设置
            if not self.project_manager.current_project:
                for project in self.project_manager.projects:
                    for dev in project.devices:
                        if dev.device_id == device.device_id:
                            self.project_manager.current_project = project
                            logger.info(f"已找到设备所属项目: {project.name}")
                            break
                    if self.project_manager.current_project:
                        break

            # 仍然没有找到项目，则无法继续
            if not self.project_manager.current_project:
                logger.error("无法确定设备所属项目")
                QMessageBox.warning(self, "警告", "无法确定设备所属项目，请先选择一个项目")
                return False

            # Switch to variable view
            self.stacked_widget.setCurrentIndex(2)

            # Update variable view with the selected device
            self.variable_view.update_device(device)

            # Show add variable dialog and get result
            result = self.variable_view.show_add_variable_dialog()

            # Refresh tree view if variable was added successfully
            if result:
                # 确保树形视图知道当前项目和设备
                self.hierarchy_tree.current_project = self.project_manager.current_project
                self.hierarchy_tree.current_device = device

                # 使用延时确保数据已完全更新
                logger.info("添加变量成功，准备刷新树形视图")
                QTimer.singleShot(100, lambda: self.hierarchy_tree.refresh_tree())

                # Update status bar
                self.statusBar().showMessage(f"已添加变量到设备: {device.name}")

                # 记录日志
                logger.info(f"已成功添加变量到设备: {device.name}")

            # Return operation result
            return result
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.error(f"添加变量过程中发生异常: {str(e)}")
            QMessageBox.critical(self, "错误", f"添加变量过程中发生异常: {str(e)}")
            return False

    def start_monitoring(self):
        """Start monitoring data from devices."""
        if not self.project_manager.current_project:
            QMessageBox.warning(self, "警告", "请先选择一个项目")
            self.goto_projects()
            return

        if not self.project_manager.current_project.devices:
            QMessageBox.warning(self, "警告", "当前项目没有设备，请先添加设备")
            self.goto_devices()
            return

        # Check if any device has variables
        has_variables = False
        for device in self.project_manager.current_project.devices:
            if device.variables:
                has_variables = True
                break

        if not has_variables:
            QMessageBox.warning(self, "警告", "没有可监控的变量，请先添加变量")
            self.goto_variables()
            return

        # 切换到监控视图
        self.goto_monitoring()

        url = "http://192.168.97.125:10002/start_monitor/"
        payload = {
            "device_type": device.device_type,
            "ip": device.ip_address,
            "port": device.port
        }
        headers = {
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(url=url, timeout=5)
            data = response.json()
            if data.get("status") == "success":
                logger.info("成功获取数据，并执行监控")
            else:
                import json
                print(f'ip{payload.get("ip")}连接失败,原因：{json.loads(response.text).get("message")}')
                QMessageBox.information(self, '提示',
                                        f'ip{payload.get("ip")}连接失败,原因：{json.loads(response.text).get("message")}')
                return
        except Exception as e:
            logger.error(msg=f'{payload.get("ip")}连接失败：{e}')


        # 启用自动刷新
        self.monitoring_view.auto_refresh.setChecked(True)

        # 更新状态栏
        self.statusBar().showMessage("监控已启动")

    # Context menu methods from tree view
    def rename_project(self):
        """Rename the selected project."""
        if self.hierarchy_tree.current_project:
            self.goto_projects()
            self.project_view.rename_project(self.hierarchy_tree.current_project)

    def delete_project(self):
        """Delete the selected project."""
        if self.hierarchy_tree.current_project:
            self.goto_projects()
            result = self.project_view.delete_project()
            if result:
                self.refresh_tree_view()

    def edit_device(self):
        """Edit the selected device."""
        if self.hierarchy_tree.current_device:
            self.goto_devices()
            self.device_view.edit_device(self.hierarchy_tree.current_device)

    def delete_device(self):
        """Delete the selected device."""
        if self.hierarchy_tree.current_device:
            self.goto_devices()
            result = self.device_view.delete_device()
            if result:
                self.refresh_tree_view()

    def edit_variable(self):
        """Edit the selected variable."""
        if not self.hierarchy_tree.current_variable or not self.hierarchy_tree.current_device:
            logger.warning("编辑变量失败：未选择变量或设备")
            return

        # 获取当前变量对象的副本，避免直接传递引用
        variable_to_edit = self.hierarchy_tree.current_variable
        device = self.hierarchy_tree.current_device
        project = self.hierarchy_tree.current_project

        if not variable_to_edit or not device or not project:
            logger.warning("编辑变量失败：变量、设备或项目对象为空")
            return

        # 切换到变量视图
        self.goto_variables()

        # 确保变量视图已经更新了当前设备
        self.variable_view.update_device(device)

        # 在变量表中选中当前变量
        selected = self.variable_view.select_variable(variable_to_edit)
        if not selected:
            logger.warning(f"无法在表格中选中变量: {variable_to_edit.name}")

        # 直接调用变量视图的编辑方法
        try:
            # 直接调用编辑方法，显式传递变量对象
            result = self.variable_view.edit_variable(variable_to_edit)

            # 如果编辑成功，刷新树形视图
            if result:
                self.refresh_tree_view()
                logger.info(f"变量 '{variable_to_edit.name}' 编辑成功")
        except Exception as e:
            logger.error(f"编辑变量时发生错误: {str(e)}")
            QMessageBox.critical(self, "错误", f"编辑变量时发生错误: {str(e)}")

    def delete_variable(self):
        """Delete the selected variable."""
        if not self.hierarchy_tree.current_variable or not self.hierarchy_tree.current_device:
            logger.warning("删除变量失败：未选择变量或设备")
            return

        # 获取当前变量对象的副本，避免直接传递引用
        variable_to_delete = self.hierarchy_tree.current_variable
        device = self.hierarchy_tree.current_device
        project = self.hierarchy_tree.current_project

        if not variable_to_delete or not device or not project:
            logger.warning("删除变量失败：变量、设备或项目对象为空")
            return

        # 切换到变量视图
        self.goto_variables()

        # 确保变量视图已经更新了当前设备
        self.variable_view.update_device(device)

        # 在变量表中选中当前变量
        selected = self.variable_view.select_variable(variable_to_delete)
        if not selected:
            logger.warning(f"无法在表格中选中变量: {variable_to_delete.name}")

        # 直接调用变量视图的删除方法
        try:
            # 直接调用删除方法，显式传递变量对象
            result = self.variable_view.delete_variable(variable_to_delete)

            # 如果删除成功，刷新树形视图
            if result:
                # 清除当前变量引用
                self.hierarchy_tree.current_variable = None
                self.refresh_tree_view()
                logger.info(f"变量 '{variable_to_delete.name}' 删除成功")
        except Exception as e:
            logger.error(f"删除变量时发生错误: {str(e)}")
            QMessageBox.critical(self, "错误", f"删除变量时发生错误: {str(e)}")

    def show_about(self):
        QMessageBox.about(
            self,
            "关于数据采集系统",
            "<h2 style='color:#00bcd4;'>数据采集系统 v1.0</h2>"
            "<p>支持多种工业协议的现代数据采集软件</p>"
            "<p>支持协议：S7、Modbus、CAN、GOOSE</p>"
            "<p>支持分层管理：项目 → 设备 → 变量</p>"
            "<p>© 2023 数据采集系统</p>"
        )

    def closeEvent(self, event):
        """Handle window close event."""
        reply = QMessageBox.question(
            self,
            '确认退出',
            "确定要退出程序吗?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Save all projects before exiting
            for project in self.project_manager.projects:
                self.project_manager.save_project(project)
            event.accept()
        else:
            event.ignore()

    def restore_tree_view(self):
        """恢复树形视图的显示"""
        if not self.hierarchy_tree.isVisible():
            self.hierarchy_tree.setVisible(True)
            # 重新设置分割器的大小比例
            self.main_splitter.setSizes([300, 900])

    def goto_data_forwarding(self):
        """Switch to data forwarding view."""
        if not self.project_manager.current_project:
            QMessageBox.warning(self, "警告", "请先选择一个项目")
            self.goto_projects()
            return

        # 隐藏树形视图，使数据转发视图占满整个窗口
        self.hierarchy_tree.setVisible(False)

        # 切换到数据转发视图
        self.stacked_widget.setCurrentIndex(4)

        # 更新状态栏
        self.statusBar().showMessage(f"数据转发配置 - 项目: {self.project_manager.current_project.name}")
