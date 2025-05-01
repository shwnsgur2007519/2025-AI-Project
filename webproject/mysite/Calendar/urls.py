from django.urls import path
from . import views

app_name='calendar'

urlpatterns = [
    path('', views.index, name='index'),
    path('schedule/create/', views.schedule_create, name='schedule_create'),
]
