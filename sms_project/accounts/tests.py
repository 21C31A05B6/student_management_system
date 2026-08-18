from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import User


class AuthenticationTests(TestCase):
    """Priority 3, issue #17: authentication test coverage."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='authtest', password='correctpass123', role='ADMIN', is_staff=True)

    def test_login_with_correct_credentials_succeeds(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'authtest', 'password': 'correctpass123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated if hasattr(response, 'wsgi_request') else True)

    def test_login_with_wrong_password_fails(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'authtest', 'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)  # re-renders login form
        self.assertFalse(response.context['user'].is_authenticated if response.context else False)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_logout_clears_session(self):
        self.client.login(username='authtest', password='correctpass123')
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)

        self.client.get(reverse('accounts:logout'))
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 302)


class RoleRestrictionTests(TestCase):
    """Priority 3, issue #17: role-based page access."""

    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(username='roleadmin', password='pass1234', role='ADMIN', is_staff=True)
        self.teacher = User.objects.create_user(username='roleteacher', password='pass1234', role='TEACHER')
        self.student = User.objects.create_user(username='rolestudent', password='pass1234', role='STUDENT')

    def test_admin_can_access_department_management(self):
        self.client.login(username='roleadmin', password='pass1234')
        response = self.client.get('/academics/departments/')
        self.assertEqual(response.status_code, 200)

    def test_teacher_cannot_access_department_management(self):
        self.client.login(username='roleteacher', password='pass1234')
        response = self.client.get('/academics/departments/')
        self.assertEqual(response.status_code, 403)

    def test_student_cannot_access_department_management(self):
        self.client.login(username='rolestudent', password='pass1234')
        response = self.client.get('/academics/departments/')
        self.assertEqual(response.status_code, 403)

    def test_student_cannot_access_student_list(self):
        self.client.login(username='rolestudent', password='pass1234')
        response = self.client.get('/students/')
        self.assertEqual(response.status_code, 403)

    def test_teacher_can_access_student_list(self):
        self.client.login(username='roleteacher', password='pass1234')
        response = self.client.get('/students/')
        self.assertEqual(response.status_code, 200)
