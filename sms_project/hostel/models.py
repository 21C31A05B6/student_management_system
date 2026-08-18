from django.core.exceptions import ValidationError
from django.db import models


class Room(models.Model):
    class RoomType(models.TextChoices):
        SINGLE = 'SINGLE', 'Single'
        SHARED = 'SHARED', 'Shared'
        DORM = 'DORM', 'Dormitory'

    block = models.CharField(max_length=50)
    room_number = models.CharField(max_length=20)
    room_type = models.CharField(max_length=10, choices=RoomType.choices, default=RoomType.SHARED)
    capacity = models.PositiveIntegerField(default=2)

    class Meta:
        unique_together = ('block', 'room_number')

    @property
    def occupied(self):
        return self.allocations.filter(vacated_date__isnull=True).count()

    @property
    def has_space(self):
        return self.occupied < self.capacity

    def __str__(self):
        return f"{self.block}-{self.room_number}"


class HostelAllocation(models.Model):
    """Priority 1, issue #12: a room's capacity must be enforced server-side,
    not just hinted at in the UI. Also: student is a plain ForeignKey (not
    OneToOne) so a student can have a new allocation after vacating a
    previous room — full allocation history is preserved."""
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='hostel_allocations')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='allocations')
    allocated_date = models.DateField(auto_now_add=True)
    vacated_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-allocated_date']

    def clean(self):
        if self.vacated_date:
            return  # nothing to validate for a closed-out allocation
        if self.room_id:
            occupied = self.room.allocations.filter(vacated_date__isnull=True).exclude(pk=self.pk).count()
            if occupied >= self.room.capacity:
                raise ValidationError({'room': f'Room {self.room} is already at full capacity ({self.room.capacity}).'})
        if self.student_id:
            already_allocated = HostelAllocation.objects.filter(
                student=self.student, vacated_date__isnull=True
            ).exclude(pk=self.pk).exists()
            if already_allocated:
                raise ValidationError({'student': 'This student already has an active room allocation.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.student_id} -> {self.room}"
