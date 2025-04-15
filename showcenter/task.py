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

import numpy as np
import pymysql
from apscheduler.schedulers.background import BackgroundScheduler
from celery import Celery, shared_task
from celery.schedules import crontab
from django_apscheduler.jobstores import DjangoJobStore

from common.TaosClass import TaosClass

app = Celery('showcenter')

logger = logging.getLogger('showcenter')

app.conf.beat_schedule = {
    'scheduled-task': {
        'task': 'showcenter.tasks.scheduled_task',
        'schedule': crontab(minute='*/0.1'),  # 每15分钟执行一次
    },
}

scheduler = BackgroundScheduler(timezone='Asia/Shanghai')
scheduler.add_jobstore(DjangoJobStore(), "default")

taos = TaosClass('localhost', 'taos', 'taosdata', 6030)
conn = taos.connect("test")
tcur = conn.cursor()
pyconn = pymysql.connect(
        user='root',
        password='ccn020125.',
        host='127.0.0.1',
        database='taospro'
    )
    # except Exception as e:
    #     print(e)
cursor = pyconn.cursor()

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


def process_and_insert_data(cursor, tcur, time_type, analysis_type):
    """统一处理数据并插入数据库"""
    # 生成动态 SQL 查询条件
    time_condition = generate_time_range(time_type)
    sql = f'''
        SELECT sys_soc, sys_fre, `duration` 
        FROM `fems_flc1`
        WHERE {time_condition}
    '''
    tcur.execute(sql)
    data = tcur.fetchall()

    if not data:
        return  # 无数据时跳过

    data_np = np.array(data)

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
        print(tuple(insert_data))
        # 执行插入
        cursor.execute(
            '''
            INSERT INTO taospro.pie_data_distribution 
            (analysis_time, partition1, partition2, partition3, partition4, partition5, analysis_type, pie_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''',
            tuple(insert_data)
        )
        pyconn.commit()

@shared_task
def scheduled_task():
    logger.info("Scheduled task is running")


@scheduler.scheduled_job('interval', minutes=0.1, id='showcenter_piedata_15min_task')
def statistic_show_center_pie_data_15min(i):
    for time_type in ['day', 'month', 'year']:
        process_and_insert_data(cursor, tcur, time_type, analysis_type=time_type)
    print("插入成功")
    """
    input_sql:
    (SELECT histogram(sys_soc, 'user_input', '[1,20,40,60,80,100]]', 0) as sys_soc_day
         FROM test.`fems_flc1` 
         WHERE ts >= "2025-04-11 00:00:00.000" AND ts <= "2025-04-11 13:54:11.114180")
            UNION ALL 
            (SELECT histogram(sys_soc, 'user_input', '[2,20,40,60,80,102]', 0)  as sys_soc_month
         FROM test.`fems_flc1` 
         WHERE ts >= "2025-04-01 00:00:00.000" AND ts <= "2025-04-11 13:54:11.114180")
        UNION ALL 
        (SELECT histogram(sys_soc, 'user_input', '[4,20,40,60,80,101]', 0) as sys_soc_year
         FROM test.`fems_flc1` 
         WHERE ts >= "2025-01-01 00:00:00.000" AND ts <= "2025-04-11 13:54:11.114180");
        output:
        [
                ([(bucket_start, count), ...], [(bucket_start, count), ...], [(bucket_start, count), ...])
        ]
        """
