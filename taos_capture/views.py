import asyncio
import copy
import json
import logging
import random
from time import sleep

import redis
import schedule
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.

import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import numpy as np
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from snap7.client import Client
from sortedcontainers import SortedList

from common.celery import app
from mqttserver.mqtt_CLi import forward_data
from .Collector_controller import start_collect, stop_collect, reset_collect
from .models import plc_connection_status
from showcenter.views import send_to_redis_channel
from taosPro.utils import get_data, file_data, JsonCache
from .shared_data import cache, FLC_NUM, collect_plcs, soc_value, frequency_value, duration_value, \
    soc_hist, frequency_hist, duration_hist, change_idx, cache_mqtt, cache_mqtt_list, MQTT_TOPIC, objs_bitmap

lock = threading.Lock()
mqtt_data = {"PNs": {
    "1": "V",
    "2": "T",
    "3": "Q"
}, "objs": {}}

rr = redis.StrictRedis("localhost", 6379, 2, decode_responses=True, charset='UTF-8', encoding='UTF-8')
redis_cache = redis.StrictRedis("localhost", 6379, 2, decode_responses=True, charset='UTF-8', encoding='UTF-8')
redis_data = redis.StrictRedis("localhost", 6379, 3, decode_responses=True, charset='UTF-8', encoding='UTF-8')


# try:
#     flc_data = json.loads(rr.get("flc_data"))
#     if flc_data is None:
#         logging.info("No flc_data")
# except Exception as e:
#     print(e)


# 数据解析示例
def parse_data(plc_ip, data, db):
    # print(f"flcdata:{flc_data.get('DBDB5')}")
    # global soc_value, frequency_value, duration_value, soc_hist, frequency_hist, duration_hist
    global objs_bitmap, mqtt_data
    flc_num = str(plc_ip.split('.')[-1])
    objs = {}
    # print(f"当前解析ip为{plc_ip},飞轮舱号为{flc_num}\n", end='')
    # 解析并处理数据
    data_dir = {}
    cache_data = rr.get(f'DB{db}', )
    cache_data = json.loads(cache_data)
    item_num = len(cache_data)
    for key in cache_data:
        cache_adata = cache_data[key]
        # key = key.replace("飞轮舱1", f"飞轮舱{flc_num}")
        value = round(get_data(cache_adata, data), 3)
        data_dir[key] = value
        try:
            if key in cache_mqtt_list:
                objs[f"{key}"] = {"1": value, "2": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"), "3": 192, "N": key}
                mqtt_data['objs'][key] = objs[f"{key}"]
        except Exception as e:
            print("here：", e)

    return data_dir
    # print(f"当前{flc_num}DB{db}块解析结束时间为：{datetime.now()}\n", end='')


# PLC数据采集任务
def read_plc_data(plc_ip, plc, dbs, lengths):
    data_dir = {}
    start_time = datetime.now()
    global s_soc_hist, s_frequency_hist, s_duration_hist, change_idx, objs_bitmap
    try:
        ## 真实数据 一次性获取所有db下的值，顺序执行
        # data = plc.db_read(db, 0, length)
        ## 模拟测试数据
        try:
            data = plc.db_read(dbs, 0, lengths)
        except KeyboardInterrupt:
            return False
        except Exception as e:
            print(f"数据读取{e}")
            return False
        data_dir = parse_data(plc_ip, data, dbs)
        # print(data_list)
        # for db, length in zip(dbs, lengths):
        #     # data_list = parse_data(plc_ip, data, db)
        #     # 数据模拟
        #     # random_data = bytearray(random.randint(0, 100) for _ in range(length))
        #     s_soc_hist, s_frequency_hist, s_duration_hist, data_list = parse_data(plc_ip, data, db)
        # print(type(s_soc_hist), type(frequency_hist), type(duration_hist))
        # try:
        #     # change_idx[int(plc_ip.split('.')[-1]) - 1] = 1
        # except Exception as e:
        #     print("心跳机制错误：",e)
        #     pass
        # # TODO:数据转发至首页
        try:
            if np.any(plc_connection_status.connected):
                print("当前连接状态修改为:", plc_connection_status.connected)
                lock.acquire()
                try:
                    if np.all(plc_connection_status.connected.astype(bool) & change_idx.astype(
                            bool) == plc_connection_status.connected):
                        send_to_redis_channel("show_center", FLC_NUM,
                                              s_soc_hist, s_frequency_hist, s_duration_hist)
                        # logging.info(f"Data sent to channel show_center")
                        print(f"匹配成功，并发送数据,当前发送时间为{datetime.now()}")
                        change_idx = np.zeros(FLC_NUM)
                finally:
                    lock.release()
        except Exception as e:
            print(f"{type(e)}here:{e}")
    except Exception as e:
        print(f"aaa读取PLC数据错误：{e},{type(e)}")
        return None
    finally:
        return data_dir, True

    # 采集每个PLC数据


def get_plc_data(plc, plc_ip, plc_rack, plc_slot, dbs, starts, lengths, executor):
    fw_data_redis_dir = defaultdict()
    rs = True
    # 将 DB 块分成两部分
    dbs_plc = dbs  # 前 5 个 DB 块由 plc 处理
    starts_plc = starts
    lengths_plc = lengths
    # 使用线程池执行读取任务
    for_time = datetime.now()
    futures = []
    Start_time = datetime.now()
    # 使用 plc 处理前 5 个 DB 块=
    for db, start, length in zip(dbs_plc, starts_plc, lengths_plc):
        for_time = datetime.now()
        if rs:
            data_list_parts, rs = read_plc_data(plc_ip, plc, db, length)
            fw_data_redis_dir.update(data_list_parts)
        else:
            return False
        # print(f"当前循环时间：{datetime.now()}")
    try:
        data_list = json.dumps(fw_data_redis_dir, ensure_ascii=False)
        if int(plc_ip.split('.')[-1], 10) > 20:
            redis_data.set("fccs", data_list)
            # print(f"{data_list}--{datetime.now()}")
        else:
            redis_data.set(f"飞轮舱{plc_ip.split('.')[-1]}", data_list)
            # print(f"写入成功！--{datetime.now()}")
    except ValueError as e:
        print(f"写入缓存出错：{e}")
    except Exception as e:
        print(f"其他错误:{e}")
    #     future = executor.submit(read_plc_data, plc_ip, plc, db, length)
    #     futures.append(future)
    # for future in as_completed(futures):
    #     # 等待所有任务完成
    #     future.result()  # 等待每个任务的结果，触发异常时会被捕获
    end_time = datetime.now()
    # print(f"PLC{plc_ip}本次采集所用：{end_time - Start_time}\n", end='')
    return True


# 外部线程负责管理每个PLC设备
def plc_thread(plc_ip, rack, slot, dbs, starts, lengths, executor):
    # 每个外部线程负责不断地进行数据采集
    while True:
        Start_time = datetime.now()
        # print(f"PLC {plc_ip} 数据采集开始于：{Start_time}\n", end='')
        # read_plc_data(plc_ip, dbs, lengths)
        """
        python深浅拷贝不同:
            深拷贝为重新开辟一片内存空间，完全一样的复制一份        
            浅拷贝仅仅为重新定义一个对象，类似软连接
        """
        data = copy.deepcopy(mqtt_data)
        data['objs'] = list(data['objs'].values())
        data = json.dumps(data, ensure_ascii=False)
        redis_cache.set("mqtt_data", data)
        # print(f"{str(plc_ip.split('.')[-1])}循环结束当前mqtt_data:{mqtt_data}")
        plc = Client()
        try:
            plc.connect(plc_ip, rack, slot)
        except Exception as e:
            print(f"数据捕捉——连接PLC失败: {e}")
            return
        if plc.get_connected():
            print(f"PLC {plc_ip} 连接成功--{datetime.now()}")
            while True:
                rc = get_plc_data(plc, plc_ip, rack, slot, dbs, starts, lengths, executor)
                try:
                    if rc is False:
                        max_retries = 30
                        retries = 0
                        while retries < max_retries:
                            plc.connect(plc_ip, rack, slot)
                            if plc.get_connected():
                                print("连接成功")
                            else:
                                print(f"连接失败，尝试重连...（{retries + 1}/{max_retries}）")
                                retries += 1
                                sleep(1)  # 等待一段时间后重试
                        print("重连失败，已达最大重试次数")
                        return False
                except Exception as e:
                    print(f"plcConnect Error：{e}")
        end_time = datetime.now()
        # print(f"PLC {plc_ip} 数据采集完成,完成时间为：{end_time}\n", end='')
        print(f"PLC {plc_ip} 本次循环所用时间：{end_time - Start_time}\n", end='')
        sleep(5)


# 多线程执行数据采集
async def run_data_collection(plcs):
    # 创建外部线程池
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor(max_workers=FLC_NUM + 1) as executor:  # 外部线程池，最大同时处理5个PLC
        threads = []

        for plc in plcs:
            thread = loop.run_in_executor(executor, plc_thread,
                                          plc['ip'], plc['rack'], plc['slot'], plc['dbs'], plc['starts'],
                                          plc['lengths'], executor)
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
        # is_connect[int(plc['ip'].split("_")[-1]) - 1] = random.randint(0, 2)
        plc = Client()
        plc.connect(plc["ip"], plc["rack"], plc['slot'])
        if plc.get_connected():
            is_connect[int(plc['ip'].split("_")[-1]) - 1] = 1
        else:
            is_connect[int(plc['ip'].split("_")[-1]) - 1] = 0
        await asyncio.sleep(1)
    pass


async def data_capture_main():
    try:
        # breakpoint()
        await run_data_collection(collect_plcs)
    except KeyboardInterrupt:
        print("采集任务已终止")


"""
-------------------------api路由分割线------------------------
"""


@csrf_exempt
def start_collect_view(request):
    if request.method == 'POST':
        start_collect()
        return JsonResponse({'status': "started!"})


@csrf_exempt
def stop_collect_view(request):
    if request.method == 'POST':
        stop_collect()
        return JsonResponse({'status': "stop!"})


@csrf_exempt
def reset_collect_view(request):
    if request.method == 'POST':
        reset_collect()
        return JsonResponse({'status': "reset!"})
