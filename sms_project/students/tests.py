from django.core.exceptions import ValidationError
from django.test import TestCase, Client

from academics.models import Department, Course, Section
from accounts.models import User
from .models import Student
from .forms import StudentForm


class StudentManagementTests(TestCase):
    """Priority 3, issue #17: student CRUD + permission coverage."""

    def setUp(self):
        self.client = Client()
        self.department = Department.objects.create(code='CSE', name='Computer Science')
        self.course = Course.objects.create(department=self.department, name='B.Tech CSE', duration_years=4)
        self.section = Section.objects.create(course=self.course, year=1, semester=1, name='A')

        self.admin = User.objects.create_user(username='sadmin', password='pass1234', role='ADMIN', is_staff=True)

        self.student_user = User.objects.create_user(username='ownstudent', password='pass1234', role='STUDENT')
        self.student = Student.objects.create(
            user=self.student_user, student_id='S100', department=self.department,
            course=self.course, section=self.section, year=1, semester=1,
        )

    def test_admin_can_create_student(self):
        self.client.login(username='sadmin', password='pass1234')
        response = self.client.post('/students/add/', {
            'username': 'newstudent', 'first_name': 'New', 'last_name': 'Student', 'email': 'new@test.com',
            'password': 'somepass123', 'student_id': 'S200', 'department': self.department.id,
            'course': self.course.id, 'section': self.section.id, 'year': 1, 'semester': 1, 'status': 'ACTIVE',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Student.objects.filter(student_id='S200').exists())
        self.assertTrue(User.objects.filter(username='newstudent', role='STUDENT').exists())

    def test_admin_can_update_student(self):
        self.client.login(username='sadmin', password='pass1234')
        response = self.client.post(f'/students/{self.student.pk}/edit/', {
            'username': self.student_user.username, 'first_name': 'Updated', 'last_name': 'Name',
            'email': 'updated@test.com', 'student_id': 'S100', 'department': self.department.id,
            'course': self.course.id, 'section': self.section.id, 'year': 2, 'semester': 3, 'status': 'ACTIVE',
        })
        self.assertEqual(response.status_code, 302)
        self.student.refresh_from_db()
        self.assertEqual(self.student.year, 2)
        self.student_user.refresh_from_db()
        self.assertEqual(self.student_user.first_name, 'Updated')

    def test_admin_can_delete_student_via_post(self):
        self.client.login(username='sadmin', password='pass1234')
        response = self.client.post(f'/students/{self.student.pk}/delete/')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Student.objects.filter(pk=self.student.pk).exists())
        self.assertFalse(User.objects.filter(pk=self.student_user.pk).exists())

    def test_get_on_delete_does_not_delete(self):
        """Priority 1, issue #11 regression guard."""
        self.client.login(username='sadmin', password='pass1234')
        response = self.client.get(f'/students/{self.student.pk}/delete/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Student.objects.filter(pk=self.student.pk).exists())

    def test_student_cannot_delete_other_student(self):
        self.client.login(username='ownstudent', password='pass1234')
        response = self.client.post(f'/students/{self.student.pk}/delete/')
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Student.objects.filter(pk=self.student.pk).exists())

    def test_student_can_view_own_profile(self):
        self.client.login(username='ownstudent', password='pass1234')
        response = self.client.get(f'/students/{self.student.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_student_cannot_view_another_students_profile(self):
        other_user = User.objects.create_user(username='otherstudent', password='pass1234', role='STUDENT')
        Student.objects.create(
            user=other_user, student_id='S300', department=self.department,
            course=self.course, section=self.section, year=1, semester=1,
        )
        self.client.login(username='ownstudent', password='pass1234')
        other_student = Student.objects.get(student_id='S300')
        response = self.client.get(f'/students/{other_student.pk}/')
        self.assertEqual(response.status_code, 403)

    def test_search_students_by_name(self):
        self.client.login(username='sadmin', password='pass1234')
        response = self.client.get('/students/?q=ownstudent')
        self.assertEqual(response.status_code, 200)

    def test_filter_students_by_department(self):
        self.client.login(username='sadmin', password='pass1234')
        response = self.client.get(f'/students/?department={self.department.id}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'S100')
