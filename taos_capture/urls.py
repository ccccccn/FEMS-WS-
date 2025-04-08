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

router = SimpleRouter()


urlpatterns = router.urls
urlpatterns = [
    path('/SystemManagement/start_collect', views.start_collect_view),
    path('/SystemManagement/stop_collect', views.stop_collect_view),
    path('/SystemManagement/reset_collect', views.reset_collect_view)
]
