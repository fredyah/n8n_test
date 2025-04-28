from django.urls import path
from . import views

urlpatterns = [
    path('get_weather', views.get_weather, name='get_weather'),
    path('get_date', views.get_date, name='get_date'),
]