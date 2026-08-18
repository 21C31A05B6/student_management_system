from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'method', 'path', 'status_code', 'timestamp')
    list_filter = ('method', 'status_code')
