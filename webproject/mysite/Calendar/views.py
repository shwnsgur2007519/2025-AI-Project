from django.shortcuts import render
from .models import Schedule

def index(request):
    schedule_list=Schedule.objects.order_by('deadline')
    context={'schedule_list' : schedule_list}
    return render(request, 'calendar/schedule_list.html',context)