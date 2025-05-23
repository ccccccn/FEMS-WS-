# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: tasks.py
 @DateTime: 2025-04-28 16:09
 @SoftWare: PyCharm
"""
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

import atexit
from copy import deepcopy

import redis
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from celery import shared_task
from django.db import connection
from django.http import JsonResponse
# from django_apscheduler.jobstores import DjangoJobStore

from common.utils import cost_time
from taosPro.celery import fems_app
from .HeartBeat import HeartBeat
from confluent_kafka import Consumer

from .MapperConfig import usage_state_mapper, energy_trend_analysis_mapper
from .models import EnergyManageRank
from .state_manage import StateManage

state_manager = StateManage()

logger = logging.getLogger(__name__)

fw_all_data_redis = redis.StrictRedis("localhost", 6379, 2,
                                      decode_responses=True, charset='UTF-8', encoding='UTF-8')
energy_management_redis = redis.StrictRedis('localhost', 6379, db=2,
                                            charset='utf-8', decode_responses=True, encoding='utf-8')
energy_thread_exe = ThreadPoolExecutor(max_workers=5)


def hearbeat_task():
    isOnlineNum = HeartBeat()
    energy_management_redis.publish('')
    return isOnlineNum


# def start_energy_scheduler():
#     scheduler = BackgroundScheduler(timezone='Asia/Shanghai', daemon=True, executor=energy_thread_exe)
#     scheduler.add_job(
#         reset_rank_table,
#         # trigger=IntervalTrigger(seconds=1),
#         trigger=CronTrigger(hour=0, minute=0, second=0),
#         id='reset_rank_table',
#         replace_existing=True
#     )
#     scheduler.add_job(update_rank_job, 'interval', seconds=1, id='update_rank_data', max_instances=20)
#     scheduler.add_job(call_state, 'interval', seconds=1, id='call_state', max_instances=5)
#     scheduler.add_job(usage_state, 'interval', seconds=1, id='usage_state', max_instances=5)
#     scheduler.start()
recent_30days_queue = Queue()


@fems_app.task
def reset_rank_table():
    objs = [
        EnergyManageRank(
            id=i,
            recent_30days=0,
            call_time=0,
            charge_time=0,
            soc=0.00,
            discharge_time=0
        ) for i in range(1, 51)  # id 自增不需要指定
    ]
    EnergyManageRank.objects.all().delete()
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


@fems_app.task(queue='EnergyManagement')
def update_rank_job():
    # print("update_rank_job call!")
    is_initialize = state_manager.is_initialized()
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

        state_manager.load_and_init_data(rank_list, record_dict)
        state_manager.mark_initialized()  # 设置已初始化标记
        return f"初始化结束rank_list:{rank_list},record_dict:{record_dict}"
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
    state_manager.update_current_and_rank(current_data)

    # 更新数据库持久化
    from .models import EnergyManageRank
    from django.db import transaction
    rank_data = state_manager.get_rank_data()
    objs = [EnergyManageRank(id=int(k.split('_')[-1]), soc=v['soc'], call_time=v['call_time']
                             , charge_time=v['charge_time'], discharge_time=v['discharge_time']) for k, v in
            rank_data.items()]

    with transaction.atomic():
        EnergyManageRank.objects.all().delete()
        EnergyManageRank.objects.bulk_create(objs)
    return f"rank_data:{rank_data}"


@fems_app.task(queue='EnergyManagement')
# 阵列调用
def call_state():
    raw_data = fw_all_data_redis.get('latest_fw_data')
    if not raw_data:
        return {'error': 'No data in Redis'}

    try:
        fw_all_data = json.loads(raw_data)
        data = {
            k: v.get("EMS_SYS_State")
            for k, v in fw_all_data.items()
            if isinstance(v, dict)
        }
        energy_management_redis.publish('ArrayCalls', json.dumps(data))
        return {'status': 'success', 'data': data}
    except Exception as e:
        return {'error': str(e)}


@fems_app.task(queue='EnergyManagement')
# 可用情况
def usage_state():
    try:
        raw_data = energy_management_redis.get('latest_fw_data')
        if not raw_data:
            logger.warning("Redis 中未找到 latest_fw_data")
            return
        fw_all_data = json.loads(raw_data)
        fccs_data = fw_all_data.get("flc_0")
        if not fccs_data:
            logger.warning("flc_0 数据不存在")
            return
        data = {
            key: value
            for key, value in fccs_data.items() if key in usage_state_mapper
        }
        energy_management_redis.publish(f'UsageState', json.dumps(data, ensure_ascii=False))
        return {'status': 'success', 'msg': f'该信息已发送至channel-UsageState'}
    except Exception as e:
        logger.exception(f"[Usage] 任务执行失败: {e}")

@fems_app.task(queue='EnergyManagement')
def energy_trend_analysis():
    try:
        raw_data = energy_management_redis.get('latest_fw_data')
        if not raw_data:
            logger.warning("Redis 中未找到 latest_fw_data")
            return
        fw_all_data = json.loads(raw_data)
        fccs_data = fw_all_data.get("flc_0")
        if not fccs_data:
            logger.warning("flc_0 数据不存在")
            return
        data = {
            key: value
            for key, value in fccs_data.items() if key in energy_trend_analysis_mapper
        }
        # logger.info(f"[UsageState] 发布数据: {data}")
        energy_management_redis.publish(f'energy_trend_analysis', json.dumps(data, ensure_ascii=False))
        return {'status': 'success', 'msg': f'该信息已发送至channel-energy_trend_analysis'}
    except Exception as e:
        logger.exception(f"[energy_trend_analysis] 任务执行失败: {e}")
