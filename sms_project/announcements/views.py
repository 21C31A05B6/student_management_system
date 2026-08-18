from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from accounts.decorators import admin_required
from accounts.view_helpers import confirm_and_delete
from .models import Announcement
from .forms import AnnouncementForm


@login_required
def announcement_list(request):
    qs = Announcement.objects.all()
    if request.user.role == 'TEACHER':
        qs = qs.filter(audience__in=[Announcement.Audience.ALL, Announcement.Audience.TEACHERS])
    elif request.user.role == 'STUDENT':
        qs = qs.filter(audience__in=[Announcement.Audience.ALL, Announcement.Audience.STUDENTS])
    return render(request, 'announcements/list.html', {'announcements': qs})


@admin_required
def announcement_form(request, pk=None):
    ann = get_object_or_404(Announcement, pk=pk) if pk else None
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=ann)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.posted_by = request.user
            obj.save()
            messages.success(request, 'Announcement published.')
            return redirect('announcements:list')
    else:
        form = AnnouncementForm(instance=ann)
    return render(request, 'generic_form.html', {
        'form': form, 'heading': 'Edit Announcement' if ann else 'New Announcement', 'cancel_url': '/announcements/',
    })


@admin_required
def announcement_delete(request, pk):
    announcement = Announcement.objects.filter(pk=pk).first()
    return confirm_and_delete(request, announcement, 'announcements:list', '/announcements/', success_message='Announcement deleted.')
