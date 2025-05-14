# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: Energy_task.py
 @DateTime: 2025-04-28 16:09
 @SoftWare: PyCharm
"""
import logging

import atexit
from copy import deepcopy

import redis
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from celery import shared_task
from django.db import connection
from django_apscheduler.jobstores import DjangoJobStore

from .HeartBeat import HeartBeat
from confluent_kafka import Consumer

from .models import EnergyManageRank

logger = logging.getLogger(__name__)

fw_all_data_redis = redis.StrictRedis("localhost", 6379, 3,
                                      decode_responses=True, charset='UTF-8', encoding='UTF-8')


@shared_task
def hearbeat_task():
    isOnlineNum = HeartBeat()
    return isOnlineNum

def start_energy_scheduler():
    scheduler = BackgroundScheduler(timezone='Asia/Shanghai')
    scheduler.add_job(
        reset_rank_table,
        # trigger=IntervalTrigger(seconds=20),
        trigger=CronTrigger(hour=0, minute=0, second=0),
        id='reset_rank_table',
        replace_existing=True
    )
    scheduler.start()

def reset_rank_table():
    EnergyManageRank.objects.all().delete()
    objs = [
        EnergyManageRank(
            id=i,
            call_time=0,
            call_rank=i,
            soc=0.00,
            soc_rank=i
        ) for i in range(1, 51)  # id 自增不需要指定
    ]
    EnergyManageRank.objects.bulk_create(objs)
    logger.info("Reset rank_table")
    init_sql = 'select * from energy_manage_rank'
    init_data = {}
    try:
        with connection.cursor() as cursor:
            cursor.execute(init_sql)
            data = cursor.fetchall()
            print(f"data={data},{type(data)}")
    except AttributeError:
        logger.error("'Cursor' object has no attribute 'excute'")
    except Exception as e:
        logger.error(f"other error:{e}")
