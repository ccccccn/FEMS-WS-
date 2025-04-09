import json
from asyncio.log import logger

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
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser
from rest_framework.response import Response

from showcenter import apps

CABIN_NUM = 20

soc_value = np.zeros(20)
frequency_value = np.zeros(20)
duration_value = np.zeros(20)
fw_redis_data = redis.StrictRedis("localhost", 6379, 4, decode_responses=True, charset='UTF-8', encoding='UTF-8')

## 使用redis作为中间件的channel传输数据
r = redis.StrictRedis(host='localhost', port=6379, db=1, socket_keepalive=-1)
p = r.pubsub()
p.subscribe('show_center')


class PieDataViewSet(viewsets.ModelViewSet):
    authentication_classes = []
    permission_classes = []

    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_queryset(self):
        PieDistribution = apps.get_model('showcenter', 'PieDistribution')
        queryset = PieDistribution.objects.all()
        pie_type = self.request.query_params.get('pie_type')
        analysis_type = self.request.query_params.get('analysis_type')
        if pie_type:
            queryset = queryset.filter(pie_type=pie_type)
        if analysis_type:
            queryset = queryset.filter(analysis_type=analysis_type)
        return queryset.order_by('-analysis_time')

    @action(detail=False, methods=['get'], url_path='latest')
    def get_latest_record(self, request):
        queryset = self.get_queryset()
        instance = queryset.first()
        if not instance:
            return Response({'message': '未找到匹配记录'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer_class()
        return Response(serializer.data)

    def get_serializer_class(self):
        from .serializers import PieSerializer
        return PieSerializer


# def send_to_redis_channel(channel_name, CABIN_NUM=20):
def send_to_redis_channel(channel_name, CABIN_NUM=20):
    global soc_value, frequency_value, duration_value
    soc_hist, frequency_hist, duration_hist = [], [], []

    ## data_hist输出结果为各分区中个数
    def center_data_deal(data_value, data_name, fw_number, partiton):
        data_value[fw_number - 1] = fw_data[data_name]
        data_bin = np.linspace(0, 100, partiton)
        data_hist, data_edges = np.histogram(data_value, bins=data_bin)
        return data_hist

    for i in range(1, CABIN_NUM + 1):
        fw_data = json.loads(fw_redis_data.get(f"飞轮舱{i}"))
        soc_hist = center_data_deal(soc_value, f"飞轮舱{i}_EMS_SYS_SOC", i, 5)
        frequency_hist = center_data_deal(soc_value, f"飞轮舱{i}_EMS_SYS_FREQUENCY", i, 5)
        duration_hist = center_data_deal(soc_value, f"飞轮舱{i}_EMS_SYS_DURATION", i, 5)

    data = {
        "title": "pie_info",
        "message": {
            "soc": (soc_hist / CABIN_NUM * 100).astype(int).tolist(),
            "frequency": (frequency_hist / CABIN_NUM * 100).astype(int).tolist(),
            "duration": (duration_hist / CABIN_NUM * 100).astype(int).tolist(),
        }
    }
    """
    向 Redis 的指定 channel 发送数据。
    :param channel_name: Redis channel 的名称
    :param data: 要发送的数据（通常是字典或字符串）
    """
    try:
        # 如果数据是字典，可以将其转换为 JSON 格式
        if isinstance(data, dict):
            data = json.dumps(data)

        # 发送数据到指定的 channel
        r.publish(channel_name, data)
        # print(f"Data sent to channel '{channel_name}': {data}\n", end='')
        # 设置退出条件
    except Exception as e:
        print(f"Error sending data to Redis channel: {e}")


## api轮训数据
def get_rack_data(request):
    data = {
        "title": "rack",
        "message": {
            "rack1": random.randint(10, 100),
            "rack2": random.randint(10, 100),
            "rack3": random.randint(10, 100)
        }
    }
    print(json.dumps(data))
    return JsonResponse(data)
