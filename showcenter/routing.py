# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: routing.py
 @DateTime: 2025-01-15 15:21
 @SoftWare: PyCharm
"""

from django.urls import path, re_path
from . import consumer

websocket_urlpatterns = [
    path('ws/', consumer.MyConsumer.as_asgi()),
]
