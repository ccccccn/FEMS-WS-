# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: urls.py
 @DateTime: 2025-05-08 16:11
 @SoftWare: PyCharm
"""

from django.urls import path, include
from . import views

urlpatterns = [
    path('/FW_overview', views.systemParamsView)
]
"""
系统参数页面实时传输已ws方式转送，连接分别为：
总览：ws://192.168.97.125:10002/ws/?group=systemParamsOverview
详情：ws://192.168.97.125:10002/ws/?group=systemParamsDetail
"""