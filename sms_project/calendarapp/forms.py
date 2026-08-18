from django import forms
from .models import AcademicEvent


class AcademicEventForm(forms.ModelForm):
    class Meta:
        model = AcademicEvent
        fields = ['title', 'description', 'category', 'start_date', 'end_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
