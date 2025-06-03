#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API客户端模块
作者: zhongqi.wang
"""

import os
import time
import json
import logging
import requests
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class APIClient(QObject):
    """API客户端类，用于处理与远程API的通信"""
    
    # API连接状态变化信号
    connection_status_changed = pyqtSignal(str, bool)  # 端点, 是否连接
    
    # API请求失败信号
    request_failed = pyqtSignal(str, str)  # 端点, 错误信息
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        初始化API客户端
        
        参数:
            base_url: API基础URL
            api_key: API密钥（可选）
        """
        super().__init__()
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        # 连接池，用于跟踪连接状态
        self.connection_pool = {}  # 字典，用于跟踪连接状态
        
        # 设置默认请求头
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        if api_key:
            self.session.headers['Authorization'] = f'Bearer {api_key}'
        
        # 连接检查定时器
        self.connection_timer = QTimer()
        self.connection_timer.timeout.connect(self.check_connections)
        self.connection_timer.start(30000)  # 每30秒检查一次
    
    def set_base_url(self, base_url):
        """Set the base URL for API requests."""
        self.base_url = base_url.rstrip('/')
    
    def set_api_key(self, api_key):
        """Set the API key for authentication."""
        self.api_key = api_key
        if api_key:
            self.session.headers['Authorization'] = f'Bearer {api_key}'
        elif 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        发送HTTP请求并处理响应
        
        参数:
            method: HTTP方法（GET, POST等）
            endpoint: API端点
            **kwargs: 请求的其他参数
            
        返回:
            Dict[str, Any]: API响应数据
            
        异常:
            APIError: 当API请求失败时
        """
        url = f'{self.base_url}/{endpoint.lstrip("/")}'
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败: {str(e)}")
            self._update_connection_status(endpoint, False)
            self.request_failed.emit(endpoint, str(e))
            raise APIError(f"API请求失败: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {str(e)}")
            self._update_connection_status(endpoint, False)
            self.request_failed.emit(endpoint, str(e))
            raise APIError(f"无效的JSON响应: {str(e)}")

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        发送GET请求
        
        参数:
            endpoint: API端点
            params: URL参数（可选）
            
        返回:
            Dict[str, Any]: API响应数据
        """
        return self._make_request('GET', endpoint, params=params)

    def post(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        """
        发送POST请求
        
        参数:
            endpoint: API端点
            data: 请求数据
            
        返回:
            Dict[str, Any]: API响应数据
        """
        return self._make_request('POST', endpoint, json=data)

    def put(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        """
        发送PUT请求
        
        参数:
            endpoint: API端点
            data: 请求数据
            
        返回:
            Dict[str, Any]: API响应数据
        """
        return self._make_request('PUT', endpoint, json=data)

    def delete(self, endpoint: str) -> Dict[str, Any]:
        """
        发送DELETE请求
        
        参数:
            endpoint: API端点
            
        返回:
            Dict[str, Any]: API响应数据
        """
        return self._make_request('DELETE', endpoint)

    def check_connections(self):
        """Check the status of all tracked API connections."""
        for endpoint, status in list(self.connection_pool.items()):
            # Skip if we already know it's connected
            if status.get("is_connected", False) and time.time() - status.get("last_check", 0) < 300:
                continue
            
            # Make a test request
            try:
                url = self._build_url(endpoint, use_base_url=status.get("use_base_url", True))
                response = self.session.get(
                    url,
                    headers=self.session.headers,
                    timeout=2
                )
                
                is_connected = response.status_code < 400
                self._update_connection_status(endpoint, is_connected)
                
            except requests.RequestException:
                self._update_connection_status(endpoint, False)
    
    def _build_url(self, endpoint, use_base_url=True):
        """Build the full URL for an API request."""
        if use_base_url and self.base_url:
            # Ensure we don't have double slashes
            if self.base_url.endswith("/") and endpoint.startswith("/"):
                endpoint = endpoint[1:]
            return f"{self.base_url}/{endpoint}" if not self.base_url.endswith("/") else f"{self.base_url}{endpoint}"
        
        return endpoint
    
    def _update_connection_status(self, endpoint, is_connected):
        """Update the connection status for an endpoint."""
        if endpoint not in self.connection_pool:
            self.connection_pool[endpoint] = {
                "is_connected": is_connected,
                "last_check": time.time()
            }
            self.connection_status_changed.emit(endpoint, is_connected)
        elif self.connection_pool[endpoint].get("is_connected") != is_connected:
            self.connection_pool[endpoint]["is_connected"] = is_connected
            self.connection_pool[endpoint]["last_check"] = time.time()
            self.connection_status_changed.emit(endpoint, is_connected)
        else:
            # Just update the timestamp
            self.connection_pool[endpoint]["last_check"] = time.time() 

class APIError(Exception):
    """API错误异常类"""
    pass 