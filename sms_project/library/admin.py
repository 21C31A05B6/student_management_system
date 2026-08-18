from django.contrib import admin
from .models import Book, IssueBook


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'quantity', 'available_copies')
    search_fields = ('title', 'author', 'isbn')


@admin.register(IssueBook)
class IssueBookAdmin(admin.ModelAdmin):
    list_display = ('book', 'student', 'issue_date', 'due_date', 'return_date', 'issued_by')
    list_filter = ('issue_date', 'return_date')
