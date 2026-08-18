import datetime
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from academics.models import Department, Course, Section
from accounts.models import User
from students.models import Student
from .models import Book, IssueBook


class LibraryFineTests(TestCase):
    """Priority 2, issue #13: fine = days_late * fine_per_day."""

    def setUp(self):
        self.department = Department.objects.create(code='CSE', name='Computer Science')
        self.course = Course.objects.create(department=self.department, name='B.Tech CSE', duration_years=4)
        self.section = Section.objects.create(course=self.course, year=1, semester=1, name='A')
        self.user = User.objects.create_user(username='libstu', password='pass1234', role='STUDENT')
        self.student = Student.objects.create(
            user=self.user, student_id='L001', department=self.department,
            course=self.course, section=self.section, year=1, semester=1,
        )
        self.book = Book.objects.create(title='Test Book', author='Author', quantity=2)

    def test_no_fine_when_returned_on_time(self):
        issue = IssueBook.objects.create(
            book=self.book, student=self.student,
            due_date=timezone.localdate() + datetime.timedelta(days=5),
            return_date=timezone.localdate(),
        )
        self.assertEqual(issue.days_late, 0)
        self.assertEqual(issue.fine_amount, Decimal('0'))

    def test_fine_accrues_for_late_return(self):
        issue = IssueBook.objects.create(
            book=self.book, student=self.student,
            due_date=timezone.localdate() - datetime.timedelta(days=5),
            return_date=timezone.localdate(),
        )
        self.assertEqual(issue.days_late, 5)
        self.assertEqual(issue.fine_amount, Decimal('25.00'))  # 5 days * ₹5/day

    def test_fine_accrues_daily_while_unreturned(self):
        issue = IssueBook.objects.create(
            book=self.book, student=self.student,
            due_date=timezone.localdate() - datetime.timedelta(days=3),
        )
        self.assertTrue(issue.is_overdue)
        self.assertEqual(issue.days_late, 3)
        self.assertEqual(issue.fine_amount, Decimal('15.00'))

    def test_available_copies_decreases_on_issue(self):
        self.assertEqual(self.book.available_copies, 2)
        IssueBook.objects.create(
            book=self.book, student=self.student,
            due_date=timezone.localdate() + datetime.timedelta(days=14),
        )
        self.assertEqual(self.book.available_copies, 1)

    def test_available_copies_restored_on_return(self):
        issue = IssueBook.objects.create(
            book=self.book, student=self.student,
            due_date=timezone.localdate() + datetime.timedelta(days=14),
        )
        self.assertEqual(self.book.available_copies, 1)
        issue.return_date = timezone.localdate()
        issue.save()
        self.assertEqual(self.book.available_copies, 2)
