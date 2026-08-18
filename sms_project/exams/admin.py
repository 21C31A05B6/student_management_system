from django.contrib import admin
from .models import Exam, ExamSubject, Mark


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'academic_year', 'semester', 'date')
    list_filter = ('semester', 'academic_year')


@admin.register(ExamSubject)
class ExamSubjectAdmin(admin.ModelAdmin):
    list_display = ('exam', 'subject', 'max_marks')
    list_filter = ('exam',)


@admin.register(Mark)
class MarkAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'exam', 'marks_obtained', 'grade')
    list_filter = ('exam_subject__exam', 'exam_subject__subject')
    search_fields = ('student__student_id',)
