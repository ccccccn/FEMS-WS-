# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: urls.py
 @DateTime: 2025-04-28 16:16
 @SoftWare: PyCharm
"""
from django.urls import path
from rest_framework.routers import SimpleRouter
from . import views
router = SimpleRouter()

urlpatterns = router.urls
urlpatterns = [
    path('/station_basic_info',views.station_basic_info,name='station_basic_info')

]