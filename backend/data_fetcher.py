#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json
import random
import time
from datetime import datetime
from threading import Thread, Event
import requests
from PyQt5.QtCore import QObject, pyqtSignal

logger = logging.getLogger(__name__)

class DataFetcher(QObject):
    """Class for fetching real-time data from backend APIs."""
    
    # Signal emitted when new data is available
    data_updated = pyqtSignal(object, object)  # variable_id, new_value
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.variables = {}  # Dictionary of variables by ID
        self.stop_event = Event()
        self.fetch_thread = None
        self.mock_mode = False  # Set to True to generate mock data instead of API calls
    
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