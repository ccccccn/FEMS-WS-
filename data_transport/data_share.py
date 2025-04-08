# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: data_share.py
 @DateTime: 2025-02-12 14:00
 @SoftWare: PyCharm
"""

# 数据初始化处理，本地IPad缓存
import os

from taosPro.utils import JsonCache, file_data

# 获取当前45台测试飞轮变量偏移量
cache = JsonCache()
folder_path = 'D:\\pycahrm\\taosPro\\datafile\\IPad_DATA'
if not os.path.exists(folder_path):
    print("当前访问文件夹不存在")

cache.load_from_dir(folder_path)

file_list = os.listdir(folder_path)
if len(file_list) == 0:
    print("当前文件夹下无分布数据")

db, start, lengths = [], [], []
for file_path in file_list:
    file_path = os.path.join(folder_path, file_path)
    data = file_data(file_path)
    db.append(data['DB'])
    start.append(data['starts'])
    lengths.append(data['lengths'])

base_config = {
    'rack': 0, 'slot': 1,
    'dbs': db, 'starts': start, 'lengths': lengths
}
# TODO:修改飞轮舱ip
ip_addresses = ['192.168.100.25']  # 示例PLC IP地址
collect_plcs = [{'ip': ip, **base_config} for ip in ip_addresses]
