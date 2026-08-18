from django.core.exceptions import ValidationError
from django.test import TestCase

from academics.models import Department, Course, Section
from accounts.models import User
from students.models import Student
from .models import Room, HostelAllocation


class HostelCapacityTests(TestCase):
    """Priority 1, issue #12: room capacity must be enforced server-side."""

    def setUp(self):
        self.department = Department.objects.create(code='CSE', name='Computer Science')
        self.course = Course.objects.create(department=self.department, name='B.Tech CSE', duration_years=4)
        self.section = Section.objects.create(course=self.course, year=1, semester=1, name='A')
        self.room = Room.objects.create(block='A', room_number='101', capacity=2)

        self.students = []
        for i in range(3):
            user = User.objects.create_user(username=f'hstu{i}', password='pass1234', role='STUDENT')
            student = Student.objects.create(
                user=user, student_id=f'H00{i}', department=self.department,
                course=self.course, section=self.section, year=1, semester=1,
            )
            self.students.append(student)

    def test_allocation_within_capacity_succeeds(self):
        HostelAllocation.objects.create(student=self.students[0], room=self.room)
        HostelAllocation.objects.create(student=self.students[1], room=self.room)
        self.assertEqual(self.room.occupied, 2)

    def test_allocation_exceeding_capacity_rejected(self):
        HostelAllocation.objects.create(student=self.students[0], room=self.room)
        HostelAllocation.objects.create(student=self.students[1], room=self.room)
        with self.assertRaises(ValidationError):
            HostelAllocation.objects.create(student=self.students[2], room=self.room)

    def test_student_cannot_have_two_active_allocations(self):
        room2 = Room.objects.create(block='B', room_number='201', capacity=2)
        HostelAllocation.objects.create(student=self.students[0], room=self.room)
        with self.assertRaises(ValidationError):
            HostelAllocation.objects.create(student=self.students[0], room=room2)

    def test_room_frees_up_after_vacating(self):
        alloc1 = HostelAllocation.objects.create(student=self.students[0], room=self.room)
        HostelAllocation.objects.create(student=self.students[1], room=self.room)
        import datetime
        alloc1.vacated_date = datetime.date.today()
        alloc1.save()
        self.assertEqual(self.room.occupied, 1)
        # Now a third student can move in.
        HostelAllocation.objects.create(student=self.students[2], room=self.room)
        self.assertEqual(self.room.occupied, 2)

    def test_student_can_be_reallocated_after_vacating(self):
        """A OneToOneField would block this — student is now a plain FK."""
        import datetime
        alloc1 = HostelAllocation.objects.create(student=self.students[0], room=self.room)
        alloc1.vacated_date = datetime.date.today()
        alloc1.save()
        room2 = Room.objects.create(block='B', room_number='202', capacity=1)
        alloc2 = HostelAllocation.objects.create(student=self.students[0], room=room2)
        self.assertIsNotNone(alloc2.pk)
