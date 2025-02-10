import asyncio
import logging
from asyncio import CancelledError
from venv import logger

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from django.apps import AppConfig

from taos_capture.views import data_capture_main
logger = logging.getLogger(__name__)

class TaosCaptureConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "taos_capture"
    verbose_name = "Data migration"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("DataCaptureConfig __init__ called!")  # 添加调试信息

    def ready(self):
        print("DataCaptureConfig ready!")
        self.initial_threadpool()

    # 方法一所对初始化异步操作
    # def initial_threadpool(self):
    #     loop = asyncio.get_event_loop()
    #     loop.create_task(self.run_scheduled_tasks())
    #     logger.info("Thread pool initialized and tasks submitted.")
    def initial_threadpool(self):
        print("启动启动启动")
        loop = asyncio.get_event_loop()
        loop.create_task(self.data_capture_main())
        logger.info("数据采集程序已经启动！")

    async def data_capture_main(self):
        try:
            # 假设 data_capture_main 函数已经在 views 文件中实现
            from .views import data_capture_main as view_data_capture_main
            await view_data_capture_main()
            await asyncio.sleep(0.01)  # 确保任务完成
        except asyncio.CancelledError as e:
            logger.error(f"用户停止了操作")
        except Exception as e:
            logger.error(f"数据采集主函数出错：{e}")
        # loop = asyncio.get_event_loop()
        # asyncio.set_event_loop(loop)
        # scheduler = AsyncIOScheduler()
        # scheduler.add_job(self.scheduled_task, 'interval', seconds=1,
        #                   max_instances=1)
        # scheduler.start()
        # logger.info("Thread pool initialized and tasks submitted.")
    ##方法二所对初始化异步操作：

    # 方法二使用apscheduler 支持异步操作和停止主线程操作
    async def scheduled_task(self):
        await data_capture_main()
        try:
            await asyncio.sleep(0.01)
        except asyncio.CancelledError as e:
            logger.error(f"用户停止了操作")
            pass


