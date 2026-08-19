from rest_framework import serializers
from students.models import Student
from teachers.models import Teacher
from academics.models import Department, Course, Subject
from attendance.models import AttendanceRecord
from exams.models import Exam, ExamSubject, Mark
from fees.models import FeeRecord


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'code', 'name']


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'department', 'duration_years']


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'code', 'name', 'department', 'semester', 'credits']


class StudentSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'student_id', 'name', 'email', 'department', 'course', 'section', 'year', 'semester', 'status']


class TeacherSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Teacher
        fields = ['id', 'teacher_id', 'name', 'email', 'department', 'status']


class AttendanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceRecord
        fields = ['id', 'student', 'subject', 'teacher', 'date', 'status']

    def validate(self, attrs):
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user.role == 'TEACHER':
            subject = attrs.get('subject', getattr(self.instance, 'subject', None))
            if subject and not subject.teachers.filter(user=request.user).exists():
                raise serializers.ValidationError({'subject': 'You are not assigned to teach this subject.'})
            if hasattr(request.user, 'teacher_profile'):
                attrs['teacher'] = request.user.teacher_profile
        return attrs


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ['id', 'name', 'academic_year', 'semester', 'date']


class ExamSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamSubject
        fields = ['id', 'exam', 'subject', 'max_marks']


class MarkSerializer(serializers.ModelSerializer):
    subject = serializers.PrimaryKeyRelatedField(source='exam_subject.subject', read_only=True)
    exam = serializers.PrimaryKeyRelatedField(source='exam_subject.exam', read_only=True)
    max_marks = serializers.ReadOnlyField()
    percentage = serializers.ReadOnlyField()
    grade = serializers.ReadOnlyField()

    class Meta:
        model = Mark
        fields = ['id', 'student', 'exam_subject', 'subject', 'exam', 'max_marks', 'marks_obtained', 'percentage', 'grade']

    def validate(self, attrs):
        request = self.context.get('request')
        exam_subject = attrs.get('exam_subject', getattr(self.instance, 'exam_subject', None))
        if request and request.user.is_authenticated and request.user.role == 'TEACHER':
            if exam_subject and not exam_subject.subject.teachers.filter(user=request.user).exists():
                raise serializers.ValidationError({'exam_subject': 'You are not assigned to teach this subject.'})

        marks_obtained = attrs.get('marks_obtained', getattr(self.instance, 'marks_obtained', None))
        if marks_obtained is not None:
            if marks_obtained < 0:
                raise serializers.ValidationError({'marks_obtained': 'Marks cannot be negative.'})
            if exam_subject and marks_obtained > exam_subject.max_marks:
                raise serializers.ValidationError({
                    'marks_obtained': f'Marks cannot exceed the maximum of {exam_subject.max_marks} for this subject.'
                })
        return attrs


class FeeRecordSerializer(serializers.ModelSerializer):
    paid_amount = serializers.ReadOnlyField()
    due_amount = serializers.ReadOnlyField()
    status = serializers.ReadOnlyField()

    class Meta:
        model = FeeRecord
        fields = ['id', 'student', 'academic_year', 'total_amount', 'paid_amount', 'due_amount', 'status']
        read_only_fields = ['paid_amount', 'due_amount', 'status']
