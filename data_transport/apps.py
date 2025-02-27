import asyncio

from django.apps import AppConfig

import logging

from showcenter.apps import logger


class DataTransportConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "data_transport"

    def ready(self):
        logger.info("IPad Starting...")
        loop = asyncio.get_event_loop()
        loop.create_task(self.run())

    async def run(self):
        try:
            from data_transport.views import data_capture_main as DT
            await DT()
            await asyncio.sleep(0.01)
        except asyncio.CancelledError as e:
            logging.error("用户停止了程序")
        except Exception as e:
            logging.error(f"程序启动错误：{e}")
