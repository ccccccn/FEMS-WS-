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

from .models import EnergyManageRank

logger = logging.getLogger(__name__)
# Create your views here.


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


fw_all_data_redis = redis.StrictRedis("localhost", 6379, 2,
                                      decode_responses=True, charset='UTF-8', encoding='UTF-8')
init_data = {}
LAST_RANK_DATA = {}
CURRENT_RANK_DATA = {}
LAST_RECORD_DATA = {}
CURRENT_RECORD_DATA = {}


# 初始化上一次的数据
def init_rank_data():
    global init_data, LAST_RANK_DATA, LAST_RECORD_DATA
    all_data = json.loads(fw_all_data_redis.get('latest_fw_data'))
    for key, value in all_data.items():
        LAST_RECORD_DATA[key] = {
            "soc": value["PCS_系统SOC"],
            "sys_state": value['EMS_SYS_State']
        }
    init_sql = 'SELECT id,call_time,soc FROM energy_manage_rank'
    with connection.cursor() as cursor:
        cursor.execute(init_sql)
        datas = cursor.fetchall()
        # print(f"data={datas}, {type(datas)}")
    for data in datas:
        id, call_time, soc = data
        init_data[f"flc_{id}"] = {
            "call_time": call_time,
            "soc": soc
        }
    LAST_RANK_DATA = init_data


"""
用于心跳机制刷新redis和mysql中的持久化数据，
也是直接将当前redis的数据传输到前端

1.项目刚启动时：将本地mysql的数据初始化到redis，后同项目启动之后
2.项目启动之后：将本地redis缓存中的数据封装，传输到前端展示
3.前端启动一个ws连接：向后端发送项目关闭（无论异常或者其他），将本地redis数据持久化到mysql

"""


def get_top5(data, key):
    top5 = sorted(data, key=itemgetter(key), reverse=True)[:5]
    return [
        {
            "id": item.get("id"),
            f"{key}": item.get(f"{key}"),
        } for item in top5
    ]


@action(['get'], False, 'energy_rank', 'energy_rank')
def get_current_rank_data(request, *args, **kwargs):
    global CURRENT_RANK_DATA, LAST_RANK_DATA, LAST_RECORD_DATA, CURRENT_RECORD_DATA

    # 初始化时使用 LAST_RANK_DATA
    if not CURRENT_RECORD_DATA:
        CURRENT_RECORD_DATA = LAST_RECORD_DATA.copy()
        CURRENT_RANK_DATA = LAST_RANK_DATA.copy()
        top5_call_time = get_top5([
            dict(**v, id=k) for k, v in LAST_RANK_DATA.items()
        ], "call_time")
        top5_soc = get_top5([
            dict(**v, id=k) for k, v in LAST_RANK_DATA.items()
        ], "soc")
        return JsonResponse({
            "top5_call_time": top5_call_time,
            "top5_soc": top5_soc
        }, safe=False, json_dumps_params={"ensure_ascii": False})

    # 否则对 Redis 数据进行处理
    fw_all_data = json.loads(fw_all_data_redis.get('latest_fw_data'))

    # 构造 CURRENT_RECORD_DATA
    CURRENT_RECORD_DATA = {
        key: {
            "id": key,
            "soc": value.get("EMS_SYS_SOC"),
            "sys_state": value.get("EMS_SYS_State")
        }
        for key, value in fw_all_data.items()
    }

    # 检测状态变更（以 key 相同为前提）
    change_keys = []
    for key in CURRENT_RECORD_DATA:
        current = CURRENT_RECORD_DATA.get(key)
        last = LAST_RECORD_DATA.get(key)
        if not last:
            continue
        if current["sys_state"] in [6, 7] and current["sys_state"] != last["sys_state"]:
            change_keys.append(key)

    # 更新 call_time
    for key in CURRENT_RECORD_DATA:
        current_soc = CURRENT_RECORD_DATA[key]["soc"]

        if key in change_keys:
            # 更新 soc 和时间
            CURRENT_RANK_DATA[key] = {
                'id': key,
                "soc": current_soc,
                "call_time": CURRENT_RANK_DATA[key]["call_time"]+1,
            }
        else:
            # 如果是新增 key，初始化 call_time，根据变更状态决定初始值
            CURRENT_RANK_DATA[key] = {
                'id': key,
                "soc": current_soc,
                "call_time": CURRENT_RANK_DATA[key]["call_time"],
            }

    # 排序并取前5
    top5_call_time = get_top5(list(CURRENT_RANK_DATA.values()), "call_time")
    top5_soc = get_top5(list(CURRENT_RANK_DATA.values()), "soc")

    # 更新 LAST_RECORD_DATA
    LAST_RECORD_DATA = CURRENT_RECORD_DATA.copy()

    return JsonResponse({
        "top5_call_time": top5_call_time,
        "top5_soc": top5_soc
    }, safe=False, json_dumps_params={"ensure_ascii": False})
