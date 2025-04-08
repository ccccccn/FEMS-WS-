# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: urls.py
 @DateTime: 2025-04-07 15:54
 @SoftWare: PyCharm
"""

from django.urls import path
from .views import IpadDataView

urlpatterns = [
    path('api/ipad_data/', IpadDataView.as_view(), name='ipad-data'),
]