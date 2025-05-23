import json
from asyncio.log import logger
from datetime import timedelta

import numpy
import redis
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.shortcuts import render

# Create your views here.
# views.py
from django.http import JsonResponse
import random
import numpy as np
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django_celery_beat.models import ClockedSchedule, PeriodicTask
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser
from rest_framework.response import Response

from django.apps import apps
from rest_framework.views import APIView

CABIN_NUM = 20

soc_value = np.zeros(20)
frequency_value = np.zeros(20)
duration_value = np.zeros(20)
fw_redis_data = redis.StrictRedis("localhost", 6379, 2, decode_responses=True, charset='UTF-8', encoding='UTF-8')

## 使用redis作为中间件的channel传输数据
r = redis.StrictRedis(host='localhost', port=6379, db=1, socket_keepalive=-1)
p = r.pubsub()
p.subscribe('show_center')

"""
饼图视图
"""


class PieDataViewSet(viewsets.ModelViewSet):
    authentication_classes = []
    permission_classes = []

    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_queryset(self):
        PieDistribution = apps.get_model('showcenter', 'PieDistribution')
        queryset = PieDistribution.objects.all()
        pie_type = self.request.query_params.get('pie_type')
        analysis_type = self.request.query_params.get('analysis_type')
        """
        pie_type=[Soc_distribution,Fre_distribution,Drt_distribution]
        analysis_type=[day,month ,year]
        """
        if pie_type:
            queryset = queryset.filter(pie_type=pie_type)
        if analysis_type:
            queryset = queryset.filter(analysis_type=analysis_type)
        return queryset.order_by('analysis_time')

    @action(detail=False, methods=['get'], url_path='latest')
    def get_latest_record(self, request):
        queryset = self.get_queryset()
        instance = queryset.last()
        if not instance:
            return Response({'message': '未找到匹配记录'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(instance)
        logger.info(f"当前查询到的数据为：{serializer.data}")
        # return JsonResponse(json.dumps(serializer.data, ensure_ascii=False))
        return Response(serializer.data)

    def get_serializer_class(self):
        from .serializers import PieSerializer
        return PieSerializer


class RunningDataViewSet(viewsets.ModelViewSet):
    authentication_classes = []
    permission_classes = []

    parser_classes = []

    def get_queryset(self):
        RunningData = apps.get_model('showcenter', 'RunStatisticsData')
        query_set = RunningData.objects.all()
        return query_set.order_by()




"""
电站实时功率api
"""




    # return JsonResponse(play_data, json_dumps_params={"ensure_ascii": False})


@action(detail=False, methods=['get'], url_path='storage_station_information')
def storage_station_information(request, *args, **kwargs):
    data = json.loads(fw_redis_data.get('latest_fw_data')).get('flc_0')
    play_data = {
        "运行天数": data["FCCS_SOC"],
        "总充电量": data["Total_Device_Charged_Capacity_总充电量"],
        "总放电量": data["Total_Device_DisCharged_Capacity_总放电量"],
        "日充电量": data["Daily_Device_Charged_Capacity_日充电量"],
        "日放电量": data["Daily_Device_DisCharged_Capacity_日放电量"]
    }
    return JsonResponse(play_data, json_dumps_params={"ensure_ascii": False})
    # def send_to_redis_channel(channel_name, CABIN_NUM=20):


