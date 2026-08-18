import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase

from academics.models import Department, Course, Section, Subject
from accounts.models import User
from teachers.models import Teacher
from .models import TimetableEntry


class TimetableConflictTests(TestCase):
    """Priority 1, issue #9: prevent double-booking a section, teacher, or
    room into overlapping time slots on the same day."""

    def setUp(self):
        self.department = Department.objects.create(code='CSE', name='Computer Science')
        self.course = Course.objects.create(department=self.department, name='B.Tech CSE', duration_years=4)
        self.section_a = Section.objects.create(course=self.course, year=1, semester=1, name='A')
        self.section_b = Section.objects.create(course=self.course, year=1, semester=1, name='B')

        self.subject1 = Subject.objects.create(code='CS101', name='DBMS', department=self.department, semester=1)
        self.subject2 = Subject.objects.create(code='CS102', name='Java', department=self.department, semester=1)

        self.teacher_user = User.objects.create_user(username='ravi', password='pass1234', role='TEACHER')
        self.teacher = Teacher.objects.create(user=self.teacher_user, teacher_id='T001', department=self.department)

        TimetableEntry.objects.create(
            section=self.section_a, subject=self.subject1, teacher=self.teacher, room_number='101',
            day_of_week=1, start_time=datetime.time(10, 0), end_time=datetime.time(11, 0),
        )

    def test_overlapping_section_slot_rejected(self):
        entry = TimetableEntry(
            section=self.section_a, subject=self.subject2, teacher=None, room_number='102',
            day_of_week=1, start_time=datetime.time(10, 30), end_time=datetime.time(11, 30),
        )
        with self.assertRaises(ValidationError):
            entry.save()

    def test_overlapping_teacher_slot_rejected(self):
        entry = TimetableEntry(
            section=self.section_b, subject=self.subject2, teacher=self.teacher, room_number='102',
            day_of_week=1, start_time=datetime.time(10, 0), end_time=datetime.time(11, 0),
        )
        with self.assertRaises(ValidationError):
            entry.save()

    def test_overlapping_room_slot_rejected(self):
        entry = TimetableEntry(
            section=self.section_b, subject=self.subject2, teacher=None, room_number='101',
            day_of_week=1, start_time=datetime.time(10, 30), end_time=datetime.time(11, 30),
        )
        with self.assertRaises(ValidationError):
            entry.save()

    def test_non_overlapping_slot_accepted(self):
        entry = TimetableEntry.objects.create(
            section=self.section_a, subject=self.subject2, teacher=self.teacher, room_number='101',
            day_of_week=1, start_time=datetime.time(11, 0), end_time=datetime.time(12, 0),
        )
        self.assertIsNotNone(entry.pk)

    def test_different_day_same_time_accepted(self):
        entry = TimetableEntry.objects.create(
            section=self.section_a, subject=self.subject2, teacher=self.teacher, room_number='101',
            day_of_week=2, start_time=datetime.time(10, 0), end_time=datetime.time(11, 0),
        )
        self.assertIsNotNone(entry.pk)

    def test_end_time_before_start_time_rejected(self):
        entry = TimetableEntry(
            section=self.section_b, subject=self.subject2, teacher=None,
            day_of_week=3, start_time=datetime.time(12, 0), end_time=datetime.time(11, 0),
        )
        with self.assertRaises(ValidationError):
            entry.save()
