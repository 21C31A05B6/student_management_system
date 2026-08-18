from django import forms
import datetime
from django.utils import timezone
from .models import Book, IssueBook


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'quantity']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }


class IssueBookForm(forms.ModelForm):
    class Meta:
        model = IssueBook
        fields = ['book', 'student', 'due_date']
        widgets = {
            'book': forms.Select(attrs={'class': 'form-select'}),
            'student': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only books with at least one available copy can be issued.
        self.fields['book'].queryset = Book.objects.all()
        if not self.initial.get('due_date') and not (self.instance and self.instance.pk):
            self.fields['due_date'].initial = timezone.localdate() + datetime.timedelta(days=14)

    def clean_book(self):
        book = self.cleaned_data['book']
        editing_same_book = self.instance.pk and self.instance.book_id == book.id
        if not editing_same_book and book.available_copies <= 0:
            raise forms.ValidationError(f'"{book.title}" has no available copies right now.')
        return book
