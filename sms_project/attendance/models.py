from django.db import models


class AttendanceRecord(models.Model):
    """Module 5 - Attendance Management. One row per student/subject/date."""

    class Status(models.TextChoices):
        PRESENT = 'PRESENT', 'Present'
        ABSENT = 'ABSENT', 'Absent'
        LATE = 'LATE', 'Late'

    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='attendance_records')
    subject = models.ForeignKey('academics.Subject', on_delete=models.CASCADE, related_name='attendance_records')
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, null=True, related_name='attendance_marked')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PRESENT)

    class Meta:
        unique_together = ('student', 'subject', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.student.student_id} - {self.subject.code} - {self.date} - {self.status}"
