from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
# DRF增删改查的API，相当于封装好了很多业务逻辑，不用自己手动再写了。（感觉之前白学了？）
from rest_framework.generics import ListAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView, RetrieveAPIView
from rest_framework.response import Response


# Create your views here.


def index_view(request):
    return render(request, 'index/index.html')


# 测试前后端分离传送数据
def depart(request):
    c = {
        "status": 0,
        "message": "This is Django Message！"
    }
    return JsonResponse(c)


# 前后端分离计算器、前段向后端传数据
def calculate(request, n, o, m):
    password = request.GET.get('password', 'nonono')
    result = 'your operation is wrong'
    if o == '+':
        result = n + m
    elif o == '-':
        result = n - m
    elif o == '*':
        result = n * m
    c = {
        "status": 200,
        "message": "This is Django Message！",
        'result': result,
        'password': password
    }
    return JsonResponse(c)


