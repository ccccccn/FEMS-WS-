# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: AllDataMock.py
 @DateTime: 2025-05-06 14:33
 @SoftWare: PyCharm
"""
import datetime
import json
import logging
import os
import random
import threading
from venv import logger

import time
from itertools import islice

import redis
from apscheduler.schedulers.background import BackgroundScheduler

from common.JsonCacheClass import JsonCache, file_take, type_mapper
import taos

from common.KafkaProducer import plc_data_producer

redis_fems = redis.StrictRedis('localhost', 6379, 2,
                               charset='utf-8', decode_responses=True, encoding='utf-8')
data_lock = threading.Lock()
all_data_dict = {}
cache = JsonCache()
file_path = 'D:\pycahrm\\taosPro\datafile\FLC_ALL_DATA'
cache.load_from_dir(file_path)
flc_point = cache.cache.get("DBDB12")
for k, v in cache.cache.items():
    flc_point = k[2:]
    if not redis_fems.get(flc_point):
        redis_fems.set(flc_point, json.dumps(v, ensure_ascii=False))
    else:
        continue
print("数据缓存生成")
conn = taos.connect('localhost', 'root', 'taosdata', 6031)
conn.select_db('test')
tcur = conn.cursor()
create_sql = "CREATE TABLE IF NOT EXISTS `fems_data` (`ts` TIMESTAMP, "
type_map = {
    "SHORT": "INT",
    "USHORT": "INT UNSIGNED",
    "LONG": "BIGINT",
    "BIT": "BOOL"
}
type_random = {
    "SHORT": lambda: random.randint(-100, 100),
    "USHORT": lambda: random.randint(0, 100),
    "LONG": lambda: random.randint(-10000, 100000),
    "BIT": lambda: random.choice([False, True]),
    "FLOAT": lambda: round(random.uniform(0, 100), 2)
}

keys = []
fields = []
for key in redis_fems.keys():
    if key.startswith("DB"):
        keys.append(key)
        for k, v in json.loads(redis_fems.get(key)).items():
            sql_type = type_map.get(v["Type"], "FLOAT")  # 默认为 FLOAT
            fields.append(f"`{k}` {sql_type}")
create_sql = f"CREATE TABLE if not exists all_flc_fems (`ts` timestamp,{', '.join(fields)}) TAGS (groupid INT)"


def publish_data():
    if all_data_dict:
        # 获取前两个数据项
        test_data = dict(all_data_dict.items())
        # 将数据转换为JSON字符串
        test_data_json = json.dumps(test_data, ensure_ascii=False)
        # 发布数据
        # redis_fems.publish("all_fw_data", test_data_json)
        redis_fems.set("latest_fw_data", test_data_json)
        # print("最新飞轮数据已缓存至redis-db2")
        # 输出日志
        # print(f"{datetime.datetime.now()} 已发布数据")


def start_publish_scheduler():
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(publish_data, 'interval', seconds=10, max_instances=1)
    scheduler.start()


def main():
    start_publish_scheduler()
    tbnames = []
    for i in range(1, 51):
        tbnames.append(f'fems_all_flc{i}')
    while True:
        data_dict = {}
        cnt = 0
        for i in range(len(keys)):
            for key, value in json.loads(redis_fems.get(keys[i])).items():
                generator = type_random.get(value['Type'], lambda: None)
                data_dict[key] = generator()
                cnt += 1
        start_time = datetime.datetime.now()
        tbname = random.choice(tbnames)
        index = list.index(tbnames, tbname)
        all_data_dict[f"飞轮舱{index}"] = data_dict
        # Redis 设置缓存，60 秒过期
        # if datetime.datetime.now().second == 0:
        #     redis_fems.set(f"latest:飞轮舱{index}", json.dumps(data_dict, ensure_ascii=False), ex=60)
        #
        # print(f"[{datetime.datetime.now()}] 发布到 Kafka 分区 (key=飞轮舱{index})，并写入 Redis")
        time.sleep(0.1)


if __name__ == "__main__":
    main()

# print(create_sql)
# conn.execute(create_sql)
# print("成功建立超级标记表")
# tcur.close()
# conn.close()
