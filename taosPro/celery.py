# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: celery.py
 @DateTime: 2025-01-22 8:47
 @SoftWare: PyCharm
"""
import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taosPro.settings')
app = Celery('taosPro')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))