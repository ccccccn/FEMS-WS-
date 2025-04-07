import redis
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
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_http_methods
from snap7.client import Client
from sortedcontainers import SortedList

from data_transport.data_share import cache, collect_plcs
from data_transport.models import PLCConnectStatu
from taos_capture.models import plc_connection_status
from showcenter.views import send_to_redis_channel
from taosPro.utils import get_data, file_data, JsonCache

lock = threading.Lock()
redis_BigCreen = redis.StrictRedis("localhost", 6379, 3, decode_responses=True, charset='utf-8', encoding='utf-8')


class IpadDataView(View):
    @method_decorator(require_http_methods(["GET"]))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request,*args,**kwargs)

    def get(self,requst,*args,**kwargs):
        data = redis_BigCreen.get('bigscreen')
        if data is not None:
            return JsonResponse(json.loads(data))
        else:
            return JsonResponse({'error':'No data avaliable'},status=404)

# 数据解析示例
def parse_data(plc_ip, data, db):
    flc_num = str(plc_ip.split('.')[-1])
    # print(f"当前解析ip为{plc_ip},飞轮{flc_num}-{int(flc_num) + 14}\n", end='')
    # 解析并处理数据

    data_list = []
    final_dir = {}
    cache_data = cache.cache.get(f"DB{db}")  ## data_dir
    for idx, chunk in enumerate(chunk_dict(cache_data, 9), start=1):
        value_list = []
        data_dir = {"time": str(datetime.now())}
        fl_num = idx
        for key, value in chunk.items():
            cache_adata = cache_data[key]
            if cache_adata['Type'] == 'FLOAT':
                value = round(get_data(cache_adata, data), 3)
            else:
                value = get_data(cache_adata, data)
            # fl_num = int(key.split('_')[0][-1])
            if fl_num not in data_dir:
                data_dir[fl_num] = {}
            value_list.append(value)
        data_dir[fl_num] = value_list
        data_list.append(data_dir)
    for data_dir in data_list:
        final_dir.update(data_dir)
    # print("final_dir", final_dir)
    return final_dir


redis = redis.StrictRedis(host='localhost', port=6379, db=2, socket_keepalive=-1)


def ipad_data_send(ipad_data):
    try:
        # print(f"当前IPad_Data:{ipad_data},当前时间为：{datetime.now()}")
        if isinstance(ipad_data, dict):
            ipad_data_json = json.dumps(ipad_data, ensure_ascii=False)
        # print("ipad_data类型", ipad_data_json)
        redis.publish("ipad_data", ipad_data_json)
        sleep(2)
    except Exception as e:
        print(f"Error sending data to Redis channel: {e}")


def chunk_dict(data, chunk_size=None):
    keys = list(data.keys())
    for i in range(0, len(keys), chunk_size):
        chunk = {key: data[key] for key in keys[i:chunk_size + i]}
        yield chunk


# PLC数据采集任务
def read_plc_data(plc_ip, dbs, start, lengths, change_idx=None):
    IPad_data = {f"time:{datetime.now()}"}
    """
    MBC编号：string
    设备编号：string
    飞轮型号：string
    电压等级：float(0-220)
    真空度：float(0-30)
    温度:float(0-60)
    转速：int(14000-29000)
    测试状态：bool
    设备状态：bool
    """
    # breakpoint()
    try:
        for i in range(2):
            ipad_list = [f"MBC{i}",f"De{i}",f"FW_{i}"]
            ipad_list.append(round(random.uniform(0.0,220.0),2))
            ipad_list.append(round(random.uniform(0.0,30.0),2))
            ipad_list.append(round(random.uniform(0.0,60.0),2))
            ipad_list.append(random.randint(14000,29000))
            ipad_list.append(random.choice([True,False]))

        ## 真实数据 一次性获取所有db下的值，顺序执行
        # data = plc.db_read(db, 0, length)
        ## 模拟测试数据
        for db, length in zip(dbs, lengths):
            IPad_data =
            random_data = bytearray(random.randint(0, 100) for _ in range(length))
            # breakpoint()
            IPad_data = parse_data(plc_ip, random_data, db)
            redis_BigCreen.set('bigscreen', json.dumps(IPad_data,ensure_ascii=False).encode('utf-8'))
            # IPad_data = json.dumps(IPad_data, ensure_ascii=False).encode('utf-8')

            ipad_data_send(IPad_data)
            # logging.info("Sending data to Ipad_data")
            # print("成功发送至ipad_data")
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
        read_plc_data(plc_ip, dbs, starts, lengths)
        # get_plc_data(plc_ip, rack, slot, dbs, starts, lengths, executor)
        end_time = datetime.now()
        # print(f"PLC {plc_ip} 数据采集完成,完成时间为：{end_time}\n", end='')
        print(f"PLC {plc_ip} 本次循环所用时间：{end_time - Start_time}\n", end='')
        sleep(0.1)


# 多线程执行数据采集
async def run_data_collection(plcs):
    # 创建外部线程池
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
