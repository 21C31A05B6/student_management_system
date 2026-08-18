from django import forms
from .models import Exam, ExamSubject


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['name', 'academic_year', 'semester', 'date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2025-2026'}),
            'semester': forms.NumberInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class ExamSubjectForm(forms.ModelForm):
    class Meta:
        model = ExamSubject
        fields = ['exam', 'subject', 'max_marks']
        widgets = {
            'exam': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'max_marks': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
