import json
from datetime import datetime, timedelta
from .models import Schedule, ScheduleType
from django.contrib.auth.models import User

def toSchedule(relocated_list):
    """
    schedule_relocation()이 반환한 dict 리스트를 받아,
    각 dict를 Schedule 인스턴스로 복원하여 리스트로 반환.
    """
    restored = []
    for data in relocated_list:
        # 1) ForeignKey 복원
        owner = User.objects.get(pk=data['owner_id'])
        task_type = None
        if data.get('task_type_id') is not None:
            task_type = ScheduleType.objects.get(pk=data['task_type_id'])
        exam = None
        if data.get('exam_id') is not None:
            exam = Schedule.objects.get(pk=data['exam_id'])

        # 2) DateTimeField 복원
        for dt_key in ('deadline', 'start_time', 'end_time'):
            dt_val = data.get(dt_key)
            if dt_val:
                data[dt_key] = datetime.strptime(dt_val, '%Y-%m-%d %H:%M:%S')
            else:
                data[dt_key] = None

        # 3) 나머지 필드 값을 꺼내서 Schedule 인스턴스 생성
        instance = Schedule(
            owner            = owner,
            task_name        = data.get('task_name'),
            duration_minutes = data.get('duration_minutes'),
            difficulty       = data.get('difficulty'),
            importance       = data.get('importance'),
            task_type        = task_type,
            subject          = data.get('subject'),
            is_exam_task     = data.get('is_exam_task', False),
            deadline         = data.get('deadline'),
            start_time       = data.get('start_time'),
            end_time         = data.get('end_time'),
            is_fixed         = data.get('is_fixed', False),
            exam             = exam,
            color            = data.get('color', '#6c8df5'),
            is_done          = data.get('is_done', False),
        )
        restored.append(instance)

    return restored

from datetime import datetime

def toJson(instances):
    """
    Schedule 인스턴스 리스트를 schedule_relocation()에 넘길 수 있는
    dict 리스트로 변환.
    DateTimeField는 "YYYY-MM-DD HH:MM:SS" 문자열로, 
    ForeignKey는 *_id 필드로, 
    나머지 필드는 원시값 그대로 반환.
    """
    result = []
    for inst in instances:
        data = {
            'id':               inst.pk,
            'owner_id':         inst.owner_id,
            'task_name':        inst.task_name,
            'duration_minutes': inst.duration_minutes,
            'difficulty':       inst.difficulty,
            'importance':       inst.importance,
            'task_type_id':     inst.task_type_id,
            'subject':          inst.subject,
            'is_exam_task':     inst.is_exam_task,
            # DateTimeField → 문자열
            'deadline':         inst.deadline.strftime('%Y-%m-%d %H:%M:%S') if inst.deadline else None,
            'start_time':       inst.start_time.strftime('%Y-%m-%d %H:%M:%S') if inst.start_time else None,
            'end_time':         inst.end_time.strftime('%Y-%m-%d %H:%M:%S') if inst.end_time else None,
            'is_fixed':         inst.is_fixed,
            'exam_id':          inst.exam_id,
            'color':            inst.color,
            'is_done':          inst.is_done,
        }
        result.append(data)
    return result



def schedule_relocation(data):
    relocated = []
    for val in data:
        # ISO 포맷("YYYY-MM-DDTHH:MM:SS") 혹은 "YYYY-MM-DD HH:MM:SS" 문자열을 파싱
        original = datetime.fromisoformat(val['start_time'])
        # 하루(1일) 뒤로
        new_start = original + timedelta(days=1)
        # Django DateTimeField가 잘 읽는 포맷으로 문자열화
        val['start_time'] = new_start.strftime('%Y-%m-%d %H:%M:%S')
        relocated.append(val)
    return relocated
