from django.shortcuts import render
from accounts.decorators import admin_required
from .models import AuditLog


@admin_required
def audit_log_list(request):
    logs = AuditLog.objects.select_related('user').all()[:300]
    return render(request, 'auditlog/list.html', {'logs': logs})
