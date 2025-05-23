# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: serializers.py
 @DateTime: 2025-04-09 14:36
 @SoftWare: PyCharm
"""
from rest_framework import serializers

from showcenter.models import PieDistribution, RunStatisticsData


class PieSerializer(serializers.ModelSerializer):

    class Meta:
        model = PieDistribution

        fields = '__all__'

        def validate_fun(self, value):
            if value > 100:
                raise serializers.ValidationError("占比不可超过100%")
            return value



class RunStatisticsDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = RunStatisticsData

        fields = '__all__'
