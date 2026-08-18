from django.db import models
from django.conf import settings


class ParentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='parent_profile')
    children = models.ManyToManyField('students.Student', related_name='parent_profiles', blank=True)
    relation = models.CharField(max_length=30, default='Guardian')

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.relation})"
