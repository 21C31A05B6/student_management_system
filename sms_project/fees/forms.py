from django import forms
from .models import FeeRecord, Payment


class FeeRecordForm(forms.ModelForm):
    class Meta:
        model = FeeRecord
        fields = ['student', 'academic_year', 'total_amount', 'paid_amount']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2025-2026'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'paid_amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'method', 'receipt_number']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'method': forms.Select(attrs={'class': 'form-select'}),
            'receipt_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
