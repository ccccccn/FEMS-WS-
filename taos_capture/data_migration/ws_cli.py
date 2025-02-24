# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: ws_cli.py
 @DateTime: 2025-01-21 9:18
 @SoftWare: PyCharm
"""
import asyncio
import time
import random

import websockets
import json

from celery.schedules import schedule


# async def send_data():
#     uri = "ws://192.168.102.75:8044/ws/ShowCenter"
#     random_arr = [random.randint(10,100) for _ in range(4)]
#     async with websockets.connect(uri) as ws:
#         message = {
#             "title": "frequency",
#             "message": {
#                 "0-15": random_arr[0],
#                 "15-30": random_arr[1],
#                 "30-50": random_arr[2],
#                 "50-100": random_arr[3]
#             }
#         }
#         await ws.send(json.dumps(message))
#         print(f"Sent message: {message}")

