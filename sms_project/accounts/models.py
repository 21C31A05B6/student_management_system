from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user with a role. Role-based access controls what each
    user can see/do across the whole system (Module 1 - Authentication)."""

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        TEACHER = 'TEACHER', 'Teacher'
        STUDENT = 'STUDENT', 'Student'
        PARENT = 'PARENT', 'Parent'

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)
    phone = models.CharField(max_length=20, blank=True)

    def is_admin(self):
        return self.role == self.Role.ADMIN

    def is_teacher(self):
        return self.role == self.Role.TEACHER

    def is_student(self):
        return self.role == self.Role.STUDENT

    def is_parent(self):
        return self.role == self.Role.PARENT

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
