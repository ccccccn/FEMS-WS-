# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: shared_data.py
 @DateTime: 2025-02-10 16:19
 @SoftWare: PyCharm
"""
import asyncio
import os
import threading

import numpy as np

from taosPro.utils import JsonCache, file_data

cache = JsonCache()
cache_mqtt = JsonCache()
cache_mqtt_list = []
# TODO：修改飞轮舱数量
FLC_NUM = 9
collect_plcs = []
objs_bitmap = {}

soc_value = np.zeros(FLC_NUM)
frequency_value = np.zeros(FLC_NUM)
duration_value = np.zeros(FLC_NUM)
soc_hist = np.zeros(4)
frequency_hist = np.zeros(4)
duration_hist = np.zeros(4)
change_idx = np.zeros(FLC_NUM)
is_connect = np.random.randint(0, 2, size=FLC_NUM)

MQTT_TOPIC = "test"




def init_data():
    folder_path = "D:\\pycahrm\\taosPro\\datafile\\FLC_ALL_DATA"
    folder_path_mqtt = "D:\\pycahrm\\taosPro\\datafile\\MQTTTest"
    # breakpoint()
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"指定的文件夹路径不存在：{folder_path}")
    # folder_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "工具类", "FEMSjson文件")

    cache.load_from_dir(folder_path)

    cache_mqtt.load_from_dir(folder_path_mqtt)

    cache_mqtt_objs = cache_mqtt.cache.get("mqtt").get("Objs")
    # mqtt需转发数据变量名

    for obj_name in cache_mqtt_objs:
        cache_mqtt_list.extend([obj_name.get("N")])

    objs_bitmap.update({f"{mqtt}": 0 for mqtt in cache_mqtt_list})
    db, start, lengths = [], [], []
    for file_path in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_path)
        data = file_data(file_path)
        db.append(data['DB'])
        start.append(data['starts'])
        lengths.append(data['lengths'])
    base_config = {
        'rack': 0, 'slot': 1,
        'dbs': db, 'starts': start, 'lengths': lengths
    }

    ip_addresses = ['192.168.110.{}'.format(i) for i in range(1, FLC_NUM + 1)]  # 示例PLC IP地址
    collect_plcs.extend([{'ip': ip, **base_config} for ip in ip_addresses])
    """
    [{'ip': '192.168.110.1', 'rack': 0, 'slot': 1, 
    'dbs': [12, 18, 20, 24, 25, 33, 34, 41, 42, 5, 8], 
    'starts': [0, 0, 0, 136, 0, 72, 0, 2, 32, 124, 0], 
    'lengths': [344, 344, 344, 326, 102, 82, 160, 4040, 4544, 252, 344]},
     {'ip': '192.168.110.2', 'rack': 0, 'slot': 1, 
     'dbs': [12, 18, 20, 24, 25, 33, 34, 41, 42, 5, 8], 
     'starts': [0, 0, 0, 136, 0, 72, 0, 2, 32, 124, 0], 
     'lengths': [344, 344, 344, 326, 102, 82, 160, 4040, 4544, 252, 344]}]"""
