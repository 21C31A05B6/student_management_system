"""API permission classes.

Priority 1, issue #2: a ModelViewSet exposes GET/POST/PUT/PATCH/DELETE by
default. Filtering the queryset to "your own records" is NOT enough — it
still lets a student PATCH or DELETE their own attendance/marks. These
classes explicitly separate read access (who may see the endpoint at all)
from write access (who may create/modify/delete), matching:

    Admin   -> GET, POST, PUT, PATCH, DELETE
    Teacher -> GET, POST, PATCH               (no PUT, no DELETE)
    Student -> GET only
    Parent  -> GET only

Every ViewSet combines one "who can access this endpoint" class with one of
the write-permission classes below (DRF ANDs multiple permission_classes).
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ADMIN'


class IsAdminOrTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ('ADMIN', 'TEACHER')


class IsStudentSelfOrParentOrAdminOrTeacher(BasePermission):
    """Endpoint-access gate. Object-level filtering (which rows) still
    happens in each ViewSet's get_queryset()."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in ('ADMIN', 'TEACHER', 'STUDENT', 'PARENT')


class IsParentOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in ('ADMIN', 'PARENT')


class IsAdminOrReadOnly(BasePermission):
    """Only Admin may write (POST/PUT/PATCH/DELETE). Anyone else who passed
    the endpoint-access gate may only read (GET/HEAD/OPTIONS)."""
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'ADMIN'


class IsAdminOrTeacherWriteReadOnlyOthers(BasePermission):
    """Admin: full write. Teacher: POST/PATCH only (no PUT, no DELETE — a
    teacher can add/update attendance or marks but never bulk-replace or
    delete records). Student/Parent: read-only."""
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        role = request.user.role
        if role == 'ADMIN':
            return True
        if role == 'TEACHER':
            return request.method in ('POST', 'PATCH')
        return False
