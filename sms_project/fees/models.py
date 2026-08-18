from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum


class FeeRecord(models.Model):
    """Module 7 - Fees Management."""

    class PaymentStatus(models.TextChoices):
        PAID = 'PAID', 'Paid'
        PARTIAL = 'PARTIAL', 'Partially Paid'
        UNPAID = 'UNPAID', 'Unpaid'

    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='fee_records')
    academic_year = models.CharField(max_length=20)  # e.g. 2025-2026
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ('student', 'academic_year')
        ordering = ['-academic_year']

    def clean(self):
        if self.total_amount < 0:
            raise ValidationError({'total_amount': 'Total amount cannot be negative.'})
        if self.paid_amount < 0:
            raise ValidationError({'paid_amount': 'Paid amount cannot be negative.'})
        if self.paid_amount > self.total_amount:
            raise ValidationError({'paid_amount': 'Paid amount cannot exceed the total fee amount.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def due_amount(self):
        return self.total_amount - self.paid_amount

    @property
    def status(self):
        if self.paid_amount <= 0:
            return self.PaymentStatus.UNPAID
        if self.paid_amount >= self.total_amount:
            return self.PaymentStatus.PAID
        return self.PaymentStatus.PARTIAL

    def __str__(self):
        return f"{self.student.student_id} - {self.academic_year} - {self.status}"


class Payment(models.Model):
    """A single payment transaction against a FeeRecord."""

    class Method(models.TextChoices):
        CASH = 'CASH', 'Cash'
        CARD = 'CARD', 'Card'
        UPI = 'UPI', 'UPI'
        BANK_TRANSFER = 'BANK', 'Bank Transfer'

    fee_record = models.ForeignKey(FeeRecord, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    method = models.CharField(max_length=10, choices=Method.choices, default=Method.CASH)
    receipt_number = models.CharField(max_length=30, unique=True)

    class Meta:
        ordering = ['-payment_date']

    def clean(self):
        if self.amount <= 0:
            raise ValidationError({'amount': 'Payment amount must be greater than zero.'})
        # When editing an existing payment, exclude its own current amount
        # from "already paid" before checking against the outstanding
        # balance — otherwise a valid edit (e.g. correcting a typo upward)
        # gets rejected against its own prior value.
        already_paid = self.fee_record.paid_amount
        if self.pk:
            previous_amount = Payment.objects.filter(pk=self.pk).values_list('amount', flat=True).first() or Decimal('0')
            already_paid -= previous_amount
        outstanding = self.fee_record.total_amount - already_paid
        if self.amount > outstanding:
            raise ValidationError({'amount': 'Payment amount exceeds the outstanding fee balance.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        self._recalculate_fee_record()

    def delete(self, *args, **kwargs):
        """Priority 1, issue #4: deleting a payment must also update the
        parent FeeRecord's paid_amount — otherwise it goes stale."""
        fee_record = self.fee_record
        super().delete(*args, **kwargs)
        fee_record.paid_amount = fee_record.payments.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        fee_record.save(update_fields=['paid_amount'])

    def _recalculate_fee_record(self):
        fee_record = self.fee_record
        total_paid = fee_record.payments.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        fee_record.paid_amount = total_paid
        fee_record.save(update_fields=['paid_amount'])

    def __str__(self):
        return f"Receipt {self.receipt_number} - {self.amount}"
