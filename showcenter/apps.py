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

from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = logging.getLogger(__name__)


class ShowcenterConfig(AppConfig):
    name = "showcenter"
    default_auto_field = "django.db.models.BigAutoField"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scheduler = None
        self.loop = None
        logger.info("ShowcenterConfig __init__ called!")  # 添加调试信息

    def ready(self):
        logger.info("ShowCenterConfig Ready!")
        # import showcenter.signals
        thread = threading.Thread(target=self.initial_threadpool)
        thread.daemon = True
        thread.start()

    ##方法二所对初始化异步操作：
    def initial_threadpool(self):
        # 创建一个新的事件循环
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        # 创建调度器
        self.scheduler = AsyncIOScheduler()
        self.scheduler.add_job(self.scheduled_task, 'interval', seconds=1, max_instances=5)

        # 启动事件循环
        try:
            self.loop.run_until_complete(self.start_scheduler())
        except KeyboardInterrupt:
            self.loop.stop()
            self.loop.close()
        finally:
            self.scheduler.shutdown()

    async def start_scheduler(self):
        self.scheduler.start()
        while True:
            await asyncio.sleep(1)

    # 方法二使用apscheduler 支持异步操作和停止主线程操作
    async def scheduled_task(self):
        from .views import CABIN_NUM, send_to_redis_channel
        try:
            send_to_redis_channel("show_center")
            try:
                await asyncio.sleep(0.001)
            except CancelledError as e:
                logger.error(f"用户停止了操作")
                pass
        except Exception as e:
            logger.error(f"中心数据展示失败{e}")
