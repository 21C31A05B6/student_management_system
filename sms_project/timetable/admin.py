from django.contrib import admin
from .models import TimetableEntry


@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):
    list_display = ('section', 'subject', 'teacher', 'day_of_week', 'start_time', 'end_time')
    list_filter = ('section', 'day_of_week')
