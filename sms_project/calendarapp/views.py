from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from accounts.decorators import admin_required
from accounts.view_helpers import confirm_and_delete
from .models import AcademicEvent
from .forms import AcademicEventForm


@login_required
def event_list(request):
    upcoming = AcademicEvent.objects.filter(start_date__gte=timezone.localdate())
    past = AcademicEvent.objects.filter(start_date__lt=timezone.localdate())
    return render(request, 'calendarapp/list.html', {'upcoming': upcoming, 'past': past})


@admin_required
def event_form(request, pk=None):
    event = get_object_or_404(AcademicEvent, pk=pk) if pk else None
    if request.method == 'POST':
        form = AcademicEventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event saved.')
            return redirect('calendarapp:list')
    else:
        form = AcademicEventForm(instance=event)
    return render(request, 'generic_form.html', {
        'form': form, 'heading': 'Edit Event' if event else 'Add Event', 'cancel_url': '/calendar/',
    })


@admin_required
def event_delete(request, pk):
    event = AcademicEvent.objects.filter(pk=pk).first()
    return confirm_and_delete(request, event, 'calendarapp:list', '/calendar/', success_message='Event deleted.')
