from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'user', 'department', 'course', 'section', 'year', 'status')
    list_filter = ('department', 'course', 'year', 'status')
    search_fields = ('student_id', 'user__first_name', 'user__last_name')
