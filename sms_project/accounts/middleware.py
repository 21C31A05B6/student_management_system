"""
accounts/middleware.py

SingleDeviceMiddleware
──────────────────────
On every authenticated request, checks that the current session key still
matches the active_session_key stored on the user record.

If they don't match it means the user logged in on another device and their
old session was deleted. The middleware immediately logs them out and sends
them to the login page with a clear message.
"""

from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse


class SingleDeviceMiddleware:
    """Enforce one active session per user across all roles."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            current_key = request.session.session_key
            stored_key = request.user.active_session_key

            # If stored key differs, this session was invalidated by a new login
            if stored_key and current_key != stored_key:
                logout(request)
                messages.warning(
                    request,
                    "Your account was logged in on another device. "
                    "You have been logged out here."
                )
                return redirect(reverse('accounts:login'))

        return self.get_response(request)
