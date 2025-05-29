#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json
import time
import requests
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

logger = logging.getLogger(__name__)

class APIClient(QObject):
    """Client for handling API communication with external data sources."""
    
    # Signal emitted when API connection status changes
    connection_status_changed = pyqtSignal(str, bool)  # endpoint, is_connected
    
    # Signal emitted when an API request fails
    request_failed = pyqtSignal(str, str)  # endpoint, error_message
    
    def __init__(self, base_url=None, api_key=None, parent=None):
        super().__init__(parent)
        self.base_url = base_url
        self.api_key = api_key
        self.connection_pool = {}  # Dictionary to track connection status
        self.session = requests.Session()
        
        # Set default headers
        self.default_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        if api_key:
            self.default_headers["Authorization"] = f"Bearer {api_key}"
        
        # Connection check timer
        self.connection_timer = QTimer(self)
        self.connection_timer.timeout.connect(self.check_connections)
        self.connection_timer.start(30000)  # Check every 30 seconds
    
    def set_base_url(self, base_url):
        """Set the base URL for API requests."""
        self.base_url = base_url
    
    def set_api_key(self, api_key):
        """Set the API key for authentication."""
        self.api_key = api_key
        if api_key:
            self.default_headers["Authorization"] = f"Bearer {api_key}"
        elif "Authorization" in self.default_headers:
            del self.default_headers["Authorization"]
    
    def get(self, endpoint, params=None, timeout=5, use_base_url=True):
        """Make a GET request to the API."""
        url = self._build_url(endpoint, use_base_url)
        
        try:
            response = self.session.get(
                url, 
                params=params,
                headers=self.default_headers,
                timeout=timeout
            )
            
            self._update_connection_status(endpoint, True)
            
            # Check for success
            response.raise_for_status()
            
            # Parse JSON response
            if response.content:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    logger.warning(f"Response from {url} is not valid JSON")
                    return response.text
            
            return None
        
        except requests.RequestException as e:
            logger.error(f"GET request to {url} failed: {str(e)}")
            self._update_connection_status(endpoint, False)
            self.request_failed.emit(endpoint, str(e))
            return None
    
    def post(self, endpoint, data=None, json_data=None, timeout=5, use_base_url=True):
        """Make a POST request to the API."""
        url = self._build_url(endpoint, use_base_url)
        
        try:
            response = self.session.post(
                url, 
                data=data,
                json=json_data,
                headers=self.default_headers,
                timeout=timeout
            )
            
            self._update_connection_status(endpoint, True)
            
            # Check for success
            response.raise_for_status()
            
            # Parse JSON response
            if response.content:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    logger.warning(f"Response from {url} is not valid JSON")
                    return response.text
            
            return None
        
        except requests.RequestException as e:
            logger.error(f"POST request to {url} failed: {str(e)}")
            self._update_connection_status(endpoint, False)
            self.request_failed.emit(endpoint, str(e))
            return None
    
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
                    headers=self.default_headers,
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