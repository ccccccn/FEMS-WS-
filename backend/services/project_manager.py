#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
项目管理器模块
作者: zhongqi.wang
"""

import os
import json
import logging
from typing import List, Dict, Optional, Any
from uuid import uuid4

logger = logging.getLogger(__name__)

class Project:
    """项目类，表示一个数据采集项目"""
    
    def __init__(self, name: str, description: str = "", project_id: str = None):
        """
        初始化项目
        
        参数:
            name: 项目名称
            description: 项目描述
            project_id: 项目ID（如果不提供则自动生成）
        """
        self.project_id = project_id or str(uuid4())
        self.name = name
        self.description = description
        self.devices = []  # 设备列表
        self.created_at = None  # 创建时间
        self.updated_at = None  # 更新时间
    
    def get_device(self, device_id: str):
        """
        根据设备ID获取设备
        
        参数:
            device_id: 设备ID
            
        返回:
            Device: 如果找到设备则返回设备对象，否则返回None
        """
        for device in self.devices:
            if device.device_id == device_id:
                return device
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """将项目转换为字典格式"""
        return {
            'project_id': self.project_id,
            'name': self.name,
            'description': self.description,
            'devices': [device.to_dict() for device in self.devices],
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """从字典创建项目实例"""
        project = cls(
            name=data['name'],
            description=data.get('description', ''),
            project_id=data['project_id']
        )
        project.created_at = data.get('created_at')
        project.updated_at = data.get('updated_at')
        
        # 加载设备
        from frontend.models.device_model import Device
        project.devices = [Device.from_dict(dev_data) for dev_data in data.get('devices', [])]
        
        return project

class ProjectManager:
    """项目管理器类，负责管理所有项目"""
    
    def __init__(self, projects_dir: str = "projects"):
        """
        初始化项目管理器
        
        参数:
            projects_dir: 项目文件存储目录
        """
        self.projects_dir = projects_dir
        self.projects: List[Project] = []
        self.current_project: Optional[Project] = None
        
        # 确保项目目录存在
        os.makedirs(projects_dir, exist_ok=True)
    
    def create_project(self, name: str, description: str = "") -> Project:
        """
        创建新项目
        
        参数:
            name: 项目名称
            description: 项目描述
            
        返回:
            Project: 新创建的项目
        """
        # 检查项目名是否已存在
        if any(p.name == name for p in self.projects):
            raise ValueError(f"项目名 '{name}' 已存在")
        
        # 创建新项目
        project = Project(name=name, description=description)
        self.projects.append(project)
        
        # 保存项目
        self.save_project(project)
        
        return project
    
    def load_projects(self) -> None:
        """加载所有项目"""
        try:
            # 清空当前项目列表
            self.projects.clear()
            
            # 遍历项目目录
            for filename in os.listdir(self.projects_dir):
                if filename.endswith('.json'):
                    project_path = os.path.join(self.projects_dir, filename)
                    try:
                        with open(project_path, 'r', encoding='utf-8') as f:
                            project_data = json.load(f)
                            project = Project.from_dict(project_data)
                            self.projects.append(project)
                    except Exception as e:
                        logger.error(f"加载项目文件 {filename} 失败: {str(e)}")
            
            logger.info(f"已加载 {len(self.projects)} 个项目")
            
        except Exception as e:
            logger.error(f"加载项目失败: {str(e)}")
    
    def save_project(self, project: Project) -> bool:
        """
        保存项目到文件
        
        参数:
            project: 要保存的项目
            
        返回:
            bool: 是否保存成功
        """
        try:
            # 生成文件名
            filename = f"{project.project_id}.json"
            filepath = os.path.join(self.projects_dir, filename)
            
            # 保存项目数据
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(project.to_dict(), f, ensure_ascii=False, indent=2)
            
            logger.info(f"项目 '{project.name}' 已保存")
            return True
            
        except Exception as e:
            logger.error(f"保存项目 '{project.name}' 失败: {str(e)}")
            return False
    
    def delete_project(self, project: Project) -> bool:
        """
        删除项目
        
        参数:
            project: 要删除的项目
            
        返回:
            bool: 是否删除成功
        """
        try:
            # 从列表中移除项目
            self.projects.remove(project)
            
            # 删除项目文件
            filename = f"{project.project_id}.json"
            filepath = os.path.join(self.projects_dir, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
            
            # 如果删除的是当前项目，清除当前项目引用
            if self.current_project and self.current_project.project_id == project.project_id:
                self.current_project = None
            
            logger.info(f"项目 '{project.name}' 已删除")
            return True
            
        except Exception as e:
            logger.error(f"删除项目 '{project.name}' 失败: {str(e)}")
            return False
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """
        根据ID获取项目
        
        参数:
            project_id: 项目ID
            
        返回:
            Optional[Project]: 找到的项目，如果不存在则返回None
        """
        for project in self.projects:
            if project.project_id == project_id:
                return project
        return None
    
    def get_project_by_name(self, name: str) -> Optional[Project]:
        """
        根据名称获取项目
        
        参数:
            name: 项目名称
            
        返回:
            Optional[Project]: 找到的项目，如果不存在则返回None
        """
        for project in self.projects:
            if project.name == name:
                return project
        return None
    
    def rename_project(self, project: Project, new_name: str) -> bool:
        """
        重命名项目
        
        参数:
            project: 要重命名的项目
            new_name: 新名称
            
        返回:
            bool: 是否重命名成功
        """
        # 检查新名称是否已存在
        if any(p.name == new_name and p.project_id != project.project_id for p in self.projects):
            raise ValueError(f"项目名 '{new_name}' 已存在")
        
        try:
            # 更新项目名称
            project.name = new_name
            
            # 保存更改
            self.save_project(project)
            
            logger.info(f"项目已重命名为 '{new_name}'")
            return True
            
        except Exception as e:
            logger.error(f"重命名项目失败: {str(e)}")
            return False
    
    def update_project(self, project: Project) -> bool:
        """
        更新项目信息
        
        参数:
            project: 要更新的项目
            
        返回:
            bool: 是否更新成功
        """
        try:
            # 查找并更新项目
            for i, p in enumerate(self.projects):
                if p.project_id == project.project_id:
                    self.projects[i] = project
                    break
            
            # 保存更改
            self.save_project(project)
            
            logger.info(f"项目 '{project.name}' 已更新")
            return True
            
        except Exception as e:
            logger.error(f"更新项目失败: {str(e)}")
            return False 