from django import forms
from .models import Route, StudentTransport


class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ['name', 'vehicle_number', 'driver_name', 'driver_phone', 'capacity']
        widgets = {f: forms.TextInput(attrs={'class': 'form-control'}) for f in
                   ['name', 'vehicle_number', 'driver_name', 'driver_phone']}
        widgets['capacity'] = forms.NumberInput(attrs={'class': 'form-control'})


class StudentTransportForm(forms.ModelForm):
    class Meta:
        model = StudentTransport
        fields = ['student', 'route', 'pickup_point']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'route': forms.Select(attrs={'class': 'form-select'}),
            'pickup_point': forms.TextInput(attrs={'class': 'form-control'}),
        }
