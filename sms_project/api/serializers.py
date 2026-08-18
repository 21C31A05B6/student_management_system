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
        # Only re-run the marks-range check (0 <= marks_obtained <= max_marks)
        # here — NOT a full model.full_clean(), which would also re-run
        # validate_unique() on a freshly-constructed (unsaved) Mark object.
        # Django's uniqueness check only excludes "self" when the instance
        # was fetched from the DB (_state.adding == False); a bare
        # Mark(pk=..., ...) constructor call is always "adding", so it would
        # incorrectly flag the very row being updated as a duplicate.
        # DRF's own auto-generated UniqueTogetherValidator already handles
        # the (student, exam_subject) uniqueness correctly for updates.
        exam_subject = attrs.get('exam_subject', getattr(self.instance, 'exam_subject', None))
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
    due_amount = serializers.ReadOnlyField()
    status = serializers.ReadOnlyField()

    class Meta:
        model = FeeRecord
        fields = ['id', 'student', 'academic_year', 'total_amount', 'paid_amount', 'due_amount', 'status']
