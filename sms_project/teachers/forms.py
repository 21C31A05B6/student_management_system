from django import forms
from django.contrib.auth.hashers import make_password
from accounts.models import User
from .models import Teacher


class TeacherForm(forms.ModelForm):
    """Creates/edits a Teacher. On create, also creates the linked User account."""
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                                help_text="Leave blank to keep existing password (only used when adding a new teacher).")

    class Meta:
        model = Teacher
        fields = ['teacher_id', 'department', 'qualification', 'joining_date', 'photo', 'status']
        widgets = {
            'teacher_id': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'joining_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['username'].initial = self.instance.user.username
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['phone'].initial = self.instance.user.phone
            self.fields['username'].widget.attrs['readonly'] = True

    def save(self, commit=True):
        teacher = super().save(commit=False)
        if teacher.pk:
            user = teacher.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.phone = self.cleaned_data['phone']
            if self.cleaned_data.get('password'):
                user.password = make_password(self.cleaned_data['password'])
            user.save()
        else:
            user = User.objects.create(
                username=self.cleaned_data['username'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                email=self.cleaned_data['email'],
                phone=self.cleaned_data['phone'],
                role=User.Role.TEACHER,
                password=make_password(self.cleaned_data.get('password') or 'changeme123'),
            )
            teacher.user = user
        if commit:
            teacher.save()
        return teacher
