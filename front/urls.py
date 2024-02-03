from django.urls import path
from . import views
app_name = 'front'

urlpatterns = [
    path('', views.index, name='home'),
    path('proxy_check' , views.proxy_check, name ='proxy_check'),
    ]

