from django.db import models
from django.core.exceptions import ValidationError
# Create your models here.

class Schedule(models.Model):
    task_name=models.CharField(max_length=50)
    duration_minutes=models.IntegerField(null=True)
    difficulty=models.IntegerField(null=True)
    importance=models.IntegerField(null=True)
    task_type=models.CharField(max_length=50,blank=True)
    subject=models.CharField(max_length=50, blank=True)
    is_exam_task=models.BooleanField(default=False)
    deadline=models.DateTimeField(null=True ,blank=True)
    start_time=models.DateTimeField(null=True ,blank=True)
    end_time=models.DateTimeField(null=True ,blank=True)
    is_fixed=models.BooleanField(default=False)
    exam=models.ForeignKey('self',default=None, on_delete=models.SET_DEFAULT, null=True ,blank=True)
    def clean(self):
        # 조건: 시험 일정이면 deadline은 필수
        errors={}
        if self.is_exam_task and self.exam is None:
            errors['exam']='시험 일정이면 반드시 입력해야 합니다.'
        elif not self.is_exam_task and self.exam:
            errors['exam']='시험 일정이 아니면 입력할 수 없습니다.'
        if self.is_fixed and self.start_time is None:
            errors['start_time']='고정 일정이면 반드시 입력해야 합니다'
        if self.is_fixed and self.end_time is None:
            errors['end_time']='고정 일정이면 반드시 입력해야 합니다'
        raise ValidationError(errors)