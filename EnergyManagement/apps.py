import logging
import threading

import redis
from time import sleep
import atexit

from apscheduler.schedulers.background import BackgroundScheduler
from django.apps import AppConfig
from django.db.models.signals import post_migrate

logger = logging.getLogger(__name__)

"""
在apps.py中仅启动调度器并不启动调度任务
start_scheduler()

"""


class EnergymanagementConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "EnergyManagement"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info("EnergymanagementConfig init call!")

    def ready(self):
        logger.info("Starting energy management")
        energy_thread = threading.Thread(target=self.start_scheduler, daemon=True)
        energy_thread.start()
        logger.info("能量管理任务调度器启动")



    def start_scheduler(self):
        from EnergyManagement.Energy_task import start_energy_scheduler
        try:
            start_energy_scheduler()
        except Exception as e:
            logger.error(f"能量管理界面任务调度器出现问题：{e}")
