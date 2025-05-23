import json
import logging

import math

import time
from venv import logger

import redis
from django.http import JsonResponse
from django.shortcuts import render

from common.mapperConfig import system_params_overview_mapped_keys, system_params_detail_mapped_keys
from common.utils import cost_time

# Create your views here.


system_params_redis = redis.StrictRedis('localhost', 6379, db=2,
                                        charset='utf-8', decode_responses=True, encoding='utf-8')

# system_params_redis.xadd()


logger = logging.getLogger(__name__)


def smart_format(template: str, i: int) -> str:
    count = template.count("{}")
    if count == 1:
        return template.format(i)
    elif count == 2:
        return template.format(math.ceil(i / 2), 1 if i % 2 == 1 else 2)
    elif count == 0:
        return template
    else:
        raise ValueError(f"模板占位符数量不支持: {template}")


# 提前生成 smart_format 映射结果 → 避免循环中格式化消耗
def generate_fw_key_map(flat_keys):
    cache = {}
    for i in range(1, 9):
        cache[f"F{i}"] = {
            k: smart_format(tpl, i) for k, tpl in flat_keys
        }
    return cache


FW_MAPPED_KEYS = generate_fw_key_map(system_params_detail_mapped_keys["FW"])
PCS_MAPPED_KEYS = dict(system_params_detail_mapped_keys["PCS"])
OVERVIEW_KEYS = dict(system_params_overview_mapped_keys)


@cost_time
def systemParamsView():
    while True:
        try:
            raw = system_params_redis.get("latest_fw_data")
            if not raw:
                time.sleep(5)
                continue
            all_data = json.loads(raw)
            overview_result = {
                name: {k: item.get(v) for k, v in OVERVIEW_KEYS.items()}
                for name, item in all_data.items()
            }
            system_params_redis.publish("systemParamsOverview", json.dumps(overview_result, ensure_ascii=False))

        except Exception as e:
            logger.exception("systemParamsView 异常", exc_info=True)
        finally:
            time.sleep(2)


def systemParamsDetailView():
    while True:
        try:
            raw = system_params_redis.get("latest_fw_data")
            if not raw:
                time.sleep(5)
                continue
            all_data = json.loads(raw)
            result = {}
            for name, flat in all_data.items():
                flywheels = {
                    key: {field: flat.get(template) for field, template in mapped.items()}
                    for key, mapped in FW_MAPPED_KEYS.items()
                }
                flywheels["PCS"] = {k: flat.get(v) for k, v in PCS_MAPPED_KEYS.items()}
                result[name] = flywheels
            system_params_redis.publish("systemParamsDetail", json.dumps(result, ensure_ascii=False))
        except Exception as e:
            logger.exception("systemParamsDetailView 异常", exc_info=True)
        finally:
            time.sleep(2)
