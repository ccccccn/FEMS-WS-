from django.shortcuts import render

# Create your views here.
# energy/views.py
from django.http import JsonResponse

def index(request):
    return JsonResponse({'message': 'Welcome to FEMS API'})