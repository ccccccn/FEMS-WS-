# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: task.py
 @DateTime: 2025-01-22 8:54
 @SoftWare: PyCharm
"""
import datetime
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from celery import Celery, shared_task
from celery.schedules import crontab
from django_apscheduler.jobstores import DjangoJobStore

from common.TaosClass import TaosClass

app = Celery('showcenter')

logger = logging.getLogger('showcenter')

app.conf.beat_schedule = {
    'scheduled-task': {
        'task': 'showcenter.tasks.scheduled_task',
        'schedule': crontab(minute='*/15'),  # 每15分钟执行一次
    },
}

scheduler = BackgroundScheduler(timezone='Asia/Shanghai')
scheduler.add_jobstore(DjangoJobStore(), "default")

taos = TaosClass('localhost', 'taos', 'taosdata', 6030)
taos.connect("fems")


@shared_task
def scheduled_task():
    logger.info("Scheduled task is running")



@scheduler.scheduled_job('interval', minutes=15, id='showcenter_piedata_15min_task')
def statistic_show_center_pie_data_15min(i):
    pie_data_sql = (f'select HISTOGRAM("飞轮舱{i}_SYS_SOC",20,0,100),'
                    f'HISTOGRAM("飞轮舱{i}_SYS_ACTION",2,0,15),'
                    f'HISTOGRAM("飞轮舱{i}_SYS_FRE",20,0,100) from `飞轮舱{i}` '
                    f'where ts >= {datetime.time}')
    """
        output:
        [
                ([(bucket_start, count), ...], [(bucket_start, count), ...], [(bucket_start, count), ...])
        ]
        """


