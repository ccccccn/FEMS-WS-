# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: Energy_task.py
 @DateTime: 2025-04-28 16:09
 @SoftWare: PyCharm
"""
from celery import shared_task

from .HeartBeat import HeartBeat

@shared_task
def hearbeat_task():
    isOnlineNum = HeartBeat()
    return isOnlineNum