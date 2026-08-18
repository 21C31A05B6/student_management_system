from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from accounts.decorators import admin_required
from accounts.view_helpers import confirm_and_delete
from academics.models import Section
from .models import TimetableEntry
from .forms import TimetableEntryForm


def view_timetable(request):
    """Shows the timetable relevant to the logged-in user's role."""
    section = None
    entries = TimetableEntry.objects.select_related('subject', 'teacher', 'section').none()

    if request.user.role == 'STUDENT':
        student = getattr(request.user, 'student_profile', None)
        section = getattr(student, 'section', None)
        if section:
            entries = TimetableEntry.objects.filter(section=section).select_related('subject', 'teacher')
    elif request.user.role == 'TEACHER':
        teacher = getattr(request.user, 'teacher_profile', None)
        entries = TimetableEntry.objects.filter(teacher=teacher).select_related('subject', 'section')
    else:  # ADMIN - can pick a section
        section_id = request.GET.get('section')
        if section_id:
            entries = TimetableEntry.objects.filter(section_id=section_id).select_related('subject', 'teacher')

    days = [(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday')]
    grid = {d[0]: [] for d in days}
    for e in entries:
        grid[e.day_of_week].append(e)

    return render(request, 'timetable/view.html', {
        'days': days, 'grid': grid, 'sections': Section.objects.all(),
        'selected_section': request.GET.get('section', ''),
    })


@admin_required
def timetable_manage(request):
    entries = TimetableEntry.objects.select_related('section', 'subject', 'teacher').all()
    return render(request, 'timetable/manage.html', {'entries': entries})


@admin_required
def timetable_form(request, pk=None):
    entry = get_object_or_404(TimetableEntry, pk=pk) if pk else None
    if request.method == 'POST':
        form = TimetableEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            messages.success(request, 'Timetable entry saved.')
            return redirect('timetable:manage')
    else:
        form = TimetableEntryForm(instance=entry)
    return render(request, 'generic_form.html', {
        'form': form, 'heading': 'Edit Timetable Entry' if entry else 'Add Timetable Entry',
        'cancel_url': '/timetable/manage/',
    })


@admin_required
def timetable_delete(request, pk):
    entry = TimetableEntry.objects.filter(pk=pk).first()
    return confirm_and_delete(request, entry, 'timetable:manage', '/timetable/manage/', success_message='Timetable entry deleted.')
