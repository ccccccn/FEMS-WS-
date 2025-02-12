from django.apps import AppConfig

import logging

class DataTransportConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "data_transport"

    def ready(self):
        logging.info("IPad Starting...")
        from data_transport.views import data_capture_main as DT
        DT()