from django.db import models
from django.conf import settings


class Announcement(models.Model):
    class Audience(models.TextChoices):
        ALL = 'ALL', 'Everyone'
        TEACHERS = 'TEACHERS', 'Teachers Only'
        STUDENTS = 'STUDENTS', 'Students Only'

    title = models.CharField(max_length=200)
    body = models.TextField()
    audience = models.CharField(max_length=10, choices=Audience.choices, default=Audience.ALL)
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    pinned = models.BooleanField(default=False)

    class Meta:
        ordering = ['-pinned', '-created_at']

    def __str__(self):
        return self.title
