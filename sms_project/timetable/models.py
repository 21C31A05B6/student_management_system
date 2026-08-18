from django.core.exceptions import ValidationError
from django.db import models


class TimetableEntry(models.Model):
    """Module 8 - Timetable Management."""

    class Day(models.IntegerChoices):
        MONDAY = 1, 'Monday'
        TUESDAY = 2, 'Tuesday'
        WEDNESDAY = 3, 'Wednesday'
        THURSDAY = 4, 'Thursday'
        FRIDAY = 5, 'Friday'
        SATURDAY = 6, 'Saturday'

    section = models.ForeignKey('academics.Section', on_delete=models.CASCADE, related_name='timetable_entries')
    subject = models.ForeignKey('academics.Subject', on_delete=models.CASCADE, related_name='timetable_entries')
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name='timetable_entries')
    room_number = models.CharField(max_length=30, blank=True)
    day_of_week = models.PositiveSmallIntegerField(choices=Day.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ['day_of_week', 'start_time']

    def clean(self):
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError({'end_time': 'End time must be after start time.'})
        if not (self.day_of_week and self.start_time and self.end_time):
            return

        # Priority 1, issue #9: prevent double-booking a section, teacher, or
        # room into overlapping time slots on the same day.
        overlapping = TimetableEntry.objects.filter(
            day_of_week=self.day_of_week,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        ).exclude(pk=self.pk)

        section_clash = overlapping.filter(section=self.section).first()
        if section_clash:
            raise ValidationError(
                f'{self.section} already has {section_clash.subject.code} '
                f'from {section_clash.start_time}-{section_clash.end_time} on {self.get_day_of_week_display()}.'
            )

        if self.teacher_id:
            teacher_clash = overlapping.filter(teacher_id=self.teacher_id).first()
            if teacher_clash:
                raise ValidationError(
                    f'{self.teacher} is already teaching {teacher_clash.subject.code} to '
                    f'{teacher_clash.section} from {teacher_clash.start_time}-{teacher_clash.end_time} '
                    f'on {self.get_day_of_week_display()}.'
                )

        if self.room_number:
            room_clash = overlapping.filter(room_number=self.room_number).first()
            if room_clash:
                raise ValidationError(
                    f'Room {self.room_number} is already booked for {room_clash.subject.code} '
                    f'from {room_clash.start_time}-{room_clash.end_time} on {self.get_day_of_week_display()}.'
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.section} - {self.subject.code} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"
