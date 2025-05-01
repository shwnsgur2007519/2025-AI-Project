import calendar
import datetime
from django.shortcuts import render, redirect
from .models import Schedule
from .forms import ScheduleForm
from django.contrib.auth.decorators import login_required

def index(request):
    today = datetime.date.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(year, month)

    # 일정 불러오기: 로그인한 사용자 기준
    if request.user.is_authenticated:
        schedules = Schedule.objects.filter(deadline__year=year, deadline__month=month, owner=request.user)
    else:
        schedules = Schedule.objects.none()
    
    # 날짜별 일정 딕셔너리
    schedule_map = {}
    for schedule in schedules:
        date_key = schedule.deadline.day
        schedule_map.setdefault(date_key, []).append(schedule)

    # 이전/다음 달 계산
    prev_year, prev_month = (year - 1, 12) if month == 1 else (year, month - 1)
    next_year, next_month = (year + 1, 1) if month == 12 else (year, month + 1)
    # print(schedule_map)
    context = {
        'year': year,
        'month': month,
        'calendar_data': month_days,
        'schedule_map': schedule_map,
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'today_day': datetime.date.today().day if year == datetime.date.today().year and month == datetime.date.today().month else None,
    }
    return render(request, 'calendar/schedule_list.html', context)

@login_required(login_url='common:login')
def schedule_create(request):
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.owner = request.user  # 로그인 사용자 지정
            schedule.save()
            return redirect('calendar:index')
    else:
        form = ScheduleForm()
    return render(request, 'calendar/schedule_form.html', {'form': form})