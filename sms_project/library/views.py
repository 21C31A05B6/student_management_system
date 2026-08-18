from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.decorators import admin_required, teacher_required, student_required
from accounts.view_helpers import confirm_and_delete
from .models import Book, IssueBook
from .forms import BookForm, IssueBookForm


# ---------------- Book catalog ----------------
# Viewable by Admin + Teacher; only Admin can add/edit/delete.

@teacher_required
def book_list(request):
    books = Book.objects.all()
    return render(request, 'library/book_list.html', {'books': books})


@admin_required
def book_form(request, pk=None):
    book = get_object_or_404(Book, pk=pk) if pk else None
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book saved.')
            return redirect('library:book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'generic_form.html', {
        'form': form, 'heading': 'Edit Book' if book else 'Add Book', 'cancel_url': '/library/',
    })


@admin_required
def book_delete(request, pk):
    book = Book.objects.filter(pk=pk).first()
    return confirm_and_delete(
        request, book, 'library:book_list', '/library/',
        message='Issue history for this book will also be deleted.',
        success_message='Book deleted.',
    )


# ---------------- Issuing ----------------
# Admin and Teacher can both issue/return books (a teacher acting as librarian
# on duty); every issue is stamped with which staff member processed it.

@teacher_required
def issue_list(request):
    issues = IssueBook.objects.select_related('book', 'student', 'student__user', 'issued_by', 'issued_by__user').all()
    return render(request, 'library/issue_list.html', {'issues': issues})


@teacher_required
def issue_form(request):
    if request.method == 'POST':
        form = IssueBookForm(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.issued_by = getattr(request.user, 'teacher_profile', None)
            issue.save()
            messages.success(request, f'"{issue.book.title}" issued to {issue.student.user.get_full_name()}.')
            return redirect('library:issue_list')
    else:
        form = IssueBookForm()
    return render(request, 'generic_form.html', {
        'form': form, 'heading': 'Issue Book', 'cancel_url': '/library/issues/',
    })


@teacher_required
@require_POST
def issue_return(request, pk):
    issue = get_object_or_404(IssueBook, pk=pk)
    issue.return_date = timezone.localdate()
    issue.save()
    messages.success(request, 'Book marked as returned.')
    return redirect('library:issue_list')


@teacher_required
@require_POST
def fine_paid(request, pk):
    """Priority 2, issue #13: mark an overdue book's fine as settled."""
    issue = get_object_or_404(IssueBook, pk=pk)
    issue.fine_paid = True
    issue.save()
    messages.success(request, 'Fine marked as paid.')
    return redirect('library:issue_list')


# ---------------- Student self-service ----------------

@student_required
def my_books(request):
    student = getattr(request.user, 'student_profile', None)
    issues = student.book_issues.select_related('book').all() if student else []
    return render(request, 'library/my_books.html', {'issues': issues})
