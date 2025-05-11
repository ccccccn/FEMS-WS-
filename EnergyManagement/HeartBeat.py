# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: HeartBeat.py
 @DateTime: 2025-04-28 15:41
 @SoftWare: PyCharm
"""
import taos
from celery import shared_task


def HeartBeat():
    taosConn = taos.connect("localhost", "root", "taosdata", 6030)
    conn = taosConn.select_db("FEMS")
    tcur = taosConn.cursor()
    FW_list = []
    for i in range(1,9):
        FW_list.append(f"FW_{i}_通讯状态")
    FW_string = ",".join(FW_list)
    heartBeat_sql = f'select first({FW_string}) from FEMS group by `ip_id`'
    def and_tuple(bits):
        result = 1
        for bit in bits:
            result&= bit
        return result
    while True:
        tcur.execute(heartBeat_sql)
        result = tcur.fetchall()[0]
        and_result = [and_tuple(tup) for tup in result]

        total_ones = sum(and_result)
        return total_ones

