"""Role-based access decorators used across every app."""
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(*roles):
    """Restrict a view to specific roles, e.g. @role_required('ADMIN')."""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if request.user.role not in roles:
                raise PermissionDenied("You do not have permission to view this page.")
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


admin_required = role_required('ADMIN')
teacher_required = role_required('ADMIN', 'TEACHER')
student_required = role_required('ADMIN', 'STUDENT')
parent_required = role_required('ADMIN', 'PARENT')
