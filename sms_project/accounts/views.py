from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import render, redirect

from .forms import StyledAuthenticationForm, StyledPasswordChangeForm, ProfileForm


class SMSLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = StyledAuthenticationForm
    redirect_authenticated_user = True


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('accounts:login')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = StyledPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully.")
            return redirect('accounts:profile')
    else:
        form = StyledPasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})
