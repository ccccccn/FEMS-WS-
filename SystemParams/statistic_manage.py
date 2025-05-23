# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: statistic_manage.py
 @DateTime: 2025-05-22 15:44
 @SoftWare: PyCharm
"""

import json
from django_redis import get_redis_connection


class CenterManager():
    def __init__(self):
        self.conn = get_redis_connection('defaults')

