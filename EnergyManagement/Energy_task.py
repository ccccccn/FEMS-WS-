# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: Energy_task.py
 @DateTime: 2025-04-28 16:09
 @SoftWare: PyCharm
"""
import json
import logging

import atexit
from copy import deepcopy

import redis
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from celery import shared_task
from django.db import connection
from django.http import JsonResponse
from django_apscheduler.jobstores import DjangoJobStore

from .HeartBeat import HeartBeat
from confluent_kafka import Consumer

from .MapperConfig import usage_state_mapper
from .models import EnergyManageRank
from .state_manage import is_initialized, mark_initialized, load_and_init_data

logger = logging.getLogger(__name__)

fw_all_data_redis = redis.StrictRedis("localhost", 6379, 2,
                                      decode_responses=True, charset='UTF-8', encoding='UTF-8')
energy_management_redis = redis.StrictRedis('localhost', 6379, db=2,
                                            charset='utf-8', decode_responses=True, encoding='utf-8')


def hearbeat_task():
    isOnlineNum = HeartBeat()
    energy_management_redis.publish('')
    return isOnlineNum


def start_energy_scheduler():
    scheduler = BackgroundScheduler(timezone='Asia/Shanghai')
    scheduler.add_job(
        reset_rank_table,
        # trigger=IntervalTrigger(seconds=1),
        trigger=CronTrigger(hour=0, minute=0, second=0),
        id='reset_rank_table',
        replace_existing=True
    )
    scheduler.add_job(update_rank_job, 'interval', seconds=1, id='update_rank_data', max_instances=20)
    scheduler.add_job(call_state, 'interval', seconds=1, id='call_state', max_instances=5)
    scheduler.add_job(usage_state, 'interval', seconds=1, id='usage_state', max_instances=5)
    scheduler.start()


def reset_rank_table():
    EnergyManageRank.objects.all().delete()
    objs = [
        EnergyManageRank(
            id=i,
            call_time=0,
            charge_time=0,
            soc=0.00,
            discharge_time=0
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


def update_rank_job():
    is_initialize = is_initialized()
    if not is_initialize:
        from .models import EnergyManageRank
        rank_list = EnergyManageRank.objects.all()
        fw_data = fw_all_data_redis.get('latest_fw_data')
        record_dict = {}
        if fw_data:
            fw_all_data = json.loads(fw_data)
            record_dict = {
                key: {
                    "id": key,
                    "soc": value.get("EMS_SYS_SOC"),
                    "sys_state": value.get("EMS_SYS_State")
                } for key, value in fw_all_data.items()
            }

        load_and_init_data(rank_list, record_dict)
        mark_initialized()  # 设置已初始化标记
        return
    from . import state_manage
    fw_data = fw_all_data_redis.get('latest_fw_data')
    if not fw_data:
        return
    fw_all_data = json.loads(fw_data)
    current_data = {
        key: {
            "id": key,
            "soc": value.get("EMS_SYS_SOC"),
            "sys_state": value.get("EMS_SYS_State")
        }
        for key, value in fw_all_data.items()
    }
    state_manage.update_current_and_rank(current_data)

    # 更新数据库持久化
    from .models import EnergyManageRank
    from django.db import transaction
    rank_data = state_manage.get_rank_data()
    objs = [EnergyManageRank(id=int(k.split('_')[-1]), soc=v['soc'], call_time=v['call_time']) for k, v in
            rank_data.items()]
    with transaction.atomic():
        EnergyManageRank.objects.all().delete()
        EnergyManageRank.objects.bulk_create(objs)


# 阵列调用
def call_state():
    fw_all_data = json.loads(fw_all_data_redis.get('latest_fw_data'))
    data = {
        key: value.get("EMS_SYS_State")
        for key, value in fw_all_data.items()
    }
    energy_management_redis.publish('ArrayCalls', json.dumps(data, ensure_ascii=False))
    return JsonResponse(data)


# 可用情况
def usage_state():
    fw_all_data = json.loads(fw_all_data_redis.get('latest_fw_data'))
    fccs_data = fw_all_data.get("flc_0")
    try:
        data = {
            key: value
            for key, value in fccs_data.items() if key in usage_state_mapper
        }
        energy_management_redis.publish('UsageState', json.dumps(data, ensure_ascii=False))
        return JsonResponse(data)
    except Exception as e:
        print(f"未连接fccs或出现{e}")
        pass

