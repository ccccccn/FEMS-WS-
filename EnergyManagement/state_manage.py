# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: state_manage.py
 @DateTime: 2025-05-14 19:47
 @SoftWare: PyCharm
"""
import decimal
import json
from threading import Lock
from django_redis import get_redis_connection

REDIS_KEY_CURRENT_RANK = 'state:current_rank'
REDIS_KEY_LAST_RANK = 'state:last_rank'
REDIS_KEY_CURRENT_RECORD = 'state:current_record'
REDIS_KEY_LAST_RECORD = 'state:last_record'
REDIS_KEY_INIT = 'state:is_initialized'
data_lock = Lock()

class StateManage:
    def __init__(self):
        self.conn = get_redis_connection('default')

    @staticmethod
    def _decimal_default(obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        raise TypeError(f"Type {type(obj)} not serializable")

    def _set_json(self, key, value):
        self.conn.set(key, json.dumps(value, default=self._decimal_default))

    def _get_json(self, key):
        data = self.conn.get(key)
        return json.loads(data) if data else {}

    def is_initialized(self):
        return self.conn.get(REDIS_KEY_INIT) == b'1'

    def mark_initialized(self):
        self.conn.set(REDIS_KEY_INIT, "1")

    def init_data(self, current_rank, last_rank, current_record, last_record):
        self._set_json(REDIS_KEY_LAST_RANK, last_rank)
        self._set_json(REDIS_KEY_LAST_RECORD, last_record)
        self._set_json(REDIS_KEY_CURRENT_RECORD, current_record)
        self._set_json(REDIS_KEY_CURRENT_RANK, current_rank)

    def update_current_and_rank(self, current_data):
        with data_lock:
            current_rank = self._get_json(REDIS_KEY_CURRENT_RANK)
            last_record = self._get_json(REDIS_KEY_LAST_RANK)

            change_keys = []
            charge_key = []
            discharge_key = []
            for key, value in current_data.items():
                if str(key).split("_")[-1] == 0:
                    continue
                new_sys_state = value.get('sys_state')
                old_sys_state = last_record.get(key, {}).get('sys_state')
                if new_sys_state != old_sys_state and new_sys_state in [6, 7]:
                    change_keys.append(key)
                if new_sys_state == 6:
                    charge_key.append(key)
                if new_sys_state == 7:
                    discharge_key.append(key)
            for key, val in current_data.items():
                if str(key).split("_")[-1] == 0:
                    continue
                soc = val.get("soc")
                call_time = current_rank.get(key, {}).get("call_time", 0)
                charge_time = current_rank.get(key, {}).get("charge_time", 0)
                discharge_time = current_rank.get(key, {}).get("discharge_time", 0)
                if key in change_keys and key in charge_key:
                    current_rank[key] = {"id": key, "soc": soc, "call_time": call_time + 1,
                                         "charge_time": charge_time+1,'discharge_time': discharge_time}
                elif key in change_keys and key in discharge_key:
                    current_rank[key] = {"id": key, "soc": soc, "call_time": call_time + 1,
                                         "charge_time": charge_time, 'discharge_time': discharge_time+1}
                else:
                    current_rank[key] = {"id": key, "soc": soc, "call_time": call_time,
                                         "charge_time": charge_time, 'discharge_time': discharge_time}

        self._set_json(REDIS_KEY_CURRENT_RANK, current_rank)
        self._set_json(REDIS_KEY_CURRENT_RECORD, current_data)
        self._set_json(REDIS_KEY_LAST_RECORD, current_data)

    def get_rank_data(self):
        return self._get_json(REDIS_KEY_CURRENT_RANK)

    def get_last_rank_data(self):
        return self._get_json(REDIS_KEY_LAST_RANK)

    def load_and_init_data(self, rank_list, record_dict):
        rank_data = {
            f'flc_{item.id}': {"id": item.id, "soc": item.soc, "call_time": item.call_time,
                               "charge_time":item.charge_time,"discharge_time":item.discharge_time}
            for item in rank_list
        }
        self._set_json(REDIS_KEY_LAST_RANK, rank_data)
        self._set_json(REDIS_KEY_CURRENT_RANK, rank_data)
        self._set_json(REDIS_KEY_LAST_RECORD, record_dict)
        self._set_json(REDIS_KEY_CURRENT_RECORD, record_dict)
