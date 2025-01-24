# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: urls.py
 @DateTime: 2024-12-23 15:41
 @SoftWare: PyCharm
"""

# 在 urls.py 中定义 API 路由
from django.urls import path
from . import views
from rest_framework.routers import SimpleRouter
from .views import MyModelListCreate

router = SimpleRouter()

router.register('messages', MyModelListCreate, basename='messages')

urlpatterns = router.urls
urlpatterns = [
    path("index", views.index, name='index'),
    path("", views.home, name='home'),
    path("data_capture/", views.DataCapturePage, name='data_capture'),
    path("pause_capture/", views.pause_data_collection, name='pause_capture')
]
