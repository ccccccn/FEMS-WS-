""""
-------------------------api路由分割线------------------------
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from taos_capture.Collector_controller import start_collect, stop_collect, reset_collect
from taos_capture.task import run_data_collect_task


@csrf_exempt
def start_collect_view(request):
    if request.method == 'POST':
        try:
            run_data_collect_task.delay()
            return JsonResponse({'status': "success", 'message': '数据采集任务已提交'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': '仅支持POST请求'}, status=405)


@csrf_exempt
def stop_collect_view(request):
    if request.method == 'POST':
        stop_collect()
        return JsonResponse({'status': "stop!"})


@csrf_exempt
def reset_collect_view(request):
    if request.method == 'POST':
        reset_collect()
        return JsonResponse({'status': "reset!"})
