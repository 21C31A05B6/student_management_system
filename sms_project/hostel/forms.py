from django import forms
from .models import Room, HostelAllocation


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['block', 'room_number', 'room_type', 'capacity']
        widgets = {
            'block': forms.TextInput(attrs={'class': 'form-control'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control'}),
            'room_type': forms.Select(attrs={'class': 'form-select'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class HostelAllocationForm(forms.ModelForm):
    class Meta:
        model = HostelAllocation
        fields = ['student', 'room']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'room': forms.Select(attrs={'class': 'form-select'}),
        }
