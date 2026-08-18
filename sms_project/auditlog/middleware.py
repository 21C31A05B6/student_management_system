"""Logs every state-changing request (POST/PUT/PATCH/DELETE) by an
authenticated user, for accountability (Module: Audit Logs)."""

WRITE_METHODS = {'POST', 'PUT', 'PATCH', 'DELETE'}
SKIP_PREFIXES = ('/static/', '/media/')


class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            if (
                request.method in WRITE_METHODS
                and getattr(request, 'user', None) is not None
                and request.user.is_authenticated
                and not request.path.startswith(SKIP_PREFIXES)
            ):
                from .models import AuditLog
                AuditLog.objects.create(
                    user=request.user,
                    method=request.method,
                    path=request.path[:255],
                    status_code=response.status_code,
                    ip_address=request.META.get('REMOTE_ADDR'),
                )
        except Exception:
            # Never let audit logging break the actual request.
            pass
        return response
