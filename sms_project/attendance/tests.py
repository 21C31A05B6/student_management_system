from django.test import TestCase, Client
from django.urls import reverse

from academics.models import Department, Course, Section, Subject
from accounts.models import User
from teachers.models import Teacher


class TeacherAuthorizationTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.department = Department.objects.create(code='CSE', name='Computer Science')
        self.course = Course.objects.create(department=self.department, name='B.Tech CSE', duration_years=4)
        self.section = Section.objects.create(course=self.course, year=1, semester=1, name='A')

        self.teacher_user = User.objects.create_user(username='teacher1', password='pass1234', role='TEACHER')
        self.teacher_profile = Teacher.objects.create(
            user=self.teacher_user,
            teacher_id='T001',
            department=self.department,
        )

        self.other_teacher_user = User.objects.create_user(username='teacher2', password='pass1234', role='TEACHER')
        self.other_teacher_profile = Teacher.objects.create(
            user=self.other_teacher_user,
            teacher_id='T002',
            department=self.department,
        )

        self.subject_owned = Subject.objects.create(
            code='CS101',
            name='Programming',
            department=self.department,
            semester=1,
        )
        self.subject_owned.teachers.add(self.teacher_profile)

        self.subject_unassigned = Subject.objects.create(
            code='CS102',
            name='Database',
            department=self.department,
            semester=1,
        )
        self.subject_unassigned.teachers.add(self.other_teacher_profile)

    def test_teacher_cannot_access_unassigned_subject_in_attendance(self):
        self.client.force_login(self.teacher_user)
        response = self.client.get(
            reverse('attendance:mark'),
            {'section': self.section.id, 'subject': self.subject_unassigned.id, 'date': '2026-08-15'}
        )

        self.assertEqual(response.status_code, 403)
