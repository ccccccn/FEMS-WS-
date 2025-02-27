# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: utils.py
 @DateTime: 2025-02-24 11:14
 @SoftWare: PyCharm
"""
import paho.mqtt.client as mqtt

from taos_capture.data_migration.CreateTableTest import getconnect


# def init_mqtt_client():
#     client = mqtt.Client()
#     client.connect("localhost", 1883, keepalive=60)
#     return client

def init__tdengine_connection():
    return getconnect()

