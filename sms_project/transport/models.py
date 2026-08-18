from django.db import models


class Route(models.Model):
    name = models.CharField(max_length=100)
    vehicle_number = models.CharField(max_length=30)
    driver_name = models.CharField(max_length=100, blank=True)
    driver_phone = models.CharField(max_length=20, blank=True)
    capacity = models.PositiveIntegerField(default=40)

    def __str__(self):
        return f"{self.name} ({self.vehicle_number})"


class StudentTransport(models.Model):
    student = models.OneToOneField('students.Student', on_delete=models.CASCADE, related_name='transport')
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='students')
    pickup_point = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return f"{self.student.student_id} -> {self.route.name}"
