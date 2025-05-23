import json
import logging
from copy import deepcopy
from datetime import datetime
from operator import itemgetter

from apscheduler.schedulers.background import BackgroundScheduler
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
from django_apscheduler.jobstores import DjangoJobStore
from rest_framework.decorators import action
from .tasks import HeartBeat
import redis
from .state_manage import StateManage
from .models import EnergyManageRank

state_manager = StateManage()
logger = logging.getLogger(__name__)
# Create your views here.


fw_all_data_redis = redis.StrictRedis("localhost", 6379, 2,
                                      decode_responses=True, charset='UTF-8', encoding='UTF-8')
redis_fw = redis.StrictRedis('localhost', 6379, 4)


@action(detail=False, methods=['get'], url_path='station_basic_info')
def station_basic_info(request, *args, **kwargs):
    try:
        OnlineNum = HeartBeat()
        OnlineNumDict = {"OnlineNum": OnlineNum}
        return JsonResponse(OnlineNumDict, safe=True, json_dumps_params={"ensure_ascii": False})
    except Exception as e:
        return JsonResponse({'message': {e}}, ensure_ascii=False)


@action(['get'], False, 'energy_rank', 'energy_rank')
def get_current_rank_data(request):
    rank_data = state_manager.get_rank_data()
    print(f"查询到的rank_data:{rank_data}")
    return JsonResponse({
        "data": list(rank_data.values())
    }, safe=False, json_dumps_params={"ensure_ascii": False})



