#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
import os

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QListWidget, QListWidgetItem, QDialog,
    QFormLayout, QLineEdit, QTextEdit, QDialogButtonBox,
    QMessageBox, QGroupBox, QSplitter, QAbstractItemView,
    QMenu, QAction, QInputDialog
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QFont

from frontend.models.project_model import Project

logger = logging.getLogger(__name__)

class AddProjectDialog(QDialog):
    """Dialog for adding a new project."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新建项目")
        self.setMinimumWidth(400)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the dialog UI."""
        layout = QVBoxLayout()
        
        # Create form layout for project properties
        form_layout = QFormLayout()
        
        # Project name
        self.name_edit = QLineEdit()
        form_layout.addRow("项目名称:", self.name_edit)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        form_layout.addRow("项目描述:", self.description_edit)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # Add layouts to main layout
        layout.addLayout(form_layout)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def get_project_data(self):
        """Get project data from the dialog."""
        return {
            "name": self.name_edit.text(),
            "description": self.description_edit.toPlainText()
        }

class ProjectView(QWidget):
    """Widget for managing projects."""
    
    project_selected = pyqtSignal(object)  # Emitted when a project is selected
    
    def __init__(self, project_manager, parent=None):
        super().__init__(parent)
        self.project_manager = project_manager
        self.main_window = parent  # Store reference to parent window
        self.init_ui()
        self.load_projects()
    
    def set_main_window(self, main_window):
        """Set the main window reference explicitly."""
        self.main_window = main_window
        logger.info("ProjectView: Main window reference set explicitly")
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("项目管理")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        
        # Project list section
        self.project_list = QListWidget()
        self.project_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.project_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.project_list.customContextMenuRequested.connect(self.show_context_menu)
        self.project_list.itemSelectionChanged.connect(self.on_project_selection_changed)
        
        # Project buttons
        btn_layout = QHBoxLayout()
        
        self.add_project_btn = QPushButton("新建项目")
        self.add_project_btn.clicked.connect(self.show_add_project_dialog)
        
        self.delete_project_btn = QPushButton("删除项目")
        self.delete_project_btn.clicked.connect(self.delete_project)
        self.delete_project_btn.setEnabled(False)
        
        btn_layout.addWidget(self.add_project_btn)
        btn_layout.addWidget(self.delete_project_btn)
        
        # Project details section
        self.project_details = QGroupBox("项目详情")
        details_layout = QVBoxLayout()
        
        self.project_name_label = QLabel("项目名称: ")
        self.project_description_label = QLabel("项目描述: ")
        self.project_created_label = QLabel("创建时间: ")
        self.project_updated_label = QLabel("更新时间: ")
        self.device_count_label = QLabel("设备数量: 0")
        
        details_layout.addWidget(self.project_name_label)
        details_layout.addWidget(self.project_description_label)
        details_layout.addWidget(self.project_created_label)
        details_layout.addWidget(self.project_updated_label)
        details_layout.addWidget(self.device_count_label)
        
        # Device buttons
        device_btn_layout = QHBoxLayout()
        
        self.add_device_btn = QPushButton("添加设备")
        self.add_device_btn.clicked.connect(self.add_device)
        self.add_device_btn.setEnabled(False)
        
        device_btn_layout.addWidget(self.add_device_btn)
        
        details_layout.addLayout(device_btn_layout)
        self.project_details.setLayout(details_layout)
        
        # Create splitter for project list and details
        splitter = QSplitter(Qt.Vertical)
        
        # Create containers for the list and details
        list_container = QWidget()
        list_layout = QVBoxLayout(list_container)
        list_layout.addWidget(self.project_list)
        list_layout.addLayout(btn_layout)
        
        # Add widgets to splitter
        splitter.addWidget(list_container)
        splitter.addWidget(self.project_details)
        
        # Set initial sizes
        splitter.setSizes([200, 200])
        
        # Add all widgets to main layout
        layout.addWidget(title_label)
        layout.addWidget(splitter)
        
        self.setLayout(layout)
    
    def load_projects(self):
        """Load projects into the list widget."""
        self.project_list.clear()
        
        for project in self.project_manager.projects:
            item = QListWidgetItem(project.name)
            item.setData(Qt.UserRole, project.project_id)
            self.project_list.addItem(item)
    
    def show_add_project_dialog(self):
        """Show dialog for adding a new project."""
        dialog = AddProjectDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_project_data()
            
            # Create new project
            project = self.project_manager.create_project(
                name=data["name"],
                description=data["description"]
            )
            
            # Save project
            self.project_manager.save_project(project)
            
            # Reload project list
            self.load_projects()
            
            # Select the new project
            for i in range(self.project_list.count()):
                item = self.project_list.item(i)
                if item.data(Qt.UserRole) == project.project_id:
                    self.project_list.setCurrentItem(item)
                    break
            
            # 刷新树形视图
            self.refresh_hierarchy_tree(project)
            
            # 返回操作成功
            return True
            
        # 返回操作取消
        return False
    
    def delete_project(self):
        """Delete the selected project."""
        selected_items = self.project_list.selectedItems()
        if not selected_items:
            return False
        
        # Get selected project
        item = selected_items[0]
        project_id = item.data(Qt.UserRole)
        project = self.project_manager.get_project(project_id)
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除项目 '{project.name}' 吗？此操作无法撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Delete project
            success = self.project_manager.delete_project(project_id)
            
            if success:
                self.remove_project_from_ip_mapper(project.name)
                # Reload project list
                self.load_projects()
                
                # Clear details
                self.update_project_details(None)
                
                # Disable delete button
                self.delete_project_btn.setEnabled(False)
                
                # Emit signal
                self.project_selected.emit(None)
                
                # 刷新树形视图
                self.refresh_hierarchy_tree(None)
                
                return True
        
        return False

    def remove_project_from_ip_mapper(self, project_name):
        mapper_path = r'E:\FEMS_Front\VYCON_IO\VYCON_IO\VYCON_IO\projects\ip_mapper.json'
        if not os.path.exists(mapper_path):
            return

        try:
            with open(mapper_path, 'r', encoding='utf-8') as f:
                ip_dict = json.load(f)

            if project_name in ip_dict.get('ip_mapper', {}):
                del ip_dict['ip_mapper'][project_name]

                with open(mapper_path, 'w', encoding='utf-8') as f:
                    json.dump(ip_dict, f, indent=4, ensure_ascii=False)
                logger.info(f"已从 ip_mapper.json 中移除项目: {project_name}")

        except Exception as e:
            logger.error(f"删除 ip_mapper 项目 {project_name} 失败: {str(e)}")

    def on_project_selection_changed(self):
        """Handle project selection change."""
        selected_items = self.project_list.selectedItems()
        
        if selected_items:
            # Get selected project
            item = selected_items[0]
            project_id = item.data(Qt.UserRole)
            project = self.project_manager.get_project(project_id)
            
            # Update project details
            self.update_project_details(project)
            
            # Enable buttons
            self.delete_project_btn.setEnabled(True)
            self.add_device_btn.setEnabled(True)
            
            # Set as current project
            self.project_manager.set_current_project(project_id)
            
            # Emit signal
            self.project_selected.emit(project)
        else:
            # Clear details
            self.update_project_details(None)
            
            # Disable buttons
            self.delete_project_btn.setEnabled(False)
            self.add_device_btn.setEnabled(False)
            
            # Emit signal
            self.project_selected.emit(None)
    
    def update_project_details(self, project):
        """Update the project details display."""
        if project:
            self.project_name_label.setText(f"项目名称: {project.name}")
            self.project_description_label.setText(f"项目描述: {project.description}")
            self.project_created_label.setText(f"创建时间: {project.created_at}")
            self.project_updated_label.setText(f"更新时间: {project.updated_at}")
            self.device_count_label.setText(f"设备数量: {len(project.devices)}")
        else:
            self.project_name_label.setText("项目名称: ")
            self.project_description_label.setText("项目描述: ")
            self.project_created_label.setText("创建时间: ")
            self.project_updated_label.setText("更新时间: ")
            self.device_count_label.setText("设备数量: 0")
    
    def show_context_menu(self, position):
        """Show context menu for project list."""
        selected_items = self.project_list.selectedItems()
        if not selected_items:
            return
        
        # Create context menu
        context_menu = QMenu()
        
        # Add actions
        add_device_action = QAction("添加设备", self)
        add_device_action.triggered.connect(self.add_device)
        
        rename_action = QAction("重命名项目", self)
        rename_action.triggered.connect(self.rename_project)
        
        delete_action = QAction("删除项目", self)
        delete_action.triggered.connect(self.delete_project)
        
        # Add actions to menu
        context_menu.addAction(add_device_action)
        context_menu.addSeparator()
        context_menu.addAction(rename_action)
        context_menu.addAction(delete_action)
        
        # Show context menu
        context_menu.exec_(self.project_list.mapToGlobal(position))
    
    def rename_project(self):
        """Rename the selected project."""
        selected_items = self.project_list.selectedItems()
        if not selected_items:
            return
        
        # Get selected project
        item = selected_items[0]
        project_id = item.data(Qt.UserRole)
        project = self.project_manager.get_project(project_id)
        
        # Show dialog
        dialog = AddProjectDialog(self)
        dialog.setWindowTitle("重命名项目")
        dialog.name_edit.setText(project.name)
        dialog.description_edit.setPlainText(project.description)
        
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_project_data()
            
            # Update project
            project.name = data["name"]
            project.description = data["description"]
            from datetime import datetime
            project.updated_at = datetime.now().isoformat()
            
            # Save project
            self.project_manager.save_project(project)
            
            # Update item text
            item.setText(project.name)
            
            # Update details
            self.update_project_details(project)
            
            # 刷新树形视图
            self.refresh_hierarchy_tree(project)
    
    def add_device(self):
        """Add a device to current project."""
        # 先检查是否有选中的项目
        selected_items = self.project_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择一个项目")
            return
            
        # 获取选中的项目并设置为当前项目
        item = selected_items[0]
        project_id = item.data(Qt.UserRole)
        project = self.project_manager.get_project(project_id)
        self.project_manager.set_current_project(project_id)
        
        # 输出调试信息
        logger.info(f"ProjectView.add_device: 准备添加设备到项目 {project.name}")
        
        # 尝试使用main_window属性
        if hasattr(self, 'main_window') and self.main_window is not None:
            logger.info("使用main_window属性跳转到设备管理页面")
            try:
                # 直接调用主窗口的方法
                self.main_window.add_device_to_project()
                return
            except Exception as e:
                logger.error(f"使用main_window调用add_device_to_project时发生错误: {str(e)}")
        
        # 尝试使用parent()方法获取父窗口
        parent = self.parent()
        logger.info(f"Parent exists: {parent is not None}")
        logger.info(f"Parent has add_device_to_project: {hasattr(parent, 'add_device_to_project') if parent else False}")
        
        # 调用父窗口的添加设备方法
        if parent and hasattr(parent, "add_device_to_project"):
            try:
                # 使用直接调用，不通过信号连接
                parent.add_device_to_project()
            except Exception as e:
                logger.error(f"调用add_device_to_project时发生错误: {str(e)}")
                self.direct_add_device_to_project()
        else:
            logger.warning("无法找到父窗口的添加设备方法，改用直接方法")
            self.direct_add_device_to_project()
    
    def direct_add_device_to_project(self):
        """当父窗口方法不可用时，直接跳转到设备管理添加设备"""
        from frontend.views.device_view import AddDeviceDialog
        
        # 确保已选择项目
        if not self.project_manager.current_project:
            QMessageBox.warning(self, "警告", "请先选择一个项目")
            return False
            
        # 创建添加设备对话框
        dialog = AddDeviceDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            device = dialog.get_device_data()
            
            # 添加设备到项目
            self.project_manager.current_project.add_device(device)
            
            # 保存项目
            self.project_manager.save_project(self.project_manager.current_project)
            
            # 刷新设备列表
            self.update_project_details(self.project_manager.current_project)
            
            # 发送项目选中信号以通知父窗口更新
            self.project_selected.emit(self.project_manager.current_project)
            
            # 刷新树形视图
            self.refresh_hierarchy_tree(self.project_manager.current_project)
            
            # 显示成功消息
            QMessageBox.information(self, "成功", f"已成功添加设备 '{device.name}'")
            
            # 尝试跳转到设备管理页面
            parent = self.parent()
            if parent and hasattr(parent, "stacked_widget") and hasattr(parent.stacked_widget, "setCurrentIndex"):
                try:
                    # 直接切换到设备视图（索引1）
                    parent.stacked_widget.setCurrentIndex(1)
                    # 更新设备视图
                    if hasattr(parent, "device_view") and hasattr(parent.device_view, "update_project"):
                        parent.device_view.update_project(self.project_manager.current_project)
                except Exception as e:
                    logger.error(f"跳转到设备管理页面时发生错误: {str(e)}")
            
            return True
        
        return False
    
    def refresh_hierarchy_tree(self, selected_project=None):
        """刷新主窗口中的树形视图"""
        # 优先使用明确设置的main_window引用
        if hasattr(self, 'main_window') and self.main_window is not None:
            if hasattr(self.main_window, 'hierarchy_tree'):
                logger.info("使用main_window引用刷新树形视图")
                # 强制刷新树形视图
                self.main_window.hierarchy_tree.refresh_tree()
                
                # 如果有项目，选中它
                if selected_project:
                    self.main_window.hierarchy_tree.select_project(selected_project)
            elif hasattr(self.main_window, 'refresh_tree_view'):
                logger.info("使用main_window.refresh_tree_view()刷新树形视图")
                self.main_window.refresh_tree_view()
            else:
                logger.warning("main_window没有hierarchy_tree或refresh_tree_view方法")
        else:
            # 回退到使用parent()
            parent = self.parent()
            if parent and hasattr(parent, "hierarchy_tree"):
                logger.info("使用parent引用刷新树形视图")
                parent.hierarchy_tree.refresh_tree()
                if selected_project:
                    parent.hierarchy_tree.select_project(selected_project)
            elif parent and hasattr(parent, "refresh_tree_view"):
                logger.info("使用parent.refresh_tree_view()刷新树形视图")
                parent.refresh_tree_view()
            else:
                logger.warning("无法找到树形视图引用，无法刷新树形视图")

    def select_project(self, project):
        """Select a project in the list."""
        if not project:
            return
            
        # Find and select the project in the list
        for i in range(self.project_list.count()):
            item = self.project_list.item(i)
            if item.data(Qt.UserRole) == project.project_id:
                self.project_list.setCurrentItem(item)
                # This will trigger on_project_selection_changed
                break
                
        # Update the project details
        self.update_project_details(project)

    def add_project(self):
        """Add a new project."""
        name, ok = QInputDialog.getText(self, "新建项目", "请输入项目名称:")
        if ok and name:
            # 检查项目名是否已存在
            if any(p.name == name for p in self.project_manager.projects):
                QMessageBox.warning(self, "警告", "项目名称已存在")
                return
                
            # 创建新项目
            project = Project(name=name)
            self.project_manager.add_project(project)
            
            # 更新列表
            self.update_project_list()
            
            # 通知主窗口刷新树形视图
            parent = self.parent()
            if parent and hasattr(parent, "hierarchy_tree"):
                parent.hierarchy_tree.refresh_tree() 