from django.shortcuts import render
from .auto-scraper-ver5 import *

from django.http import JsonResponse


# Create your views here.

def mainview(request) :
    return render(request, "machineapp/index.html")


def scrap(request) :
    run_main()
    return JsonResponse({'msg': '작업이 종료되었습니다'})