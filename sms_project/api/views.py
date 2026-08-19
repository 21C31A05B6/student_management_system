from rest_framework import viewsets

from students.models import Student
from teachers.models import Teacher
from academics.models import Department, Course, Subject
from attendance.models import AttendanceRecord
from exams.models import Exam, ExamSubject, Mark
from fees.models import FeeRecord

from . import serializers
from .permissions import (
    IsAdminOrTeacher, IsAdminOnly, IsStudentSelfOrParentOrAdminOrTeacher, IsParentOrAdmin,
    IsAdminOrReadOnly, IsAdminOrTeacherWriteReadOnlyOthers,
)


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = serializers.DepartmentSerializer
    permission_classes = [IsAdminOnly]


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = serializers.CourseSerializer
    permission_classes = [IsAdminOnly]


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = serializers.SubjectSerializer
    permission_classes = [IsAdminOrTeacher, IsAdminOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == 'TEACHER' and hasattr(user, 'teacher_profile'):
            qs = qs.filter(teachers=user.teacher_profile)
        return qs


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related('user', 'department', 'course', 'section').all()
    serializer_class = serializers.StudentSerializer
    permission_classes = [IsStudentSelfOrParentOrAdminOrTeacher, IsAdminOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == 'ADMIN':
            return qs
        if user.role == 'STUDENT' and hasattr(user, 'student_profile'):
            return qs.filter(user=user)
        if user.role == 'PARENT' and hasattr(user, 'parent_profile'):
            parent_profile = user.parent_profile
            return qs.filter(id__in=parent_profile.children.all())
        if user.role == 'TEACHER' and hasattr(user, 'teacher_profile'):
            return qs.filter(section__subjects__teachers=user.teacher_profile).distinct()
        return qs.none()


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.select_related('user', 'department').all()
    serializer_class = serializers.TeacherSerializer
    permission_classes = [IsAdminOnly]


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = AttendanceRecord.objects.all()
    serializer_class = serializers.AttendanceRecordSerializer
    permission_classes = [IsStudentSelfOrParentOrAdminOrTeacher, IsAdminOrTeacherWriteReadOnlyOthers]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == 'ADMIN':
            return qs
        if user.role == 'STUDENT' and hasattr(user, 'student_profile'):
            return qs.filter(student=user.student_profile)
        if user.role == 'PARENT' and hasattr(user, 'parent_profile'):
            parent_profile = user.parent_profile
            student_ids = parent_profile.children.all().values_list('id', flat=True)
            return qs.filter(student__id__in=student_ids)
        if user.role == 'TEACHER' and hasattr(user, 'teacher_profile'):
            return qs.filter(subject__teachers=user.teacher_profile)
        return qs.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'TEACHER' and hasattr(user, 'teacher_profile'):
            serializer.save(teacher=user.teacher_profile)
        else:
            serializer.save()


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = serializers.ExamSerializer
    permission_classes = [IsAdminOrTeacher, IsAdminOrReadOnly]


class ExamSubjectViewSet(viewsets.ModelViewSet):
    queryset = ExamSubject.objects.all()
    serializer_class = serializers.ExamSubjectSerializer
    permission_classes = [IsAdminOrTeacher, IsAdminOrReadOnly]


class MarkViewSet(viewsets.ModelViewSet):
    queryset = Mark.objects.all()
    serializer_class = serializers.MarkSerializer
    permission_classes = [IsStudentSelfOrParentOrAdminOrTeacher, IsAdminOrTeacherWriteReadOnlyOthers]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == 'ADMIN':
            return qs
        if user.role == 'STUDENT' and hasattr(user, 'student_profile'):
            return qs.filter(student=user.student_profile)
        if user.role == 'PARENT' and hasattr(user, 'parent_profile'):
            parent_profile = user.parent_profile
            student_ids = parent_profile.children.all().values_list('id', flat=True)
            return qs.filter(student__id__in=student_ids)
        if user.role == 'TEACHER' and hasattr(user, 'teacher_profile'):
            return qs.filter(exam_subject__subject__teachers=user.teacher_profile)
        return qs.none()


class FeeRecordViewSet(viewsets.ModelViewSet):
    queryset = FeeRecord.objects.all()
    serializer_class = serializers.FeeRecordSerializer
    permission_classes = [IsStudentSelfOrParentOrAdminOrTeacher, IsAdminOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == 'ADMIN':
            return qs
        if user.role == 'STUDENT' and hasattr(user, 'student_profile'):
            return qs.filter(student=user.student_profile)
        if user.role == 'PARENT' and hasattr(user, 'parent_profile'):
            parent_profile = user.parent_profile
            student_ids = parent_profile.children.all().values_list('id', flat=True)
            return qs.filter(student__id__in=student_ids)
        if user.role == 'TEACHER' and hasattr(user, 'teacher_profile'):
            return qs.filter(student__section__subjects__teachers=user.teacher_profile).distinct()
        return qs.none()
