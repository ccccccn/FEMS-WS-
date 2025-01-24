import json
from asyncio.log import logger

import redis
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.shortcuts import render

# Create your views here.
# views.py
from django.http import JsonResponse
import random
import numpy as np

CABIN_NUM = 20


soc_value = np.zeros(20)
frequency_value = np.zeros(20)
duration_value = np.zeros(20)
soc_bins = np.linspace(-100,100,5)
# soc_value = np.array([random.randint(-100, 100) for _ in range(20)])
# frequency_value = np.array([random.randint(-100, 100) for _ in range(20)])
# duration_value = np.array([random.randint(-100, 100) for _ in range(20)])
# soc_bins = np.arange(-100, 101, 20)


def get_frequency_data(request):
    data = {
        "title": "frequency",
        "message": {
            "0-15": random.randint(10, 100),
            "15-30": random.randint(10, 100),
            "30-50": random.randint(10, 100),
            "50-100": random.randint(10, 100)
        }
    }
    return JsonResponse(data)


## 使用redis作为中间件的channel传输数据
r = redis.StrictRedis(host='localhost', port=6379, db=0)
p = r.pubsub()
p.subscribe('show_center')


# def send_to_redis_channel(channel_name):
#     random_idx = random.randint(0, 19)
#     random_value = random.randint(-100, 100)
#     soc_value[random_idx] = random_value
#     hist, bin_edges = np.histogram(soc_value, bins=soc_bins)
#     hist_json_str = json.dumps((hist / CABIN_NUM).tolist())
#     hist_json = json.loads(hist_json_str)
#     data = {
#         "title": "soc",
#         "message": {
#             "value": hist_json
#         }
#     }
#     """
#     向 Redis 的指定 channel 发送数据。
#     :param channel_name: Redis channel 的名称
#     :param data: 要发送的数据（通常是字典或字符串）
#     """
#     try:
#         # 如果数据是字典，可以将其转换为 JSON 格式
#         if isinstance(data, dict):
#             data = json.dumps(data)
#
#         # 发送数据到指定的 channel
#         r.publish(channel_name, data)
#         print(f"Data sent to channel '{channel_name}': {data}")
#         # 设置退出条件
#     except Exception as e:
#         print(f"Error sending data to Redis channel: {e}")
def send_to_redis_channel(channel_name, CABIN_NUM=20):
    random_idx_arr = [random.randint(0, 19) for _ in range(3)]
    random_value_arr = [random.randint(-100, 100) for _ in range(3)]

    cnt = 0
    for idx, value in zip(random_idx_arr, random_value_arr):
        if cnt == 0:
            soc_value[idx] = value
        if cnt == 1:
            frequency_value[idx] = value
        if cnt == 2:
            duration_value[idx] = value
        cnt += 1

    soc_hist, bin_edges = np.histogram(soc_value, bins=soc_bins)
    frequency_hist, bin_edges = np.histogram(frequency_value, bins=soc_bins)
    duration_hist, bin_edges = np.histogram(duration_value, bins=soc_bins)
    data = {
        "title": "pie_info",
        "message": {
            "soc": (soc_hist/CABIN_NUM*100).tolist(),
            "frequency":(frequency_hist/CABIN_NUM*100).tolist(),
            "duration": (duration_hist/CABIN_NUM*100).tolist(),
        }
    }
    """
    向 Redis 的指定 channel 发送数据。
    :param channel_name: Redis channel 的名称
    :param data: 要发送的数据（通常是字典或字符串）
    """
    try:
        # 如果数据是字典，可以将其转换为 JSON 格式
        if isinstance(data, dict):
            data = json.dumps(data)

        # 发送数据到指定的 channel
        r.publish(channel_name, data)
        print(f"Data sent to channel '{channel_name}': {data}")
        # 设置退出条件
    except Exception as e:
        print(f"Error sending data to Redis channel: {e}")

## api轮训数据
def get_soc_data(request):
    random_idx = random.randint(0, 19)
    random_value = random.randint(-100, 100)
    soc_value[random_idx] = random_value
    hist, bin_edges = np.histogram(soc_value, bins=soc_bins)
    hist_json_str = json.dumps((hist / CABIN_NUM).tolist())
    hist_json = json.loads(hist_json_str)
    data = {
        "title": "soc",
        "message": {
            "value": hist_json
        }
    }
    return JsonResponse(data)


def get_rack_data(request):
    data = {
        "title": "rack",
        "message": {
            "rack1": random.randint(10, 100),
            "rack2": random.randint(10, 100),
            "rack3": random.randint(10, 100)
        }
    }
    print(json.dumps(data))
    return JsonResponse(data)
