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
    interval_frequency, _ = IntervalSchedule.objects.get_or_create(
        every=1,
        period=IntervalSchedule.SECONDS
    )

    PeriodicTask.objects.update_or_create(
        name="frequency_compare_analysis",
        defaults={
            'task': 'showcenter.tasks.frequency_compare_analysis',
            'interval': interval_frequency,
            'start_time': now()
        }
    )

    center_pie_interval, _ = IntervalSchedule.objects.get_or_create(
        # every=15,
        # period=IntervalSchedule.MINUTES
        every=1,
        period=IntervalSchedule.SECONDS
    )

    PeriodicTask.objects.update_or_create(
        name="statistic_show_center_pie_data_15min",
        defaults={
            'task': 'showcenter.tasks.statistic_show_center_pie_data_15min',
            'interval': center_pie_interval,
            'start_time': now()
        }
    )

    current_data_interval, _ = IntervalSchedule.objects.get_or_create(
        every=1,
        period=IntervalSchedule.SECONDS
    )

    PeriodicTask.objects.update_or_create(
        name="current_data_play_by_redis",
        defaults={
            'task': 'showcenter.tasks.current_data_play_by_redis',
            'interval': current_data_interval,
            'start_time': now()
        }
    )

    PeriodicTask.objects.update_or_create(
        name="running_statistics_station_data",
        defaults={
            'task': 'showcenter.tasks.running_statistics_station_data',
            'interval': current_data_interval,
            'start_time': now(),
        }
    )
