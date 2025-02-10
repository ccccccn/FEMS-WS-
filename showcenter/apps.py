import asyncio
import json
import logging
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
from django.apps import AppConfig

from showcenter.views import CABIN_NUM, send_to_redis_channel
from apscheduler.schedulers.asyncio import AsyncIOScheduler
logger = logging.getLogger(__name__)

soc_value = np.array([random.randint(-100, 100) for _ in range(20)])
soc_bins = np.arange(-100, 101, 20)




class ShowcenterConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "showcenter"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("ShowcenterConfig __init__ called!")  # 添加调试信息

    def ready(self):
        logger.info("ShowCenterConfig Ready!")
        # import showcenter.signals
        self.initial_threadpool()
#
#     #方法一所对初始化异步操作
#     # def initial_threadpool(self):
#     #     loop = asyncio.get_event_loop()
#     #     loop.create_task(self.run_scheduled_tasks())
#     #     logger.info("Thread pool initialized and tasks submitted.")
#
    ##方法二所对初始化异步操作：
    def initial_threadpool(self):
        print("仅借用启动一下")
        # scheduler = AsyncIOScheduler()
        # scheduler.add_job(self.scheduled_task, 'interval', seconds=1)
        # scheduler.start()
        # logger.info("Thread pool initialized and tasks submitted.")


# 方法二使用apscheduler 支持异步操作和停止主线程操作
    async def scheduled_task(self):
        print("借用启动一下")
        send_to_redis_channel("show_center")
        try:
            await asyncio.sleep(0.001)
        except CancelledError as e:
            logger.error(f"用户停止了操作")
            pass
