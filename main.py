#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import logging
from PyQt5.QtWidgets import QApplication
from frontend.views.main_window import MainWindow
from backend.services.config_service import config_service
from backend.services.acquisition_service import acquisition_service
from backend.models.variable import Variable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def initialize_services():
    """Initialize application services."""
    try:
        # Get acquisition settings from config
        acq_settings = config_service.get_acquisition_settings()
        
        # Configure global acquisition settings
        acquisition_service.set_update_rate(acq_settings.get("update_rate", 1.0))
        acquisition_service.set_logging(
            acq_settings.get("logging_enabled", False),
            acq_settings.get("logging_interval", 60)
        )
        
        # Configure storage settings******
        storage_settings = config_service.get_storage_settings()
        acquisition_service.set_storage_location(storage_settings.get("location", "logs"))
        acquisition_service.set_storage_format(storage_settings.get("format", "json"))
        
        # Load variables from config
        variables_config = config_service.get_all_variables()
        for var_config in variables_config:
            # Create variable from config
            variable = Variable.from_dict(var_config)
            
            # Add variable to acquisition service
            acquisition_service.add_variable(variable)
            
            # Set variable-specific acquisition settings
            variable.set_acquisition_settings(
                collection_frequency=var_config.get("collection_frequency", 1.0),
                storage_frequency=var_config.get("storage_frequency", 60.0),
                storage_enabled=var_config.get("storage_enabled", True)
            )
        
        logger.info("Services initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing services: {str(e)}", exc_info=True)
        return False

def main():
    """Main entry point for the application."""
    try:
        # Initialize services
        if not initialize_services():
            logger.error("Failed to initialize services")
            return 1
        
        # Create the Qt Application
        app = QApplication(sys.argv)
        app.setApplicationName("Data Acquisition System")
        
        # Create and show the main window
        main_window = MainWindow()
        main_window.show()
        
        # Start the acquisition service
        acquisition_service.start()
        
        # Start the event loop
        result = app.exec_()
        
        # Stop the acquisition service
        acquisition_service.stop()
        
        return result
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 