from django.test import TestCase, Client
from django.urls import reverse

from academics.models import Department, Course, Section, Subject
from accounts.models import User
from assignments.models import Assignment
from teachers.models import Teacher


class AssignmentAuthorizationTests(TestCase):
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

        self.subject = Subject.objects.create(
            code='CS201',
            name='Data Structures',
            department=self.department,
            semester=2,
        )
        self.subject.teachers.add(self.other_teacher_profile)

        self.assignment = Assignment.objects.create(
            subject=self.subject,
            section=self.section,
            teacher=self.other_teacher_profile,
            title='Assignment 1',
            due_date='2026-08-20',
        )

    def test_teacher_cannot_access_other_teacher_assignment_submissions(self):
        self.client.force_login(self.teacher_user)
        response = self.client.get(reverse('assignments:submissions', kwargs={'pk': self.assignment.pk}))

        self.assertEqual(response.status_code, 403)
