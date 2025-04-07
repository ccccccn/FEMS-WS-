import json
from asyncio.log import logger

import numpy
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
fw_redis_data = redis.StrictRedis("localhost", 6379, 4, decode_responses=True, charset='UTF-8', encoding='UTF-8')

## 使用redis作为中间件的channel传输数据
r = redis.StrictRedis(host='localhost', port=6379, db=1, socket_keepalive=-1)
p = r.pubsub()
p.subscribe('show_center')


# def send_to_redis_channel(channel_name, CABIN_NUM=20):
def send_to_redis_channel(channel_name, CABIN_NUM=20):
    global soc_value, frequency_value, duration_value
    soc_hist, frequency_hist, duration_hist = [], [], []

    ## data_hist输出结果为各分区中个数
    def center_data_deal(data_value, data_name, fw_number, partiton):
        data_value[fw_number] = fw_data[data_name]
        data_bin = np.linspace(0, 100, partiton)
        data_hist, data_edges = np.histogram(data_value, bins=data_bin)
        return data_hist

    for i in range(1, CABIN_NUM + 1):
        fw_data = fw_redis_data.get(f"飞轮舱{i}")
        soc_hist = center_data_deal(soc_value, f"飞轮舱{i}_EMS_SYS_SOC", i, 5)
        frequency_hist = center_data_deal(soc_value, f"飞轮舱{i}_EMS_SYS_FREQUENCY", i, 5)
        duration_hist = center_data_deal(soc_value, f"飞轮舱{i}_EMS_SYS_DURATION", i, 5)

    data = {
        "title": "pie_info",
        "message": {
            "soc": (soc_hist / CABIN_NUM * 100).astype(int).tolist(),
            "frequency": (frequency_hist / CABIN_NUM * 100).astype(int).tolist(),
            "duration": (duration_hist / CABIN_NUM * 100).astype(int).tolist(),
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
        # print(f"Data sent to channel '{channel_name}': {data}\n", end='')
        # 设置退出条件
    except Exception as e:
        print(f"Error sending data to Redis channel: {e}")


## api轮训数据
# def get_soc_data(request):
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
#     return JsonResponse(data)


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
