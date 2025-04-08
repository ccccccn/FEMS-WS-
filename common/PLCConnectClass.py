# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: PLCConnectClass.py
 @DateTime: 2025-04-07 11:47
 @SoftWare: PyCharm
"""
import json
import logging
import threading
from collections import defaultdict
from datetime import datetime
import redis
import numpy as np
from snap7 import Client

from common.JsonCacheClass import get_data
from taos_capture.shared_data import cache_mqtt_list

lock = threading.Lock()

rr = redis.StrictRedis("localhost", 6379, 2, decode_responses=True, charset='UTF-8', encoding='UTF-8')


class PLCConnectClass:
    def __init__(self, plc, plc_ip, plc_rack, plc_slot):
        self.plc = Client()
        self.plc_ip = plc_ip
        self.plc_rack = plc_rack
        self.plc_slot = plc_slot

    def connect(self):
        self.plc.connect(self.plc_ip, self.plc_rack, self.plc_slot)
        logging.info(f"Connected to PLC{self.plc_ip}")

    def disconnect(self):
        self.plc.disconnect()
        logging.info(f"DisConnected to PLC{self.plc_ip}")

    def get_plc_data(self, plc, plc_ip, dbs, starts, lengths):
        data = defaultdict()
        rs = True
        # 将 DB 块分成两部分
        futures = []

        for db, start, length in zip(dbs, starts, lengths):
            if rs:
                data_list_parts, rs = self.read_plc_data(plc_ip, plc, db, length)
                data.update(data_list_parts)
            else:
                return False

        return data

    def read_plc_data(self, plc_ip, plc, db, length):
        data_dir = {}
        global change_idx, objs_bitmap
        try:
            ## 真实数据 一次性获取所有db下的值，顺序执行
            # data = plc.db_read(db, 0, length)
            ## 模拟测试数据
            try:
                data = plc.db_read(db, 0, length)
            except KeyboardInterrupt:
                return False
            except Exception as e:
                print(f"数据读取{e}")
                return False
            data_dir = self.parse_data(plc_ip, data, db)
        except Exception as e:
            print(f"aaa读取PLC数据错误：{e},{type(e)}")
            return None
        finally:
            return data_dir, True

    def parse_data(self, plc_ip, data, db):
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
                objs[f"{key}"] = {"1": value, "2": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"), "3": 192,
                                  "N": key}
                mqtt_data['objs'][key] = objs[f"{key}"]
        except Exception as e:
            print("here：", e)

        return data_dir
