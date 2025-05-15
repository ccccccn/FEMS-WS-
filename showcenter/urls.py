# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: urls.py
 @DateTime: 2025-01-21 15:00
 @SoftWare: PyCharm
"""
# urls.py
from django.urls import path, include
from rest_framework import routers

from . import views
from .views import PieDataViewSet

router = routers.DefaultRouter()
router.register(r'pie_data', PieDataViewSet, basename='pie_data')

urlpatterns = [
    path('', include(router.urls)),
    path('current_data_play', views.current_data_play_by_redis, name='station_data'),
    path("storage_station_info", views.storage_station_information, name="storage_station_info")
]
