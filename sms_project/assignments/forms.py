from django import forms
from .models import Assignment, Submission


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['subject', 'section', 'title', 'description', 'due_date', 'attachment']
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'section': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['file']
        widgets = {'file': forms.ClearableFileInput(attrs={'class': 'form-control'})}


class GradeSubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['grade', 'feedback']
        widgets = {
            'grade': forms.TextInput(attrs={'class': 'form-control'}),
            'feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
