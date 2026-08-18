from django.db import models
from django.conf import settings


class Teacher(models.Model):
    """Module 3 - Teacher Management."""
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        INACTIVE = 'INACTIVE', 'Inactive'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teacher_profile')
    teacher_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey('academics.Department', on_delete=models.SET_NULL, null=True, related_name='teachers')
    qualification = models.CharField(max_length=150, blank=True)
    joining_date = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to='teacher_photos/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        ordering = ['teacher_id']

    def __str__(self):
        return f"{self.teacher_id} - {self.user.get_full_name() or self.user.username}"
