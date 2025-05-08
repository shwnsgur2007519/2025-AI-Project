from django.urls import path
from . import views

app_name='calendar'

urlpatterns = [
    path('', views.index, name='index'),
    path('schedule/create/', views.schedule_create, name='schedule_create'),
    path('schedule/<int:pk>/edit/', views.schedule_edit, name='schedule_edit'),
    path('schedule/list/', views.schedule_list, name='schedule_list'),
    path('schedule/type_create/', views.schedule_type_create, name='schedule_type_create'),
    path('schedule-type/list/', views.schedule_type_list, name='schedule_type_list'),
    path('schedule-type/<int:pk>/edit/', views.schedule_type_edit, name='schedule_type_edit'),
    path('schedule-type/<int:pk>/delete/', views.schedule_type_delete, name='schedule_type_delete'),

]
