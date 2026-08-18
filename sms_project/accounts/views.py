from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.sessions.backends.db import SessionStore
from django.shortcuts import render, redirect

from .forms import StyledAuthenticationForm, StyledPasswordChangeForm, ProfileForm


class SMSLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = StyledAuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()

        # ── Single-device enforcement ──────────────────────────────────────
        # If this user already has an active session on another device,
        # delete it from the session store so they are logged out immediately.
        if user.active_session_key:
            try:
                old_session = SessionStore(session_key=user.active_session_key)
                old_session.delete()
            except Exception:
                pass  # Session may have already expired — that's fine

        # Proceed with normal login (creates a new session)
        response = super().form_valid(form)

        # Save the new session key on the user record
        user.active_session_key = self.request.session.session_key
        user.save(update_fields=['active_session_key'])

        return response


@login_required
def logout_view(request):
    # Clear the stored session key so the user record is clean
    user = request.user
    user.active_session_key = None
    user.save(update_fields=['active_session_key'])
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
