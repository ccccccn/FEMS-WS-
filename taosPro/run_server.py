# # -*- coding:UTF-8 -*-
# """
#  @Author: CNN
#  @FileName: run_server.py
#  @DateTime: 2025-02-07 9:00
#  @SoftWare: PyCharm
# """
# import subprocess
# from multiprocessing import Process
#
# import uvicorn
# import sys
# import signal
# from django.core.management import call_command
#
#
# def handle_shutdown(signal, frame):
#     print("\n🔌 安全关闭中...")
#     if 'celery_proc' in globals():
#         celery_proc.terminate()
#     # 在这里可以执行一些清理操作，例如关闭数据库连接等
#     sys.exit(0)
#
#
# def run_celery():
#     subprocess.run([
#         'celery', '-A', 'common', 'worker', '--events',
#         '--pool=solo',
#         '--concurrency=32',  # 根据CPU核心数调整
#         '--max-tasks-per-child=100',  # 防止内存泄漏
#         '--heartbeat-interval=10',  # 保持心跳检测
#         '--without-gossip',  # 禁用集群通信（单机部署时）
#         '--optimization=fair',  # 任务公平调度算法
#         '--loglevel=info'  # 调试时使用
#     ])
#
#
# def run_flower():
#     subprocess.run([
#         'celery', '-A', 'common', 'flower'
#     ])
#
# if __name__ == "__main__":
#     # 注册信号处理函数
#     signal.signal(signal.SIGINT, handle_shutdown)
#     signal.signal(signal.SIGTERM, handle_shutdown)
#
#     global celery_proc
#     celery_proc = Process(target=run_celery)
#     celery_flower_proc = Process(target=run_flower)
#     celery_proc.start()
#     celery_flower_proc.start()
#     print("✅ Celery worker 已启动 | PID:", celery_proc.pid)
#
#     # 启动 Uvicorn
#     print("🚀 Uvicorn 服务启动中...")
#     uvicorn.run("taosPro.asgi:application", host="192.168.102.75", port=10000, reload=True)
# -*- coding:UTF-8 -*-
"""
 @Author: CNN
 @FileName: run_server.py
 @DateTime: 2025-02-07 9:00
 @SoftWare: PyCharm
"""
import subprocess
from multiprocessing import Process
import signal
import uvicorn
import sys



def handle_shutdown(signal, frame):
    print("\n🔌 安全关闭中...")
    # 终止所有子进程
    # if 'celery_proc' in globals() and celery_proc.is_alive():
    #     celery_proc.terminate()
    #     celery_proc.join()
    # if 'celery_flower_proc' in globals() and celery_flower_proc.is_alive():
    #     celery_flower_proc.terminate()
    #     celery_flower_proc.join()
    # if 'celery_beat_proc' in globals() and celery_beat_proc.is_alive():
    #     celery_beat_proc.terminate()
    #     celery_beat_proc.join()
    if 'uvicorn_proc' in globals() and uvicorn_proc.is_alive():
        uvicorn_proc.terminate()
        uvicorn_proc.join()
    print("✅ 所有子进程已安全关闭。")
    sys.exit(0)


def run_celery():
    subprocess.Popen([
        'celery',
        '-A', 'common',
        'worker',
        '--events',
        '--pool=solo',
        '--concurrency=8',  # 根据 CPU 核心数调整（例如 8 核可用 8）
        '--max-tasks-per-child=100',
        '--heartbeat-interval=10',
        '--without-gossip',
        '--optimization=fair',
        '--loglevel=info',
        '--include=common.celery',
    ])


def run_flower():
    subprocess.Popen([
        'celery',
        '-A', 'common',
        'flower',
        '--loglevel=info'
    ])


def run_celery_beat():
    # Celery Beat 负责调度周期性任务
    subprocess.Popen([
        'celery',
        '-A', 'common',
        'beat',
        '--loglevel=info',
        '--pidfile=',
        '--max-interval=30'  # 防止调度器停顿
    ])


def run_uvicorn():
    uvicorn.run(
        "taosPro.asgi:application",
        # host="localhost",
        host="192.168.102.75",
        port=10001,
        reload=True
    )


if __name__ == "__main__":
    # # 注册信号处理函数
    # signal.signal(signal.SIGINT, handle_shutdown)
    # signal.signal(signal.SIGTERM, handle_shutdown)
    #
    # # 启动 Celery Worker
    # celery_proc = Process(target=run_celery)
    # celery_proc.start()
    # print("✅ Celery worker 已启动 | PID:", celery_proc.pid)
    #
    # # 启动 Celery Flower
    # celery_flower_proc = Process(target=run_flower)
    # celery_flower_proc.start()
    # print("✅ Celery Flower 已启动 | URL: http://localhost:5555")
    #
    # # 启动 Celery Beat
    # celery_beat_proc = Process(target=run_celery_beat)
    # celery_beat_proc.start()
    # print("✅ Celery Beat 已启动 | 负责周期性任务调度")

    # 启动 Uvicorn
    uvicorn_proc = Process(target=run_uvicorn)
    print("🚀 Uvicorn 服务启动中...")
    uvicorn_proc.start()


    # 等待所有进程完成
    # 等待所有进程完成
    try:
        uvicorn_proc.join()
        # celery_proc.join()
        # celery_flower_proc.join()
        # celery_beat_proc.join()
    except KeyboardInterrupt:
        handle_shutdown(signal.SIGINT, None)
