from django.contrib import admin
from .models import Schedule
# Register your models here.
# admin.site.register(Schedule)

class ScheduleAdmin(admin.ModelAdmin):
    search_fields = ['task_name', 'task_type', 'subject']

admin.site.register(Schedule, ScheduleAdmin)