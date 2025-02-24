# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: urls.py
 @DateTime: 2025-01-21 15:00
 @SoftWare: PyCharm
"""
# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('api/frequency/', views.get_frequency_data, name='frequency-data'),
    path('api/soc/', views.get_soc_data, name='soc-data'),
    path('api/rack/', views.get_rack_data, name='rack-data'),
]