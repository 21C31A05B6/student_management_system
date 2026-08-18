import uuid
from django.db import models
from django.conf import settings


class Student(models.Model):
    """Module 2 - Student Management."""

    class Gender(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
        OTHER = 'O', 'Other'

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        INACTIVE = 'INACTIVE', 'Inactive'
        GRADUATED = 'GRADUATED', 'Graduated'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True)
    qr_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=Gender.choices, blank=True)
    address = models.TextField(blank=True)
    photo = models.ImageField(upload_to='student_photos/', null=True, blank=True)

    department = models.ForeignKey('academics.Department', on_delete=models.SET_NULL, null=True, related_name='students')
    course = models.ForeignKey('academics.Course', on_delete=models.SET_NULL, null=True, related_name='students')
    section = models.ForeignKey('academics.Section', on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    year = models.PositiveSmallIntegerField(default=1)
    semester = models.PositiveSmallIntegerField(default=1)

    admission_date = models.DateField(null=True, blank=True)
    parent_name = models.CharField(max_length=150, blank=True)
    parent_phone = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        ordering = ['student_id']

    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name() or self.user.username}"
