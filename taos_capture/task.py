# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: task.py
 @DateTime: 2025-04-28 12:05
 @SoftWare: PyCharm
"""
from celery import shared_task

from .Collector_controller import start_collect


@shared_task
def run_data_collect_task():
    start_collect()
