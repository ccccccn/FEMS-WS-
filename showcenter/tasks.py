# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: task.py
 @DateTime: 2025-01-22 8:54
 @SoftWare: PyCharm
"""
import datetime
import json
import logging
from concurrent.futures import ThreadPoolExecutor

import redis
import taos
import numpy as np
import pymysql
from apscheduler.schedulers.background import BackgroundScheduler
from celery import Celery, shared_task
from celery.schedules import crontab
from django_apscheduler.jobstores import DjangoJobStore

from showcenter import MapperConfig
from taosPro.celery import fems_app

# app = Celery('showcenter')
center_redis_pool = redis.ConnectionPool(host='localhost', port=6379, db=2, decode_responses=True)
center_redis = redis.Redis(connection_pool=center_redis_pool)
center_exe = ThreadPoolExecutor(max_workers=10)
logger = logging.getLogger('showcenter')


# app.conf.beat_schedule = {
#     'scheduled-task': {
#         'task': 'showcenter.tasks.scheduled_task',
#         'schedule': crontab(minute='*/0.1'),  # 每15分钟执行一次
#     },
# }


def generate_time_range(time_type):
    """生成对应时间类型的 SQL 时间范围条件"""
    today = datetime.date.today()
    now = datetime.datetime.now()

    if time_type == 'day':
        start_time = f"{today} 00:00:00.000"
    elif time_type == 'month':
        start_time = f"{today.strftime('%Y-%m')}-01 00:00:00.000"
    elif time_type == 'year':
        start_time = f"{today.strftime('%Y')}-01-01 00:00:00.000"
    else:
        raise ValueError("Invalid time_type. Use 'day', 'month', or 'year'.")

    return f'ts >= "{start_time}" AND ts <= "{now}"'


def process_and_insert_data(time_type, analysis_type):
    pyconn = pymysql.connect(
        user='root',
        password='ccn020125.',
        host='127.0.0.1',
        database='taospro'
    )
    # except Exception as e:
    #     print(e)
    cursor = pyconn.cursor()

    conn = taos.connect(host='127.0.0.1', user='root', password='taosdata', port=6030)
    conn.select_db('test')
    tcur = conn.cursor()
    """统一处理数据并插入数据库"""
    # 生成动态 SQL 查询条件
    time_condition = generate_time_range(time_type)
    sql = f'''
        SELECT sys_soc, sys_fre, `duration` 
        FROM `fems_fccs`
        WHERE {time_condition}
    '''
    tcur.execute(sql)
    data = tcur.fetchall()
    data_np = np.array(data)
    if data_np.size == 0:
        print("没有查询到数据")
        return
    if data_np.ndim == 1:
        data_np = data_np.reshape(1, -1)

    # 定义各列的分箱规则 (可配置化)
    bins_config = {
        'soc': {'column': 0, 'bins': np.linspace(0, 100, 6), 'pie_type': 'Soc_distribution'},
        'fre': {'column': 1, 'bins': np.linspace(0, 15, 6), 'pie_type': 'Fre_distribution'},
        'drt': {'column': 2, 'bins': np.linspace(0, 100, 6), 'pie_type': 'Drt_distribution'}
    }

    # 统一处理各指标
    for metric, config in bins_config.items():
        col_data = data_np[:, config['column']]
        hist, _ = np.histogram(col_data, bins=config['bins'])
        if sum(hist) == 0:
            continue  # 避免除以零
        # 构造插入数据
        percentages = (np.round(hist / sum(hist), 4) * 100).tolist()
        insert_data = [
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            *percentages,
            analysis_type,
            config['pie_type']
        ]
        # print(tuple(insert_data))
        # 执行插入
        cursor.execute('select count(*) from taospro.pie_data_distribution')
        count = cursor.fetchone()[0]
        if count < 9:
            cursor.execute(
                '''
                INSERT INTO taospro.pie_data_distribution
                (analysis_time, partition1, partition2, partition3, partition4, partition5, analysis_type, pie_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ''',
                tuple(insert_data)
            )
            pyconn.commit()
            continue
        cursor.execute(
            '''
            UPDATE taospro.pie_data_distribution
            SET
                analysis_time = %s,
                partition1 = %s,
                partition2 = %s,
                partition3 = %s,
                partition4 = %s,
                partition5 = %s
            WHERE
                analysis_type = %s
                AND pie_type = %s
            ''',
            tuple(insert_data)
        )
        pyconn.commit()


@fems_app.task(queue='showcenter')
def statistic_show_center_pie_data_15min():
    for time_type in ['day', 'month', 'year']:
        process_and_insert_data(time_type, analysis_type=time_type)
    # print(f"插入成功--{datetime.datetime.now()}")


@fems_app.task(queue='showcenter')
def frequency_compare_analysis():
    try:
        try:
            all_data = json.loads(center_redis.get('latest_fw_data'))
            fccs_data = all_data.get('flc_0')
            frequency_data = {
                key: value for key, value in fccs_data.items() if key in MapperConfig.frequency_mapper
            }
            center_redis.publish('frequency_analysis', json.dumps(frequency_data, ensure_ascii=False))
            return {'status': 'success', 'msg': "该信息已发送至channel-frequency_analysis"}
        except:
            pass
        # logger.info(f"data:{frequency_data}")
    except Exception as e:
        logger.error(f"频率对比数据有误：{e}")


@fems_app.task(queue='showcenter')
def current_data_play_by_redis():
    data = json.loads(center_redis.get('latest_fw_data')).get('flc_0')
    try:
        play_data = {
            "实时功率": data['FCCS_RT_Action_POWER'],
            "电网频率": data['Grid_Frequency'],
            "电网电压": data['FCCS_SOC'],
            "环境温度": data['FCCS_SOC'],
            "设备状态": data['FCCS_SOC'],
            "通讯状态": data['FCCS_SOC']
        }
        center_redis.publish('station_current_data', json.dumps(play_data, ensure_ascii=False))
        return {'status': 'success', 'msg': "该信息已发送至channel-station_current_data"}
    except Exception as e:
        pass


@fems_app.task(queue='showcenter')
def running_statistics_station_data():
    return "ShowCenter"
