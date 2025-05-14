# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: state_manage.py
 @DateTime: 2025-05-14 19:47
 @SoftWare: PyCharm
"""
from threading import Lock

CURRENT_RANK_DATA = {}
LAST_RANK_DATA = {}
LAST_RECORD_DATA = {}
CURRENT_RECORD_DATA = {}

data_lock = Lock()
_is_initialized = False


def is_initialized():
    global _is_initialized
    return _is_initialized


def mark_initialized():
    global _is_initialized
    _is_initialized = True


def init_data(current_rank, last_rank, current_record, last_record):
    global CURRENT_RANK_DATA, LAST_RANK_DATA, LAST_RECORD_DATA, CURRENT_RECORD_DATA
    with data_lock:
        CURRENT_RANK_DATA = current_rank
        CURRENT_RECORD_DATA = current_record
        LAST_RANK_DATA = last_rank
        LAST_RECORD_DATA = last_record


def update_current_and_rank(current_data):
    global CURRENT_RANK_DATA, CURRENT_RECORD_DATA, LAST_RANK_DATA, LAST_RECORD_DATA
    with data_lock:
        change_keys = []
        for key, value in current_data.items():
            new_sys_state = value.get('sys_state')
            old_sys_state = LAST_RECORD_DATA.get(key, {}).get("sys_state")
            if new_sys_state != old_sys_state and new_sys_state in [6, 7]:
                change_keys.append(key)
        for key, val in current_data.items():
            soc = val.get("soc")
            if key in CURRENT_RANK_DATA:
                call_time = CURRENT_RANK_DATA[key].get("call_time", 0)
                if key in change_keys:
                    call_time += 1
                CURRENT_RANK_DATA[key] = {"id": key, "soc": soc, "call_time": call_time}
            else:
                CURRENT_RANK_DATA[key] = {"id": key, "soc": soc, "call_time": 1 if key in change_keys else 0}

        CURRENT_RECORD_DATA = current_data.copy()
        LAST_RECORD_DATA = current_data.copy()


def get_rank_data():
    with data_lock:
        return CURRENT_RANK_DATA.copy()


def get_last_rank_data():
    with data_lock:
        return LAST_RANK_DATA.copy()


def load_and_init_data(rank_list, record_dict):
    global LAST_RANK_DATA, LAST_RECORD_DATA
    LAST_RANK_DATA = {item.id: {"id": item.id, "soc": item.soc, "call_time": item.call_time} for item in rank_list}
    LAST_RECORD_DATA = record_dict
