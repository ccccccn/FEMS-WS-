# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: celery_task_init.py
 @DateTime: 2025-05-21 8:43
 @SoftWare: PyCharm
"""
from django.utils.timezone import now
from django_celery_beat.models import IntervalSchedule, PeriodicTask, CrontabSchedule


def init_periodic_task():
    # 1s定间隔配置
    interval_1s, _ = IntervalSchedule.objects.get_or_create(
        every=1,
        period=IntervalSchedule.SECONDS
    )
    # 排名定时任务
    PeriodicTask.objects.update_or_create(
        name="update_rank_job",
        defaults={
            'task': 'EnergyManagement.tasks.update_rank_job',
            'interval': interval_1s,
            'start_time': now()
        }
    )
    # 趋势任务
    PeriodicTask.objects.update_or_create(
        name="energy_trend_analysis",
        defaults={
            'task': 'EnergyManagement.tasks.energy_trend_analysis',
            'interval': interval_1s,
            'start_time': now()
        }
    )
    # 调用情况定时任务
    PeriodicTask.objects.update_or_create(
        name="call_state",
        defaults={
            'task': 'EnergyManagement.tasks.call_state',
            'interval': interval_1s,
            'start_time': now()
        }
    )
    # 可用情况定时任务
    PeriodicTask.objects.update_or_create(
        name="usage_state",
        defaults={
            'task': 'EnergyManagement.tasks.usage_state',
            'interval': interval_1s,
            'start_time': now()
        }
    )
    cron_rank_table, _ = CrontabSchedule.objects.get_or_create(
        minute='0',
        hour='0',
        day_of_week='*',
        day_of_month='*',
        month_of_year='*',
    )
    # 重置调用表定时任务
    PeriodicTask.objects.update_or_create(
        name="reset_rank_table",
        defaults={
            'task': 'EnergyManagement.tasks.reset_rank_table',
            'crontab': cron_rank_table,
            'start_time': now()
        }
    )
