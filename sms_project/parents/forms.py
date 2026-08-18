from django import forms
from django.contrib.auth.hashers import make_password
from accounts.models import User
from students.models import Student
from .models import ParentProfile


class ParentForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. john_parent'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}))
    phone = forms.CharField(
        required=False,
        label="Parent WhatsApp / Mobile Number",
        help_text="Attendance notifications (Present/Absent) will be sent to this WhatsApp number.",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 9908656185 or +919908656185'})
    )
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Leave blank to default to 'changeme123' (or keep current password when editing)."
    )

    class Meta:
        model = ParentProfile
        fields = ['relation', 'children']
        widgets = {
            'relation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Father, Mother, Guardian'}),
            'children': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and hasattr(self.instance, 'user'):
            self.fields['username'].initial = self.instance.user.username
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['phone'].initial = self.instance.user.phone

    def save(self, commit=True):
        parent = super().save(commit=False)
        phone_num = self.cleaned_data.get('phone', '').strip()
        if not parent.pk:
            user = User.objects.create(
                username=self.cleaned_data['username'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                email=self.cleaned_data['email'],
                phone=phone_num,
                role=User.Role.PARENT,
                password=make_password(self.cleaned_data.get('password') or 'changeme123'),
            )
            parent.user = user
        else:
            user = parent.user
            user.username = self.cleaned_data['username']
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.phone = phone_num
            if self.cleaned_data.get('password'):
                user.password = make_password(self.cleaned_data['password'])
            user.save()

        if commit:
            parent.save()
            self.save_m2m()
            # Sync parent's phone and name to linked children if not already set
            if phone_num:
                for child in parent.children.all():
                    if not child.parent_phone:
                        child.parent_phone = phone_num
                        if not child.parent_name:
                            child.parent_name = parent.user.get_full_name() or parent.user.username
                        child.save(update_fields=['parent_phone', 'parent_name'])

        return parent
