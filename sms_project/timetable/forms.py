from django import forms
from .models import TimetableEntry


class TimetableEntryForm(forms.ModelForm):
    class Meta:
        model = TimetableEntry
        fields = ['section', 'subject', 'teacher', 'room_number', 'day_of_week', 'start_time', 'end_time']
        widgets = {
            'section': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'teacher': forms.Select(attrs={'class': 'form-select'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Room 204'}),
            'day_of_week': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }
