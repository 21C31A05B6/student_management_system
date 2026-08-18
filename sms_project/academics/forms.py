from django import forms
from .models import Department, Course, Section, Subject


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['code', 'name', 'head_of_department', 'description']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'head_of_department': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['department', 'name', 'duration_years']
        widgets = {
            'department': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'duration_years': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['course', 'year', 'semester', 'name']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'semester': forms.NumberInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['code', 'name', 'department', 'semester', 'credits', 'teachers', 'sections']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'semester': forms.NumberInput(attrs={'class': 'form-control'}),
            'credits': forms.NumberInput(attrs={'class': 'form-control'}),
            'teachers': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'sections': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }
