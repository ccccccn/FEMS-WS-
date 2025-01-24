# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: utils.py
 @DateTime: 2025-01-22 16:48
 @SoftWare: PyCharm
"""
import time

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def send_message_to_redis(channel_name, msg):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.groups_send)(
        channel_name,
        {
            "type":"update_message",
            "message":msg,
        }
    )


## 函数性能时间计算装饰器
def cost_time(func):
    def wrapper(*args, **kwargs):
        t = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"当前方法 {func.__name__} cost time {time.perf_counter() - t:.8f}s")
        return result
    return wrapper