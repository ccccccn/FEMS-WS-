#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置服务模块
作者: zhongqi.wang
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class ConfigService:
    """配置服务类，负责管理应用程序配置"""
    
    def __init__(self, config_dir="config"):
        """Initialize the configuration service.
        
        Args:
            config_dir (str): Configuration directory
        """
        self.config_dir = config_dir
        self.config = {}
        self.config_file = None
        
        # Load default configuration
        self.load_default_config()
    
    def load_default_config(self):
        """加载默认配置"""
        self.config = {
            "version": "1.0",
            "settings": {
                "theme": "dark",
                "language": "zh_CN",
                "update_rate": 1000,
                "logging_enabled": True,
                "logging_interval": 60000
            },
            "devices": [],
            "variables": [],
            "forwarding": []
        }
    
    def load_config(self, file_path: Optional[str] = None) -> bool:
        """
        从文件加载配置
        
        参数:
            file_path: 配置文件路径，如果为None则使用默认路径
            
        返回:
            bool: 加载是否成功
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                logger.warning(f"配置文件不存在: {file_path}")
                return False
            
            # 加载配置
            with open(file_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
                self.config_file = file_path
                logger.info(f"已加载配置文件: {file_path}")
                return True
                
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            return False
    
    def save_config(self, file_path: Optional[str] = None) -> bool:
        """
        保存配置到文件
        
        参数:
            file_path: 配置文件路径，如果为None则使用上次加载或保存的路径
            
        返回:
            bool: 保存是否成功
        """
        try:
            # 使用提供的文件路径或上次加载/保存的路径
            save_path = file_path or self.config_file
            
            # 如果未指定路径，使用默认路径
            if not save_path:
                save_path = os.path.join("config", "config.json")
            
            # 如果目录不存在则创建
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # 保存配置
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
                self.config_file = save_path
                logger.info(f"已保存配置到: {save_path}")
                return True
                
        except Exception as e:
            logger.error(f"保存配置失败: {str(e)}")
            return False
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        参数:
            key: 配置键，使用点号分隔层级，如'settings.theme'
            default: 如果键不存在时返回的默认值
            
        返回:
            Any: 配置值或默认值
        """
        try:
            # 将键拆分为各部分
            parts = key.split('.')
            value = self.config
            
            # 遍历配置层级
            for part in parts:
                value = value[part]
            return value
        except (KeyError, TypeError):
            return default
    
    def set_config(self, key: str, value: Any) -> bool:
        """
        设置配置值
        
        参数:
            key: 配置键，使用点号分隔层级，如'settings.theme'
            value: 要设置的值
            
        返回:
            bool: 设置是否成功
        """
        try:
            # 将键拆分为各部分
            parts = key.split('.')
            
            # 遍历配置层级
            config = self.config
            
            # 如果不存在则创建嵌套字典
            for i, part in enumerate(parts[:-1]):
                if part not in config:
                    config[part] = {}
                    
                # 移动到下一层
                config = config[part]
                
            # 设置值
            config[parts[-1]] = value
            return True
            
        except Exception as e:
            logger.error(f"设置配置失败: {str(e)}")
            return False
    
    def update_device(self, device_id: str, device_data: Dict[str, Any]) -> bool:
        """
        更新或添加设备配置
        
        参数:
            device_id: 设备ID
            device_data: 设备数据字典
            
        返回:
            bool: 更新是否成功
        """
        try:
            # 在设备列表中查找设备
            devices = self.config.get('devices', [])
            device_found = False
            
            # 获取设备列表
            if 'devices' not in self.config:
                self.config['devices'] = []
            
            # 检查设备是否已存在
            for i, device in enumerate(self.config['devices']):
                if device.get('device_id') == device_id:
                    # 更新现有设备
                    self.config['devices'][i] = device_data
                    device_found = True
                    break
            
            # 添加新设备
            if not device_found:
                self.config['devices'].append(device_data)
            
            return True
            
        except Exception as e:
            logger.error(f"更新设备配置失败: {str(e)}")
            return False
    
    def remove_device(self, device_id: str) -> bool:
        """
        删除设备配置
        
        参数:
            device_id: 设备ID
            
        返回:
            bool: 删除是否成功
        """
        try:
            # 获取设备列表
            if 'devices' not in self.config:
                return False
            
            # 查找并删除设备
            for i, device in enumerate(self.config['devices']):
                if device.get('device_id') == device_id:
                    del self.config['devices'][i]
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"删除设备配置失败: {str(e)}")
            return False
    
    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        获取设备配置
        
        参数:
            device_id: 设备ID
            
        返回:
            Optional[Dict[str, Any]]: 设备配置字典，如果不存在则返回None
        """
        try:
            for device in self.config.get('devices', []):
                if device.get('device_id') == device_id:
                    return device
            return None
            
        except Exception as e:
            logger.error(f"获取设备配置失败: {str(e)}")
            return None
    
    def get_devices(self) -> List[Dict[str, Any]]:
        """
        获取所有设备配置
        
        返回:
            List[Dict[str, Any]]: 设备配置列表
        """
        return self.config.get('devices', [])
    
    def update_variable(self, variable_id: str, variable_data: Dict[str, Any]) -> bool:
        """
        更新或添加变量配置
        
        参数:
            variable_id: 变量ID
            variable_data: 变量数据字典
            
        返回:
            bool: 更新是否成功
        """
        try:
            # 获取变量列表
            if 'variables' not in self.config:
                self.config['variables'] = []
            
            # 检查变量是否已存在
            for i, variable in enumerate(self.config['variables']):
                if variable.get('variable_id') == variable_id:
                    # 更新现有变量
                    self.config['variables'][i] = variable_data
                    return True
            
            # 添加新变量
            self.config['variables'].append(variable_data)
            return True
            
        except Exception as e:
            logger.error(f"更新变量配置失败: {str(e)}")
            return False
    
    def remove_variable(self, variable_id: str) -> bool:
        """
        删除变量配置
        
        参数:
            variable_id: 变量ID
            
        返回:
            bool: 删除是否成功
        """
        try:
            # 获取变量列表
            if 'variables' not in self.config:
                return False
            
            # 查找并删除变量
            for i, variable in enumerate(self.config['variables']):
                if variable.get('variable_id') == variable_id:
                    del self.config['variables'][i]
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"删除变量配置失败: {str(e)}")
            return False
    
    def get_variable(self, variable_id: str) -> Optional[Dict[str, Any]]:
        """
        获取变量配置
        
        参数:
            variable_id: 变量ID
            
        返回:
            Optional[Dict[str, Any]]: 变量配置字典，如果不存在则返回None
        """
        try:
            for variable in self.config.get('variables', []):
                if variable.get('variable_id') == variable_id:
                    return variable
            return None
            
        except Exception as e:
            logger.error(f"获取变量配置失败: {str(e)}")
            return None
    
    def get_variables(self) -> List[Dict[str, Any]]:
        """
        获取所有变量配置
        
        返回:
            List[Dict[str, Any]]: 变量配置列表
        """
        return self.config.get('variables', [])
    
    def update_variable_settings(self, variable_id: str, settings: Dict[str, Any]) -> bool:
        """
        更新变量设置
        
        参数:
            variable_id: 变量ID
            settings: 设置字典
            
        返回:
            bool: 更新是否成功
        """
        try:
            # 更新设置
            variables = self.config.get('variables', [])
            
            # 更新变量列表中的变量
            for variable in variables:
                if variable.get('variable_id') == variable_id:
                    variable.update(settings)
                    break
            
            # 保存更新后的变量
            self.config['variables'] = variables
            return True
            
        except Exception as e:
            logger.error(f"更新变量设置失败: {str(e)}")
            return False
    
    def get_variable_settings(self, variable_id: str) -> Optional[Dict[str, Any]]:
        """
        获取变量设置
        
        参数:
            variable_id: 变量ID
            
        返回:
            Optional[Dict[str, Any]]: 变量设置字典，如果不存在则返回None
        """
        try:
            for variable in self.config.get('variables', []):
                if variable.get('variable_id') == variable_id:
                    return variable
            return None
            
        except Exception as e:
            logger.error(f"获取变量设置失败: {str(e)}")
            return None

# 创建单例实例
config_service = ConfigService() 