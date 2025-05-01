from django import forms
from .models import Schedule

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = [
            'task_name',
            'duration_minutes',
            'difficulty',
            'importance',
            'task_type',
            'subject',
            'is_exam_task',
            'exam',
            'deadline',
            'start_time',
            'end_time',
            'is_fixed',
        ]
        widgets = {
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # exam 항목은 자기 자신을 참조하므로, 자신은 선택지에서 제외
        if self.instance.pk:
            self.fields['exam'].queryset = Schedule.objects.exclude(pk=self.instance.pk)
