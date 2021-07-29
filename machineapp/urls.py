
from django.urls import path, include
from .views import *
app_name='machineapp'

urlpatterns = [
    path('', mainview ),
    path('scrap/', scrap, name='scrap' )

]
