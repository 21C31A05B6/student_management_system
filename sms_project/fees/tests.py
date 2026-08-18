from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from academics.models import Department, Course
from fees.models import FeeRecord, Payment
from students.models import Student
from accounts.models import User


class FeeValidationTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(code='CSE', name='Computer Science')
        self.course = Course.objects.create(department=self.department, name='B.Tech CSE', duration_years=4)
        self.user = User.objects.create_user(username='student1', password='pass1234', role='STUDENT')
        self.student = Student.objects.create(
            user=self.user,
            student_id='S001',
            department=self.department,
            course=self.course,
            year=1,
            semester=1,
        )
        self.fee_record = FeeRecord.objects.create(
            student=self.student,
            academic_year='2025-2026',
            total_amount=Decimal('5000.00'),
            paid_amount=Decimal('0.00'),
        )
        Payment.objects.create(
            fee_record=self.fee_record,
            amount=Decimal('2000.00'),
            receipt_number='RCP-INIT',
        )

    def test_fee_record_rejects_negative_or_overpaid_amounts(self):
        invalid_record = FeeRecord(
            student=self.student,
            academic_year='2026-2027',
            total_amount=Decimal('5000.00'),
            paid_amount=Decimal('6000.00'),
        )
        with self.assertRaises(ValidationError):
            invalid_record.full_clean()

        negative_record = FeeRecord(
            student=self.student,
            academic_year='2026-2027',
            total_amount=Decimal('-50.00'),
            paid_amount=Decimal('0.00'),
        )
        with self.assertRaises(ValidationError):
            negative_record.full_clean()

    def test_payment_over_limit_is_rejected(self):
        payment = Payment(
            fee_record=self.fee_record,
            amount=Decimal('4000.00'),
            receipt_number='RCP-001',
        )
        with self.assertRaises(ValidationError):
            payment.full_clean()

    def test_payment_amount_updates_fee_record_total(self):
        payment = Payment.objects.create(
            fee_record=self.fee_record,
            amount=Decimal('1500.00'),
            receipt_number='RCP-002',
        )
        self.fee_record.refresh_from_db()

        self.assertEqual(self.fee_record.paid_amount, Decimal('3500.00'))
        self.assertEqual(payment.fee_record.paid_amount, Decimal('3500.00'))
