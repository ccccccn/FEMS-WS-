from django.shortcuts import render

# Create your views here.

import asyncio
import logging
import random
from time import sleep

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.

import json
import os
import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import numpy as np
from django.http import JsonResponse
from snap7.client import Client
from sortedcontainers import SortedList

from data_transport.data_share import cache, collect_plcs
from taos_capture.models import plc_connection_status
from showcenter.views import send_to_redis_channel
from taosPro.utils import get_data, file_data, JsonCache


lock = threading.Lock()
# 数据解析示例
def parse_data(plc_ip, data, db):
    # global soc_value, frequency_value, duration_value, soc_hist, frequency_hist, duration_hist
    global soc_hist, frequency_hist, duration_hist
    flc_num = str(plc_ip.split('.')[-1])
    # print(f"当前解析ip为{plc_ip},飞轮舱号为{flc_num}\n", end='')
    # 解析并处理数据
    data_dir = {}
    cache_data = cache.cache.get(f"DBDB{db}")
    for key in cache_data:
        cache_adata = cache_data[key]
        value = round(get_data(cache_adata, data), 3)
        data_dir[key] = value
            # print(f"当前{flc_num}dur:{duration_value}\n", end='')
        # print(f"{key}:{value}")
    # print(f"当前DB块数据为：{data_dir}")
    # breakpoint()
    return soc_hist, frequency_hist, duration_hist
    # data_dir_json = json.dumps(data_dir)
    print(f"当前{flc_num}DB{db}块解析结束时间为：{datetime.now()}\n", end='')


def IPadData_send():
    pass

# PLC数据采集任务
def read_plc_data(plc_ip, dbs, start, lengths, change_idx=None):
    # breakpoint()
    try:
        ## 真实数据 一次性获取所有db下的值，顺序执行
        # data = plc.db_read(db, 0, length)
        ## 模拟测试数据
        for db, length in zip(dbs, lengths):
            random_data = bytearray(random.randint(0, 100) for _ in range(length))
            # breakpoint()
            s_soc_hist, s_frequency_hist, s_duration_hist = parse_data(plc_ip, random_data, db)
            # print(type(s_soc_hist), type(frequency_hist), type(duration_hist))
        change_idx[int(plc_ip.split('.')[-1]) - 1] = 1
        try:
            if np.any(plc_connection_status.connected):
                lock.acquire()
                try:
                    if np.all(plc_connection_status.connected.astype(bool) & change_idx.astype(
                            bool) == plc_connection_status.connected):
                        IPadData_send()
                        logging.info(f"Data sent to channel show_center")
                        print(f"匹配成功，并发送数据,当前发送时间为{datetime.now()}")
                        change_idx = np.zeros(9)
                finally:
                    lock.release()
        except Exception as e:
                print(f"{type(e)}here:{e}")
            # print(f"DB{db}块获取到数据:{datetime.now()}")
    except Exception as e:
        print(f"读取PLC数据错误：{e}")
        return None




# 采集每个PLC数据
def get_plc_data(plc_ip, plc_rack, plc_slot, dbs, starts, lengths, executor):
    plc = Client()
    plc1 = Client()
    try:
        plc.connect(plc_ip, plc_rack, plc_slot)
        plc1.connect(plc_ip, plc_rack, plc_slot)
    except Exception as e:
        print(f"连接PLC失败: {e}")
        return

    if plc.get_connected():
        print(f"PLC {plc_ip} 连接成功")

        # 将 DB 块分成两部分
        dbs_plc = dbs[:5]  # 前 5 个 DB 块由 plc 处理
        starts_plc = starts[:5]
        lengths_plc = lengths[:5]

        dbs_plc1 = dbs[5:]  # 后 6 个 DB 块由 plc1 处理
        starts_plc1 = starts[5:]
        lengths_plc1 = lengths[5:]

        # 使用线程池执行读取任务
        futures = []
        Start_time = datetime.now()
        # 使用 plc 处理前 5 个 DB 块
        for db, start, length in zip(dbs_plc, starts_plc, lengths_plc):
            future = executor.submit(read_plc_data, plc, db, start, length)
            futures.append(future)

        # 使用 plc1 处理后 6 个 DB 块
        for db, start, length in zip(dbs_plc1, starts_plc1, lengths_plc1):
            future = executor.submit(read_plc_data, plc1, db, start, length)
            futures.append(future)

        # 等待所有任务完成
        for future in as_completed(futures):
            future.result()  # 等待每个任务的结果，触发异常时会被捕获

        end_time = datetime.now()
        print(f"PLC{plc_ip}本次采集所用：{end_time - Start_time}\n", end='')


# 外部线程负责管理每个PLC设备
def plc_thread(plc_ip, rack, slot, dbs, starts, lengths):
    # 每个外部线程负责不断地进行数据采集
    while True:
        Start_time = datetime.now()
        # print(f"PLC {plc_ip} 数据采集开始于：{Start_time}\n", end='')
        read_plc_data(plc_ip, dbs, starts, lengths)
        # get_plc_data(plc_ip, rack, slot, dbs, starts, lengths, executor)
        end_time = datetime.now()
        # print(f"PLC {plc_ip} 数据采集完成,完成时间为：{end_time}\n", end='')
        # print(f"PLC {plc_ip} 本次循环所用时间：{end_time - Start_time}\n", end='')
        sleep(0.5)


# 多线程执行数据采集
async def run_data_collection(plcs):
    # 创建外部线程池
    CONNECT_CNT = 0
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor(max_workers=7) as executor:  # 外部线程池，最大同时处理5个PLC
        threads = []

        for plc in plcs:
            thread = loop.run_in_executor(executor, plc_thread,
                                          plc['ip'], plc['rack'], plc['slot'], plc['dbs'], plc['starts'],
                                          plc['lengths'])
            # 每个 PLC 使用内部线程池来管理其 DB 数据采集任务
            # plc_thread_instance = threading.Thread(target=plc_thread, args=(
            #     plc['ip'], plc['rack'], plc['slot'], plc['dbs'], plc['starts'], plc['lengths'], executor))
            threads.append(thread)
            await asyncio.sleep(0.01)
        await asyncio.gather(*threads)
        # plc_thread_instance.start()

        # 等待所有外部线程完成
        for thread in threads:
            thread.join()


async def plc_is_connect(plcs):
    global is_connect
    for plc in plcs:
        is_connect[int(plc['ip'].split("_")[-1]) - 1] = random.randint(0, 2)
        # plc = Client()
        # plc.connect(plc["ip"], plc["rack"], plc['slot'])
        # if plc.get_connected():
        #     is_connect[int(plc['ip'].split("_")[-1]) - 1] = 1
        # else:
        #     is_connect[int(plc['ip'].split("_")[-1]) - 1] = 0
        await asyncio.sleep(1)
    pass


async def data_capture_main():
    try:
        # breakpoint()
        await run_data_collection(collect_plcs)
    except KeyboardInterrupt:
        print("采集任务已终止")

# if __name__ == '__main__':
