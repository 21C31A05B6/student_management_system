from django.db import models


class Assignment(models.Model):
    subject = models.ForeignKey('academics.Subject', on_delete=models.CASCADE, related_name='assignments')
    section = models.ForeignKey('academics.Section', on_delete=models.CASCADE, related_name='assignments')
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, null=True, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    attachment = models.FileField(upload_to='assignments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-due_date']

    def __str__(self):
        return f"{self.title} ({self.subject.code})"


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='submissions')
    file = models.FileField(upload_to='submissions/', null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.CharField(max_length=10, blank=True)
    feedback = models.TextField(blank=True)

    class Meta:
        unique_together = ('assignment', 'student')

    def __str__(self):
        return f"{self.student.student_id} -> {self.assignment.title}"
