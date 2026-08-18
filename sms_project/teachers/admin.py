from django.contrib import admin
from .models import Teacher


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('teacher_id', 'user', 'department', 'status', 'joining_date')
    list_filter = ('department', 'status')
    search_fields = ('teacher_id', 'user__first_name', 'user__last_name')
