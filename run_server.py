import os
import subprocess
import threading
from importlib import import_module
from typing import List

import django
import sys
import signal
import time
import traceback

from django.apps import apps

from common.LogRecord import setup_logger

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taosPro.settings')
django.setup()
# 子进程对象全局保存
celery_worker_proc = None
celery_flower_proc = None
celery_beat_proc = None
uvicorn_proc = None


# INIT_FLAG = os.path.join(os.path.dirname(__file__), 'celery_init.flag')


def run_celery(app_name):
    global celery_worker_proc
    celery_worker_proc = subprocess.Popen([
        'celery', '-A', 'taosPro', 'worker',
        '--pool=threads',  # Windows ONLY 支持 solo 或 threads
        '-c', '9',  # solo 模式只能单线程，线程模式可调
        '-n', f'{app_name}_worker@%h',
        '-Q', app_name,
        '--max-tasks-per-child=100',
        '--loglevel=info',
        '-E'
    ])
    return celery_worker_proc


def run_flower():
    global celery_flower_proc
    celery_flower_proc = subprocess.Popen([
        'celery',
        '-A', 'taosPro',
        'flower',
        '--loglevel=info',
        '--port=5556',
        '--address=0.0.0.0'
    ])
    return celery_flower_proc


def run_celery_beat():
    global celery_beat_proc
    celery_beat_proc = subprocess.Popen([
        'celery', '-A', 'taosPro', 'beat',
        '--scheduler=django_celery_beat.schedulers:DatabaseScheduler',
        # '--pidfile=/tmp/celerybeat.pid',
        '--max-interval=10',  # 缩短检查间隔
        '--loglevel=info'
    ])


def run_uvicorn():
    global uvicorn_proc
    uvicorn_proc = subprocess.Popen([
        'uvicorn',
        'taosPro.asgi:application',
        '--host', '192.168.97.125',
        '--port', '10002',
        '--log-level', 'info',
    ])
    return uvicorn_proc


# 执行所有 app 的 celery_task_init.init_periodic_task()
def init_all_app_tasks():
    logger = setup_logger()
    # if os.path.exists(INIT_FLAG):
    #     logger.info("Celery 任务已初始化，跳过")
    #     return
    logger.info("开始初始化 Celery 任务...")

    for app_config in apps.get_app_configs():
        try:
            task_init_module = import_module(f"{app_config.name}.celery_task_init")
            if hasattr(task_init_module, "init_periodic_task"):
                task_init_module.init_periodic_task()
                print(f"已初始化 {app_config.name} 的定时任务")
                logger.info(f"已初始化 {app_config.name} 的定时任务")
        except ModuleNotFoundError:
            continue  # 某些 app 没有任务初始化文件，跳过
        except Exception as e:
            logger.exception(f"初始化 {app_config.name} 任务失败: {e}")

    # with open(INIT_FLAG, "w") as f:
    #     f.write("done")
    # logger.info("Celery Beat 任务初始化完成")


def handle_shutdown(signum, frame):
    print("\n🔌 安全关闭中...")
    procs = [uvicorn_proc, celery_worker_proc, celery_flower_proc, celery_beat_proc]
    for p in procs:
        if p and p.poll() is None:  # 进程存在且未结束
            print(f"终止进程 PID={p.pid}")
            p.terminate()

    # 等待进程退出
    timeout = 5
    start = time.time()
    while time.time() - start < timeout:
        if all(p.poll() is not None for p in procs if p):
            break
        time.sleep(0.5)
    else:
        # 仍未结束，强制杀死
        for p in procs:
            if p and p.poll() is None:
                print(f"强制杀死进程 PID={p.pid}")
                p.kill()

    print("✅ 所有子进程已安全关闭。")
    sys.exit(0)


if __name__ == "__main__":
    # 注册信号处理
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    print("🚀 启动 Uvicorn 服务...")
    run_uvicorn()
    print("🌱 启动 Celery Worker...")
    app_name = ['showcenter', 'EnergyManagement', 'SystemParams']
    for name in app_name:
        run_celery(name)

    print("🧩 初始化定时任务...")
    init_all_app_tasks()  # <-- ⏱ 必须先执行！
    time.sleep(2)
    print("🕒 启动 Celery Beat...")
    run_celery_beat()

    print("🌼 启动 Flower...")
    run_flower()

    try:
        while True:
            time.sleep(1)  # 保持主进程存活，等待信号
    except KeyboardInterrupt:
        handle_shutdown(signal.SIGINT, None)
    except Exception:
        traceback.print_exc()
        handle_shutdown(None, None)
