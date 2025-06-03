#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据获取器模块
作者: zhongqi.wang
"""

import logging
import json
import random
import time
from datetime import datetime
from threading import Thread, Event
import requests
from typing import Dict, Any, Optional
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

logger = logging.getLogger(__name__)

class DataFetcher(QObject):
    """
    数据获取器类
    负责从各种数据源获取数据并进行处理
    """
    
    # 信号定义
    data_updated = pyqtSignal(str, dict)  # 数据源ID, 数据
    error_occurred = pyqtSignal(str, str)  # 数据源ID, 错误信息
    connection_status_changed = pyqtSignal(str, bool)  # 数据源ID, 连接状态

    def __init__(self, parent=None):
        """初始化数据获取器"""
        super().__init__(parent)
        self.data_sources = {}  # 数据源配置字典
        self.active_sources = set()  # 活动数据源集合
        self.update_timers = {}  # 更新定时器字典
        self.last_values = {}  # 最后一次获取的值
        self.connection_status = {}  # 连接状态字典
        self.variables = {}  # Dictionary of variables by ID
        self.stop_event = Event()
        self.fetch_thread = None
        self.mock_mode = False  # Set to True to generate mock data instead of API calls
    
    def add_data_source(self, source_id: str, config: Dict[str, Any]) -> bool:
        """
        添加数据源
        
        参数:
            source_id: 数据源ID
            config: 数据源配置
            
        返回:
            bool: 是否添加成功
        """
        try:
            if source_id in self.data_sources:
                logger.warning(f"数据源 {source_id} 已存在，将被更新")
            
            # 验证配置
            self._validate_source_config(config)
            
            # 存储配置
            self.data_sources[source_id] = config
            self.connection_status[source_id] = False
            
            # 如果数据源处于活动状态，则启动数据获取
            if source_id in self.active_sources:
                self._start_fetching(source_id)
            
            logger.info(f"数据源 {source_id} 添加成功")
            return True
            
        except Exception as e:
            logger.error(f"添加数据源 {source_id} 失败: {str(e)}")
            return False

    def remove_data_source(self, source_id: str) -> bool:
        """
        移除数据源
        
        参数:
            source_id: 数据源ID
            
        返回:
            bool: 是否移除成功
        """
        try:
            if source_id not in self.data_sources:
                logger.warning(f"数据源 {source_id} 不存在")
                return False
            
            # 停止数据获取
            self._stop_fetching(source_id)
            
            # 移除配置和状态
            del self.data_sources[source_id]
            del self.connection_status[source_id]
            if source_id in self.last_values:
                del self.last_values[source_id]
            
            self.active_sources.discard(source_id)
            
            logger.info(f"数据源 {source_id} 移除成功")
            return True
            
        except Exception as e:
            logger.error(f"移除数据源 {source_id} 失败: {str(e)}")
            return False

    def start_source(self, source_id: str) -> bool:
        """
        启动数据源
        
        参数:
            source_id: 数据源ID
            
        返回:
            bool: 是否启动成功
        """
        try:
            if source_id not in self.data_sources:
                logger.error(f"数据源 {source_id} 不存在")
                return False
            
            if source_id in self.active_sources:
                logger.warning(f"数据源 {source_id} 已经处于活动状态")
                return True
            
            self.active_sources.add(source_id)
            self._start_fetching(source_id)
            
            logger.info(f"数据源 {source_id} 启动成功")
            return True
            
        except Exception as e:
            logger.error(f"启动数据源 {source_id} 失败: {str(e)}")
            return False

    def stop_source(self, source_id: str) -> bool:
        """
        停止数据源
        
        参数:
            source_id: 数据源ID
            
        返回:
            bool: 是否停止成功
        """
        try:
            if source_id not in self.data_sources:
                logger.error(f"数据源 {source_id} 不存在")
                return False
            
            if source_id not in self.active_sources:
                logger.warning(f"数据源 {source_id} 已经处于停止状态")
                return True
            
            self._stop_fetching(source_id)
            self.active_sources.discard(source_id)
            
            logger.info(f"数据源 {source_id} 停止成功")
            return True
            
        except Exception as e:
            logger.error(f"停止数据源 {source_id} 失败: {str(e)}")
            return False

    def get_last_value(self, source_id: str) -> Optional[Dict[str, Any]]:
        """
        获取数据源的最后一次值
        
        参数:
            source_id: 数据源ID
            
        返回:
            Optional[Dict[str, Any]]: 最后一次获取的值，如果不存在则返回None
        """
        return self.last_values.get(source_id)

    def _validate_source_config(self, config: Dict[str, Any]) -> bool:
        """
        验证数据源配置
        
        参数:
            config: 数据源配置
            
        返回:
            bool: 配置是否有效
            
        异常:
            ValueError: 当配置无效时抛出
        """
        required_fields = ['type', 'update_interval']
        
        for field in required_fields:
            if field not in config:
                raise ValueError(f"缺少必需的配置字段: {field}")
        
        if not isinstance(config['update_interval'], (int, float)) or config['update_interval'] <= 0:
            raise ValueError("更新间隔必须是正数")
        
        return True

    def _start_fetching(self, source_id: str):
        """
        启动数据获取定时器
        
        参数:
            source_id: 数据源ID
        """
        if source_id in self.update_timers:
            self.update_timers[source_id].stop()
        
        timer = QTimer(self)
        interval = int(self.data_sources[source_id]['update_interval'] * 1000)  # 转换为毫秒
        timer.setInterval(interval)
        timer.timeout.connect(lambda: self._fetch_data(source_id))
        timer.start()
        
        self.update_timers[source_id] = timer
        
        # 立即获取一次数据
        self._fetch_data(source_id)

    def _stop_fetching(self, source_id: str):
        """
        停止数据获取定时器
        
        参数:
            source_id: 数据源ID
        """
        if source_id in self.update_timers:
            self.update_timers[source_id].stop()
            del self.update_timers[source_id]

    def _fetch_data(self, source_id: str):
        """
        获取数据源数据
        
        参数:
            source_id: 数据源ID
        """
        try:
            config = self.data_sources[source_id]
            source_type = config['type']
            
            # 根据数据源类型获取数据
            if source_type == 'api':
                data = self._fetch_api_data(config)
            elif source_type == 'modbus':
                data = self._fetch_modbus_data(config)
            elif source_type == 'opcua':
                data = self._fetch_opcua_data(config)
            else:
                raise ValueError(f"不支持的数据源类型: {source_type}")
            
            # 更新最后一次获取的值
            self.last_values[source_id] = data
            
            # 发送数据更新信号
            self.data_updated.emit(source_id, data)
            
            # 更新连接状态
            if not self.connection_status.get(source_id, False):
                self.connection_status[source_id] = True
                self.connection_status_changed.emit(source_id, True)
            
        except Exception as e:
            logger.error(f"获取数据源 {source_id} 数据失败: {str(e)}")
            
            # 更新连接状态
            if self.connection_status.get(source_id, True):
                self.connection_status[source_id] = False
                self.connection_status_changed.emit(source_id, False)
            
            # 发送错误信号
            self.error_occurred.emit(source_id, str(e))

    def _fetch_api_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        从API获取数据
        
        参数:
            config: API配置
            
        返回:
            Dict[str, Any]: 获取的数据
        """
        # 实现API数据获取逻辑
        pass

    def _fetch_modbus_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        从Modbus获取数据
        
        参数:
            config: Modbus配置
            
        返回:
            Dict[str, Any]: 获取的数据
        """
        # 实现Modbus数据获取逻辑
        pass

    def _fetch_opcua_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        从OPC UA获取数据
        
        参数:
            config: OPC UA配置
            
        返回:
            Dict[str, Any]: 获取的数据
        """
        # 实现OPC UA数据获取逻辑
        pass

    def register_variable(self, variable):
        """Register a variable for data fetching."""
        if variable.variable_id in self.variables:
            logger.debug(f"Variable {variable.name} already registered")
            return False
        
        self.variables[variable.variable_id] = {
            "variable": variable,
            "last_fetch": None
        }
        logger.info(f"Registered variable {variable.name} for data fetching")
        return True
    
    def unregister_variable(self, variable_id):
        """Unregister a variable from data fetching."""
        if variable_id in self.variables:
            logger.info(f"Unregistered variable {self.variables[variable_id]['variable'].name}")
            del self.variables[variable_id]
            return True
        return False
    
    def start(self):
        """Start the data fetching process."""
        if self.fetch_thread and self.fetch_thread.is_alive():
            logger.warning("Data fetcher already running")
            return False
        
        self.stop_event.clear()
        self.fetch_thread = Thread(target=self._fetch_loop, daemon=True)
        self.fetch_thread.start()
        logger.info("Data fetcher started")
        return True
    
    def stop(self):
        """Stop the data fetching process."""
        if not self.fetch_thread or not self.fetch_thread.is_alive():
            logger.warning("Data fetcher not running")
            return False
        
        self.stop_event.set()
        self.fetch_thread.join(timeout=2)
        logger.info("Data fetcher stopped")
        return True
    
    def _fetch_loop(self):
        """Main data fetching loop."""
        while not self.stop_event.is_set():
            current_time = time.time() * 1000  # Current time in milliseconds
            
            # Check each variable to see if it needs an update
            for var_id, var_info in list(self.variables.items()):
                variable = var_info["variable"]
                last_fetch = var_info["last_fetch"] or 0
                
                # Skip if not enough time has elapsed since last fetch
                if current_time - last_fetch < variable.polling_interval:
                    continue
                
                try:
                    # Fetch new data
                    if self.mock_mode:
                        value = self._generate_mock_data(variable)
                        quality = "良好"
                    else:
                        value, quality = self._fetch_variable_data(variable)
                    
                    # Update last fetch time
                    self.variables[var_id]["last_fetch"] = current_time
                    
                    # Update variable and emit signal
                    timestamp = datetime.now().isoformat()
                    variable.update_value(value, quality, timestamp)
                    self.data_updated.emit(var_id, value)
                    
                except Exception as e:
                    logger.error(f"Error fetching data for variable {variable.name}: {str(e)}")
            
            # Sleep briefly to avoid consuming too much CPU
            time.sleep(0.1)
    
    def _fetch_variable_data(self, variable):
        """Fetch data for a specific variable from its API endpoint."""
        if not variable.api_endpoint:
            return self._generate_mock_data(variable), "模拟"
        
        try:
            # Make API request
            response = requests.get(
                variable.api_endpoint, 
                timeout=2,
                headers={"Accept": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract value from response - adjust based on your API structure
                if isinstance(data, dict):
                    # Try common field names
                    for field in ["value", "data", "result", "measurement", "reading"]:
                        if field in data:
                            return data[field], "良好"
                    
                    # If response is simple with just one key, use that
                    if len(data) == 1:
                        return next(iter(data.values())), "良好"
                
                # If it's just a number
                if isinstance(data, (int, float)):
                    return data, "良好"
                
                # Fallback
                return self._generate_mock_data(variable), "替代"
            else:
                logger.warning(f"API request failed with status {response.status_code}")
                return self._generate_mock_data(variable), "替代"
                
        except requests.RequestException as e:
            logger.error(f"API request error: {str(e)}")
            return self._generate_mock_data(variable), "替代"
    
    def _generate_mock_data(self, variable):
        """Generate mock data for a variable based on its data type."""
        data_type = variable.data_type.lower()
        
        # Generate value based on data type
        if data_type in ["bool", "boolean", "bit"]:
            return random.choice([True, False])
        
        elif data_type in ["int", "integer", "word", "dword"]:
            # Use current value as base if available
            base = 0
            if isinstance(variable.current_value, (int, float)):
                base = int(variable.current_value)
            
            # Generate a value that changes gradually
            change = random.randint(-5, 5)
            new_value = base + change
            
            # Apply thresholds occasionally to test alarms
            if random.random() < 0.05 and variable.threshold.enabled:
                if variable.threshold.alarm_high is not None:
                    new_value = variable.threshold.alarm_high + random.randint(1, 10)
                elif variable.threshold.warning_high is not None:
                    new_value = variable.threshold.warning_high + random.randint(1, 5)
            
            return new_value
        
        elif data_type in ["float", "real", "double"]:
            # Use current value as base if available
            base = 0.0
            if isinstance(variable.current_value, (int, float)):
                base = float(variable.current_value)
            
            # Generate a value that changes gradually
            change = random.uniform(-1.0, 1.0)
            new_value = base + change
            
            # Apply thresholds occasionally to test alarms
            if random.random() < 0.05 and variable.threshold.enabled:
                if variable.threshold.alarm_high is not None:
                    new_value = variable.threshold.alarm_high + random.uniform(0.1, 2.0)
                elif variable.threshold.warning_high is not None:
                    new_value = variable.threshold.warning_high + random.uniform(0.1, 1.0)
            
            return round(new_value, 2)
        
        elif data_type in ["string", "text"]:
            return f"Sample-{random.randint(1000, 9999)}"
        
        else:
            return None 