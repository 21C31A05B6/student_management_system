from django.contrib import admin
from .models import Department, Course, Section, Subject


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'head_of_department')
    search_fields = ('code', 'name')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'duration_years')
    list_filter = ('department',)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('course', 'year', 'semester', 'name')
    list_filter = ('course', 'year')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'department', 'semester', 'credits')
    list_filter = ('department', 'semester')
    filter_horizontal = ('teachers', 'sections')
    search_fields = ('code', 'name')
