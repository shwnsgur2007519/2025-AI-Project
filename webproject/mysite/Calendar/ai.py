import json
from datetime import datetime, timedelta
from .models import Schedule, ScheduleType
from django.contrib.auth.models import User
from datetime import datetime

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


def toJson(instances):
    """
    Schedule 인스턴스 리스트를 JSON 직렬화 가능한 dict 리스트로 변환.
    datetime은 문자열로, None/기본값 포함 처리.
    """
    result = []
    for inst in instances:
        def dt_str(dt):
            return dt.strftime('%Y-%m-%d %H:%M:%S') if dt else None

        data = {
            'id':               inst.pk,
            'owner_id':         inst.owner_id,
            'task_name':        inst.task_name or '',
            'duration_minutes': inst.duration_minutes,
            'difficulty':       inst.difficulty,
            'importance':       inst.importance,
            'task_type_id':     inst.task_type_id,
            'subject':          inst.subject or '',
            'is_exam_task':     bool(inst.is_exam_task),
            'deadline':         dt_str(inst.deadline),
            'start_time':       dt_str(inst.start_time),
            'end_time':         dt_str(inst.end_time),
            'is_fixed':         bool(inst.is_fixed),
            'exam_id':          inst.exam_id,
            'color':            inst.color or '#6c8df5',
            'is_done':          bool(inst.is_done),
        }
        result.append(data)
    return result

def schedule_relocation(task_list):
    import numpy as np
    import random
    import math
    import calendar
    from datetime import datetime, date, timedelta
    import os

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    weight_file_path = os.path.join(BASE_DIR, "trained_weights.npy")

    state_dim = 3
    action_dim = len(task_list)
    feature_dim = state_dim + action_dim

    def get_feature(state, action):
        one_hot = np.zeros(action_dim, dtype=np.float32)
        one_hot[action] = 1.0
        return np.concatenate([state.astype(np.float32), one_hot])

    if not os.path.exists(weight_file_path):
        raise FileNotFoundError(f"가중치 파일이 없습니다: {weight_file_path}")

    w_loaded = np.load(weight_file_path)
    old_dim = w_loaded.shape[0]
    if old_dim != feature_dim:
        w = np.zeros(feature_dim, dtype=np.float32)
        w[:state_dim] = w_loaded[:state_dim]
        old_action_dim = old_dim - state_dim
        copy_cnt = min(old_action_dim, action_dim)
        if copy_cnt > 0:
            w[state_dim : state_dim + copy_cnt] = w_loaded[state_dim : state_dim + copy_cnt]
    else:
        w = w_loaded.astype(np.float32)

    today = date.today()
    month_start = datetime.combine(date(today.year, today.month, 1), datetime.min.time())
    _, month_days = calendar.monthrange(today.year, today.month)

    deadline_tasks = []
    for idx, t in enumerate(task_list):
        due_str = t.get("due_date", None)
        if due_str:
            due_dt = datetime.strptime(due_str, "%Y-%m-%d %H:%M:%S")
            delta = due_dt - month_start
            due_offset = int(delta.total_seconds() // 60)
            deadline_tasks.append((idx, t["duration_minutes"], due_offset))

    def check_deadline_feasible_from(remaining_deadline_tasks, curr_time):
        for (idx, dur, due_offset) in remaining_deadline_tasks:
            tod = curr_time % 1440
            if tod > 22 * 60:
                curr_time += (1440 - tod) + (7 * 60)
            elif tod < 7 * 60:
                curr_time += (7 * 60 - tod)
            if curr_time + dur > due_offset:
                return False
            curr_time += dur + 10
        return True

    start_time_for_deadline = 7 * 60
    if not check_deadline_feasible_from(deadline_tasks, start_time_for_deadline):
        return task_list  # 불가능할 경우 원본 그대로 반환

    class SimpleScheduleEnv:
        def __init__(self, task_list):
            self.task_list = task_list
            self.total_actions = len(task_list)
            self.month_start = month_start
            self.month_days = month_days

        def reset(self):
            self.idx = 0
            self.schedule = [-1] * self.total_actions
            self.start_times = []
            self.current_time = 7 * 60
            self.done = False
            return self._get_state()

        def _get_state(self):
            remaining = sum(1 for i in range(self.total_actions) if i not in self.schedule)
            return np.array([
                self.idx / self.total_actions,
                remaining / self.total_actions,
                (self.current_time % 1440) / 1440
            ], dtype=np.float32)

        def step(self, action):
            if self.done:
                return self._get_state(), 0, True, {}

            self.schedule[self.idx] = action
            self.start_times.append(self.current_time)
            dur = self.task_list[action]["duration_minutes"]
            self.current_time += dur + 10 + random.randint(10, 30)

            tod = self.current_time % 1440
            if tod > 22 * 60:
                self.current_time += (1440 - tod) + 7 * 60
            elif tod < 7 * 60:
                self.current_time += (7 * 60 - tod)

            self.idx += 1
            if self.idx >= self.total_actions:
                self.done = True

            return self._get_state(), 0, self.done, {}

    env = SimpleScheduleEnv(task_list)
    state = env.reset()

    while not env.done:
        valid = [a for a in range(action_dim) if a not in env.schedule]
        q_vals = [np.dot(w, get_feature(state, a)) if a in valid else -np.inf for a in range(action_dim)]
        action = int(np.argmax(q_vals))
        next_state, _, done, _ = env.step(action)
        state = next_state

    week_start = month_start
    relocated = []
    for idx, start_min in zip(env.schedule, env.start_times):
        task = task_list[idx]
        start_dt = week_start + timedelta(minutes=start_min)

        # 원본 task를 복사하여 start_time만 교체
        updated = task.copy()
        updated["start_time"] = start_dt.strftime("%Y-%m-%d %H:%M:%S")
        relocated.append(updated)
    return relocated