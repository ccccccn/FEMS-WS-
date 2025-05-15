# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: HeartBeat.py
 @DateTime: 2025-04-28 15:41
 @SoftWare: PyCharm
"""
import json

import numpy as np
import redis
import taos
from celery import shared_task

heart_beat_redis = redis.StrictRedis(host='localhost', port=6379, db=2,
                                     decode_responses=True, charset='utf-8', encoding='utf-8')


def HeartBeat():
    OnlineCount = 0
    listen_data = json.loads(heart_beat_redis.get('latest_fw_data'))  # 顶层大约21个
    for key, value in listen_data.items():
        if key[-1] == 0:
            continue
        # 只判断 FW_1 ~ FW_8 通讯状态是否都为 1
        # all()具有短路机制
        if all(value.get(f"FW_{i}_通讯状态", 0) == 1 for i in range(1, 9)):
            OnlineCount += 1
    return OnlineCount
