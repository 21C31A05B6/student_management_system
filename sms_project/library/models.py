from decimal import Decimal

from django.db import models
from django.utils import timezone


class Book(models.Model):
    """Book catalog entry (mirrors the standalone libraryproject's library_book
    table: title, author, isbn, quantity)."""
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=20, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['title']

    @property
    def issued_count(self):
        return self.issues.filter(return_date__isnull=True).count()

    @property
    def available_copies(self):
        return self.quantity - self.issued_count

    def __str__(self):
        return self.title


class IssueBook(models.Model):
    """A book issued to a student. Uses the SMS's real students.Student model
    (not a separate library-only student record) so borrowing history shows
    up on the student's own profile and is visible to admins/teachers/parents
    exactly like attendance, marks, and fees."""
    FINE_PER_DAY = Decimal('5.00')  # Priority 2, issue #13: library fines

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='issues')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='book_issues')
    issued_by = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name='books_issued')
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(help_text="Expected return date")
    return_date = models.DateField(null=True, blank=True)
    fine_paid = models.BooleanField(default=False)

    class Meta:
        ordering = ['-issue_date']

    @property
    def is_returned(self):
        return self.return_date is not None

    @property
    def is_overdue(self):
        return not self.return_date and self.due_date < timezone.localdate()

    @property
    def days_late(self):
        """Days late, based on the return date if returned, otherwise today."""
        end = self.return_date or timezone.localdate()
        if end <= self.due_date:
            return 0
        return (end - self.due_date).days

    @property
    def fine_amount(self):
        return self.days_late * self.FINE_PER_DAY

    def __str__(self):
        return f"{self.book.title} -> {self.student.student_id}"
