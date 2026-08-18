from django import forms
from django.contrib.auth.hashers import make_password
from accounts.models import User
from .models import Student


class StudentForm(forms.ModelForm):
    """Creates/edits a Student. On create, also creates the linked User account."""
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                                help_text="Leave blank to keep existing password (only used when adding a new student).")

    class Meta:
        model = Student
        fields = [
            'student_id', 'date_of_birth', 'gender', 'address', 'photo',
            'department', 'course', 'section', 'year', 'semester',
            'admission_date', 'parent_name', 'parent_phone', 'status',
        ]
        widgets = {
            'student_id': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'section': forms.Select(attrs={'class': 'form-select'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'semester': forms.NumberInput(attrs={'class': 'form-control'}),
            'admission_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'parent_name': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['username'].initial = self.instance.user.username
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['username'].widget.attrs['readonly'] = True

    def save(self, commit=True):
        student = super().save(commit=False)
        if student.pk:
            user = student.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            if self.cleaned_data.get('password'):
                user.password = make_password(self.cleaned_data['password'])
            user.save()
        else:
            user = User.objects.create(
                username=self.cleaned_data['username'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                email=self.cleaned_data['email'],
                role=User.Role.STUDENT,
                password=make_password(self.cleaned_data.get('password') or 'changeme123'),
            )
            student.user = user
        if commit:
            student.save()
        return student
