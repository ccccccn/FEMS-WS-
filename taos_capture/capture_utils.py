# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: capture_utils.py
 @DateTime: 2025-02-11 15:05
 @SoftWare: PyCharm
"""
import time

import numpy as np
from snap7 import Client

from taos_capture.shared_data import collect_plcs, FLC_NUM
from .models import plc_connection_status

def check_plc_connected(plcs):
    is_connected = np.random.randint(0, 2, size=FLC_NUM)
    # for plc in plcs:
    #     plc = Client()
    #     if plc.get_connected():
    #         is_connected[int(plc['ip'].split(".")[-1]) - 1] = 1
    return is_connected


def check_plc_connected_loop():
    global plc_connection_status
    while True:
        # print("running...."）
        is_connected_status = check_plc_connected(collect_plcs)
        plc_connection_status.connected = is_connected_status
        # print('is_connected_status:', plc_connection_status.connected)
        time.sleep(5)
