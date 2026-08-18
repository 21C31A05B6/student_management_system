from django.contrib import admin
from .models import AttendanceRecord


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'date', 'status', 'teacher')
    list_filter = ('subject', 'status', 'date')
    search_fields = ('student__student_id',)
