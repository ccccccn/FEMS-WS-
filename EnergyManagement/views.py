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
from .Energy_task import HeartBeat
import redis
from . import state_manage
from .models import EnergyManageRank

logger = logging.getLogger(__name__)
# Create your views here.


fw_all_data_redis = redis.StrictRedis("localhost", 6379, 2,
                                      decode_responses=True, charset='UTF-8', encoding='UTF-8')
redis_fw = redis.StrictRedis('localhost', 6379, 4)


@action(detail=False, methods=['get'], url_path='station_basic_info')
def station_basic_info(request, *args, **kwargs):
    try:
        OnlineNum = HeartBeat()
        return JsonResponse(json.dumps(OnlineNum), ensure_ascii=False)
    except Exception as e:
        return JsonResponse({'error': f'{e}', 'message': {e.message}}, ensure_ascii=False)


def usage_status(request, *args, **kwargs):
    data = redis_fw.get('fccs')
    # response_data = [
    #     "场站SOC":
    #
    # ]


def get_top5(data, key):
    top5 = sorted(data, key=itemgetter(key), reverse=True)[:5]
    return top5


@action(['get'], False, 'energy_rank', 'energy_rank')
def get_current_rank_data(request):
    rank_data = state_manage.get_rank_data()

    # def get_top5(data, key):
    #     return sorted(data, key=lambda x: x[key], reverse=True)[:5]
    #
    # top5_call_time = get_top5(list(rank_data.values()), 'call_time')
    # top5_soc = get_top5(list(rank_data.values()), 'soc')

    # return JsonResponse({
    #     "top5_call_time": top5_call_time,
    #     "top5_soc": top5_soc
    # }, safe=False, json_dumps_params={"ensure_ascii": False})

    return JsonResponse({
        "data": list(rank_data.values())
    }, safe=False, json_dumps_params={"ensure_ascii": False})
