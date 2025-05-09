import threading
from venv import logger

from django.apps import AppConfig

from SystemParams.views import systemParamsView, systemParamsDetailView


class SystemparamsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "SystemParams"


    def ready(self):
        logger.info('System Params Start!')
        system_thread = threading.Thread(target=systemParamsView,daemon=True)
        system_thread.start()
        system_thread = threading.Thread(target=systemParamsDetailView, daemon=True)
        system_thread.start()
        logger.info('System Params Start!')