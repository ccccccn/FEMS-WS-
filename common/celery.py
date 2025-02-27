# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: celery.py
 @DateTime: 2025-02-25 15:35
 @SoftWare: PyCharm
"""
import json
import os
import random
from datetime import datetime

import redis
from celery import Celery
from celery.schedules import crontab

from taosPro import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taosPro.settings')
app = Celery('taosPro', enable_utc=True)
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)  # 支持新型任务发现机制

redis = redis.StrictRedis(host='localhost', port=6379, db=2, socket_keepalive=10)



