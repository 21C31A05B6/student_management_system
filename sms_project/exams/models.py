from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models


class Exam(models.Model):
    """Module 6 - Examination Management (e.g. Internal 1, Midterm, Semester).

    An Exam no longer carries a single max_marks — different subjects can
    have different maximum marks within the same exam (e.g. DBMS out of 100,
    a lab subject out of 50). Per-subject maximums live on ExamSubject.
    """
    name = models.CharField(max_length=100)  # Internal 1, Midterm, Semester
    academic_year = models.CharField(max_length=20, default='2025-2026', help_text="e.g. 2025-2026")
    date = models.DateField(null=True, blank=True)
    semester = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.name} (Sem {self.semester}, {self.academic_year})"


class ExamSubject(models.Model):
    """A subject as examined within a specific Exam, carrying its own
    max_marks (Academic Year -> Exam -> ExamSubject -> Marks)."""
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_subjects')
    subject = models.ForeignKey('academics.Subject', on_delete=models.CASCADE, related_name='exam_subjects')
    max_marks = models.PositiveIntegerField(default=100)

    class Meta:
        unique_together = ('exam', 'subject')
        ordering = ['exam', 'subject']

    def __str__(self):
        return f"{self.exam.name} - {self.subject.code} (out of {self.max_marks})"


class Mark(models.Model):
    """Marks for a student in a given exam-subject."""
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='marks')
    exam_subject = models.ForeignKey(ExamSubject, on_delete=models.CASCADE, related_name='marks')
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ('student', 'exam_subject')
        ordering = ['-exam_subject__exam__date']

    # --- Backward-compatible accessors (subject/exam used throughout the
    # rest of the app — this avoids having to touch every template/serializer
    # that reads mark.subject or mark.exam). ---
    @property
    def subject(self):
        return self.exam_subject.subject

    @property
    def exam(self):
        return self.exam_subject.exam

    @property
    def max_marks(self):
        return self.exam_subject.max_marks

    def clean(self):
        if self.marks_obtained is None:
            return
        if self.marks_obtained < 0:
            raise ValidationError({'marks_obtained': 'Marks cannot be negative.'})
        if self.exam_subject_id and self.marks_obtained > self.exam_subject.max_marks:
            raise ValidationError({
                'marks_obtained': f'Marks cannot exceed the maximum of {self.exam_subject.max_marks} for this subject.'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def percentage(self):
        max_marks = self.exam_subject.max_marks
        if max_marks:
            return round((float(self.marks_obtained) / max_marks) * 100, 2)
        return 0

    @property
    def grade(self):
        p = self.percentage
        if p >= 90:
            return 'A+'
        if p >= 80:
            return 'A'
        if p >= 70:
            return 'B'
        if p >= 60:
            return 'C'
        if p >= 50:
            return 'D'
        return 'F'

    # --- GPA support (Priority 2, issue #8) ---
    GRADE_POINTS = {'A+': 10, 'A': 9, 'B': 8, 'C': 7, 'D': 6, 'F': 0}

    @property
    def grade_point(self):
        return self.GRADE_POINTS.get(self.grade, 0)

    def __str__(self):
        return f"{self.student.student_id} - {self.subject.code} - {self.exam.name}: {self.marks_obtained}"


def calculate_gpa(marks_queryset):
    """GPA = Σ(credit × grade_point) / Σ credits, for a queryset of Mark
    objects belonging to a single exam (so it represents that exam's GPA)."""
    total_credits = Decimal('0')
    weighted_points = Decimal('0')
    for mark in marks_queryset.select_related('exam_subject__subject'):
        credits = Decimal(mark.subject.credits or 0)
        total_credits += credits
        weighted_points += credits * Decimal(mark.grade_point)
    if total_credits == 0:
        return None
    return round(weighted_points / total_credits, 2)


def calculate_cgpa(student):
    """CGPA = credit-weighted average GPA across every exam the student has
    marks for (Priority 2, issue #8)."""
    from django.db.models import Count
    exam_ids = Mark.objects.filter(student=student).values_list('exam_subject__exam_id', flat=True).distinct()
    total_credits = Decimal('0')
    weighted_points = Decimal('0')
    for exam_id in exam_ids:
        marks = Mark.objects.filter(student=student, exam_subject__exam_id=exam_id)
        for mark in marks.select_related('exam_subject__subject'):
            credits = Decimal(mark.subject.credits or 0)
            total_credits += credits
            weighted_points += credits * Decimal(mark.grade_point)
    if total_credits == 0:
        return None
    return round(weighted_points / total_credits, 2)
