# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: task.py
 @DateTime: 2025-01-22 8:54
 @SoftWare: PyCharm
"""
from venv import logger

from common.celery import Celery, shared_task
from common.celery import crontab

app = Celery('showcenter')

app.conf.beat_schedule = {
    'scheduled-task': {
        'task': 'showcenter.tasks.scheduled_task',
        'schedule': crontab(minute='*/5'),  # 每5分钟执行一次
    },
}

@shared_task
def scheduled_task():
    logger.info("Scheduled task is running")