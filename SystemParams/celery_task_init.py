# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: celery_task_init.py
 @DateTime: 2025-05-21 8:43
 @SoftWare: PyCharm
"""
import json

from django.utils.timezone import now
from django_celery_beat.models import IntervalSchedule, PeriodicTask, CrontabSchedule


def init_periodic_task():
    interval_1s, _ = IntervalSchedule.objects.get_or_create(
        every=1,
        period=IntervalSchedule.SECONDS
    )

    PeriodicTask.objects.update_or_create(
        name="systemParamsDetailView",
        defaults={
            'task': 'SystemParams.tasks.systemParamsDetailView',
            'interval': interval_1s,
            'start_time': now()
        }
    )

    PeriodicTask.objects.update_or_create(
        name="systemParamsView",
        defaults={
            'task': 'SystemParams.tasks.systemParamsView',
            'interval': interval_1s,
            'start_time': now()
        }
    )
