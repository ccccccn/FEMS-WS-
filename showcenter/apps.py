import asyncio
import json
import logging
import multiprocessing
import os
import random
import signals
import sys
import threading
import time
from asyncio import CancelledError
from concurrent.futures import ThreadPoolExecutor
from functools import partial

import numpy as np
import schedule
from apscheduler.schedulers.background import BackgroundScheduler
from django.apps import AppConfig
from common.LogRecord import setup_logger

from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = setup_logger()


class ShowcenterConfig(AppConfig):
    name = "showcenter"
    default_auto_field = "django.db.models.BigAutoField"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scheduler = None
        self.loop = None
        logger.info("ShowcenterConfig __init__ called!")  # 添加调试信息

    def ready(self):
        pass
        # 启动线程等其他初始化操作
        # if ('runserver' in sys.argv or 'uwsgi' in sys.argv or 'gunicorn' in sys.argv) and not os.path.exists(INIT_FLAG):
        #     from showcenter.celery_task_init import init_periodic_task
        #     def safe_init():
        #         try:
        #             init_periodic_task()
        #             logger.info("初始化 Celery Beat 任务成功")
        #             print("初始化 Celery Beat 任务成功")
        #         except Exception as e:
        #             import logging
        #             logging.exception("初始化 Celery Beat 任务失败")
        #
        #     threading.Thread(target=safe_init, daemon=True).start()

    # 方法二使用apscheduler 支持异步操作和停止主线程操作
    # def start_scheduler(self):
    #     pass
    #     from showcenter.task import start_energy_scheduler
    #     try:
    #         start_energy_scheduler()
    #     except Exception as e:
    #         logger.error(f"能量管理界面任务调度器出现问题：{e}")
