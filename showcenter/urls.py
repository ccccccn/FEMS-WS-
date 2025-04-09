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
    path('showcenter/', include(router.urls)),
    # path('api/rack/', views.get_rack_data, name='rack-data'),
    # path('piedata/<str:pie>', views.get_rack_data, name='showcenter_piedata')
]
