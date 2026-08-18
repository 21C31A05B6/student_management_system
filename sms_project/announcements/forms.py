from django import forms
from .models import Announcement


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'body', 'audience', 'pinned']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'audience': forms.Select(attrs={'class': 'form-select'}),
            'pinned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
