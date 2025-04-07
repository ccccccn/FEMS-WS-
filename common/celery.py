# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: celery.py
 @DateTime: 2025-02-25 15:35
 @SoftWare: PyCharm
"""

import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taosPro.settings')
app = Celery('taosPro', enable_utc=True)
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()  # 支持新型任务发现机制




