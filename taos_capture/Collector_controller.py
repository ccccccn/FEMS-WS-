# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: Collector_controller.py
 @DateTime: 2025-04-08 15:39
 @SoftWare: PyCharm
"""
import asyncio
import threading

from taos_capture.capture_utils import data_capture_main

collect_thread = None
collect_loop = None
collect_task = None
is_running = False
import logging

logger = logging.getLogger('data_capture')


def start_collect():
    global collect_thread, collect_loop, collect_task, is_running
    if is_running:
        logger.warning("采集正在执行")
        pass

    def run_loop():
        global collect_loop, collect_task
        collect_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(collect_loop)
        collect_task = collect_loop.create_task(data_capture_main())
        try:
            collect_loop.run_until_complete(collect_task)
        except Exception as e:
            logger.exception("采集任务异常")

    logger.info("启动采集线程")
    collect_thread = threading.Thread(target=run_loop)
    collect_thread.start()
    is_running = True


def stop_collect():
    global collect_thread, collect_loop, collect_task, is_running
    if not is_running:
        logger.warning("采集仍未启动")
        return
    if collect_task:
        collect_task.cancel()
    if collect_loop:
        collect_loop.stop()
    is_running = False
    logger.info("采集已停止")


def reset_collect():
    stop_collect()
    start_collect()
    logger.info("已开始重新采集")
