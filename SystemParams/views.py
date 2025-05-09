import json
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


@cost_time
def systemParamsView():
    while True:
        try:
            all_fw_latest_data = json.loads(system_params_redis.get('latest_fw_data'))
            sys_params_data = {
                name: {k: data.get(v, None) for k, v in system_params_overview_mapped_keys}
                for name, data in all_fw_latest_data.items()
            }
            # print(sys_params_data['飞轮舱1'])
            sys_params_data = json.dumps(sys_params_data, ensure_ascii=False)
            system_params_redis.publish("systemParamsOverview", sys_params_data)
        except Exception as e:
            logger.error(f'系统参数总览页面有误：{e}')
        finally:
            time.sleep(5)


def smart_format(template: str, i: int) -> str:
    count = template.count("{}")
    if count == 1:
        tempstr = template.format(i)
        return template.format(i)
    elif count == 2:
        tmpstr = template.format(math.ceil(i / 2), 1 if i % 2 == 1 else 2)
        return template.format(math.ceil(i / 2), 1 if i % 2 == 1 else 2)
    elif count == 0:
        return template
    else:
        raise ValueError(f"模板占位符数量不支持: {template}")


def systemParamsDetailView():
    while True:
        try:
            latest_data_raw = system_params_redis.get('latest_fw_data')
            if not latest_data_raw:
                logger.warning("未获取到最新飞轮数据")
                continue

            all_fw_latest_data = json.loads(latest_data_raw)
            sys_params_detail = {}

            for name, fw_data in all_fw_latest_data.items():
                fw_detail = {}
                for i in range(1, 9):
                    fw_detail[f"F{i}"] = {
                        key: fw_data.get(smart_format(template, i), None)
                        for key, template in system_params_detail_mapped_keys["FW"]
                    }
                fw_detail['PCS'] = {
                    k: fw_data.get(v, None) for k, v in system_params_detail_mapped_keys["PCS"]
                }
                sys_params_detail[name] = fw_detail

            # print(json.dumps(sys_params_detail['飞轮舱1'],ensure_ascii=False))
            # 此处可将 sys_params_detail 赋值给前端缓存/返回等逻辑
            system_params_redis.publish("systemParamsDetail",json.dumps(sys_params_detail,ensure_ascii=False))
            # yield sys_params_detail 或赋值到 Redis 等...

        except Exception as e:
            logger.error(f"系统参数详情处理异常：{e}", exc_info=True)
        finally:
            time.sleep(5)