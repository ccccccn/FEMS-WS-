# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: Energy_task.py
 @DateTime: 2025-04-28 16:09
 @SoftWare: PyCharm
"""
from copy import deepcopy

import redis
from celery import shared_task

from .HeartBeat import HeartBeat
from confluent_kafka import Consumer

fw_all_data_redis = redis.StrictRedis("localhost", 6379, 3,
                                      decode_responses=True, charset='UTF-8', encoding='UTF-8')

conf = {
    'bootstrap.servers': 'localhost:9092',  # Kafka 服务地址
    'group.id': 'energy_data',  # 消费组名
    'auto.offset.reset': 'latest',  # 从最早开始读（可选 latest）
}
energy_consumer = Consumer(conf)
energy_consumer.subscribe(['plc_data_kafka'])


@shared_task
def hearbeat_task():
    isOnlineNum = HeartBeat()
    return isOnlineNum


LAST_RANK_DATA = fw_all_data_redis.get('latest_fw_data')
CURRENT_RANK_DATA = {}
COUNT_DICT = {}

def get_current_rank_data():
    global CURRENT_RANK_DATA
    global LAST_RANK_DATA
    temp_data = deepcopy(LAST_RANK_DATA)
    for key, value in LAST_RANK_DATA.items():
        CURRENT_RANK_DATA[key] = {
            "SOC": value["EMS_SYS_SOC"],
            "EMS_SYS_State": value["EMS_SYS_State"]
        }
    for last_state, current_state in zip(LAST_RANK_DATA.values(), CURRENT_RANK_DATA.values()):
        if last_state != current_state:
            LAST_RANK_DATA = CURRENT_RANK_DATA
            CURRENT_RANK_DATA = {}
            break
        else:
            continue
    fw_all_data_redis.set('fw_call_soc_rank', CURRENT_RANK_DATA)
