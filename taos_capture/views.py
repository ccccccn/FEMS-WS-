from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets
from .models import WeiboHotPointSearch
from .serializers import MyModelSerializer
from .data_migration.trend_analysis import data_main as data_capture_main
from .data_migration.trend_analysis import collecting


class MyModelListCreate(viewsets.ModelViewSet):
    queryset = WeiboHotPointSearch.objects.all()
    serializer_class = MyModelSerializer


def home(request):
    return render(request, 'index.html')


def index(request):
    return HttpResponse("Hello world,you are at the index page")

def DataCapturePage(request):
    if request.method == 'POST':
        return render(request, 'taos_capture/data_capture.html', {'message': "Data capture started!"})
    return render(request, 'taos_capture/data_capture.html')


def pause_data_collection(request):
    global collecting
    collecting = False
    return JsonResponse({'message': 'Data collection has been paused.'})
