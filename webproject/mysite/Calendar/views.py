import calendar
import datetime
import json
from django.shortcuts import render, redirect
from .models import Schedule, ScheduleType
from .forms import ScheduleForm, ScheduleTypeForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.timezone import make_aware
from django.utils import timezone

def index(request):
    today = datetime.datetime.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(year, month)

    if request.user.is_authenticated:
        schedules = Schedule.objects.filter(
            deadline__year=year,
            deadline__month=month,
            owner=request.user
        )
    else:
        schedules = Schedule.objects.none()

    # 날짜별 일정 분류
    schedule_map = {}
    for schedule in schedules:
        date_key = schedule.deadline.day
        schedule_map.setdefault(date_key, []).append(schedule)

    # JSON용 schedule 정리 (모달용)
    schedule_json = {
    day: [
        {
            'id': s.id,
            'task_name': s.task_name,
            'subject': s.subject,
            'deadline': s.deadline.strftime('%Y-%m-%d %H:%M') if s.deadline else '',
            'is_fixed': s.is_fixed,
            'is_exam_task': s.is_exam_task,
            'owner_id': s.owner.id,
            'color': s.color,
        }
        for s in schedule_list
    ]
    for day, schedule_list in schedule_map.items()
    }


    prev_year, prev_month = (year - 1, 12) if month == 1 else (year, month - 1)
    next_year, next_month = (year + 1, 1) if month == 12 else (year, month + 1)

    context = {
        'year': year,
        'month': month,
        'calendar_data': month_days,
        'schedule_map': schedule_map,
        'schedule_json': json.dumps(schedule_json),
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'today_day': today.day if year == today.year and month == today.month else None,
        'user_id': request.user.id if request.user.is_authenticated else None,
    }

    return render(request, 'calendar/schedule_list.html', context)

@login_required
def schedule_week(request):
    date_str = request.GET.get('date')
    if date_str:
        try:
            reference_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            reference_date = timezone.now().date()
    else:
        reference_date = timezone.now().date()

    # 월요일 기준 주 시작일
    start_of_week = reference_date - datetime.timedelta(days=reference_date.weekday())
    days = [start_of_week + datetime.timedelta(days=i) for i in range(7)]

    schedules = Schedule.objects.filter(
        owner=request.user,
        start_time__date__range=(days[0],days[-1])
    )

    # 요일별로 스케줄 정리
    schedule_map = {day: [] for day in days}
    for schedule in schedules:
        key = schedule.start_time.date()
        if key in schedule_map:
            schedule_map[key].append(schedule)


    context = {
        'days': days,
        'schedule_map': schedule_map,
        'hours': range(0, 24),
        'user_id': request.user.id if request.user.is_authenticated else None,
        'prev_date': (start_of_week - datetime.timedelta(days=7)).strftime('%Y-%m-%d'),
        'next_date': (start_of_week + datetime.timedelta(days=7)).strftime('%Y-%m-%d'),
    }
    print(context['prev_date'])
    return render(request, 'calendar/schedule_week.html', context)


@login_required(login_url='common:login')
def schedule_create(request):
    if request.method == 'POST':
        form = ScheduleForm(request.POST, owner=request.user)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.owner = request.user
            schedule.save()
            return redirect('calendar:index')
    else:
        form = ScheduleForm(owner=request.user)
    return render(request, 'calendar/schedule_form.html', {'form': form, 'is_edit': False})


@login_required(login_url='common:login')
def schedule_edit(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk, owner=request.user)
    next_url = request.GET.get('next') or request.POST.get('next')  # GET/POST 모두 대응

    if request.method == 'POST':
        form = ScheduleForm(request.POST, instance=schedule, owner=request.user)
        if form.is_valid():
            form.save()

            # 보안 체크 포함
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect('calendar:index')
    else:
        form = ScheduleForm(instance=schedule, owner=request.user)

    return render(request, 'calendar/schedule_form.html', {
        'form': form,
        'is_edit': True,
        'next': next_url  # 템플릿에 전달
    })


@login_required(login_url='common:login')
def schedule_list(request):
    schedules = Schedule.objects.filter(owner=request.user).order_by('deadline')
    return render(request, 'calendar/schedule_list_page.html', {'schedules': schedules})

def schedule_type_create(request):
    if request.method == 'POST':
        form = ScheduleTypeForm(request.POST)
        if form.is_valid():
            schedule_type = form.save(commit=False)
            schedule_type.owner = request.user  # 소유자 지정
            schedule_type.save()
            return redirect('calendar:schedule_type_list')  # 저장 후 이동
    else:
        form = ScheduleTypeForm()
    
    return render(request, 'calendar/schedule_type_create.html', {'form': form})

@login_required(login_url='common:login')
def schedule_type_list(request):
    types = ScheduleType.objects.filter(owner=request.user)
    return render(request, 'calendar/schedule_type_list.html', {'types': types})

@login_required(login_url='common:login')
def schedule_type_edit(request, pk):
    schedule_type = get_object_or_404(ScheduleType, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = ScheduleTypeForm(request.POST, instance=schedule_type)
        if form.is_valid():
            form.save()
            return redirect('calendar:schedule_type_list')
    else:
        form = ScheduleTypeForm(instance=schedule_type)
    return render(request, 'calendar/schedule_type_form.html', {'form': form, 'is_edit': True})

@login_required(login_url='common:login')
def schedule_type_delete(request, pk):
    schedule_type = get_object_or_404(ScheduleType, pk=pk, owner=request.user)
    if request.method == 'POST':
        schedule_type.delete()
        return redirect('calendar:schedule_type_list')
    return render(request, 'calendar/schedule_type_confirm_delete.html', {'type': schedule_type})
