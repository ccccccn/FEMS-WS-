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


folder_path = "D:\\pycahrm\\taosPro\\datafile"
# breakpoint()
if not os.path.exists(folder_path):
    raise FileNotFoundError(f"指定的文件夹路径不存在：{folder_path}")
# folder_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "工具类", "FEMSjson文件")
cache = JsonCache()
cache.load_from_dir(folder_path)
# TODO：修改飞轮舱数量
FLC_NUM = 2

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
collect_plcs = [{'ip': ip, **base_config} for ip in ip_addresses]
"""
[{'ip': '192.168.110.1', 'rack': 0, 'slot': 1, 
'dbs': [12, 18, 20, 24, 25, 33, 34, 41, 42, 5, 8], 
'starts': [0, 0, 0, 136, 0, 72, 0, 2, 32, 124, 0], 
'lengths': [344, 344, 344, 326, 102, 82, 160, 4040, 4544, 252, 344]},
 {'ip': '192.168.110.2', 'rack': 0, 'slot': 1, 
 'dbs': [12, 18, 20, 24, 25, 33, 34, 41, 42, 5, 8], 
 'starts': [0, 0, 0, 136, 0, 72, 0, 2, 32, 124, 0], 
 'lengths': [344, 344, 344, 326, 102, 82, 160, 4040, 4544, 252, 344]}]"""

soc_value = np.zeros(FLC_NUM)
frequency_value = np.zeros(FLC_NUM)
duration_value = np.zeros(FLC_NUM)
soc_hist = np.zeros(4)
frequency_hist = np.zeros(4)
duration_hist = np.zeros(4)
change_idx = np.zeros(FLC_NUM)
is_connect = np.random.randint(0, 2, size=FLC_NUM)

is_connected_data = np.zeros(FLC_NUM)
is_connected_lock = threading.Lock

async def update_is_connected(new_data):
    with is_connected_lock:
        global is_connected_data
        is_connected_data = new_data
        await asyncio.sleep(1)

def get_is_connected():
    with is_connected_lock:
        return is_connected_data
