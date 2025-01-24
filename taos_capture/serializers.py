# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: serializers.py
 @DateTime: 2024-12-23 15:32
 @SoftWare: PyCharm
"""

from rest_framework import serializers
from .models import WeiboHotPointSearch

class MyModelSerializer(serializers.ModelSerializer):
    class Mete:
        model = WeiboHotPointSearch
        fields = '__all__'