from django.db import models


class AcademicEvent(models.Model):
    class Category(models.TextChoices):
        HOLIDAY = 'HOLIDAY', 'Holiday'
        EXAM = 'EXAM', 'Exam'
        EVENT = 'EVENT', 'Event'
        DEADLINE = 'DEADLINE', 'Deadline'

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=10, choices=Category.choices, default=Category.EVENT)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        return f"{self.title} ({self.start_date})"
