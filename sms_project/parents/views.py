from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q

from accounts.decorators import admin_required, parent_required
from students.models import Student
from .models import ParentProfile
from .forms import ParentForm


@admin_required
def parent_list(request):
    profiles = ParentProfile.objects.select_related('user').prefetch_related('children').order_by('user__first_name', 'user__last_name').all()
    legacy_parents = Student.objects.filter(
        Q(parent_name__gt='') | Q(parent_phone__gt=''),
        parent_profiles__isnull=True
    ).select_related('user').order_by('parent_name', 'user__first_name')
    return render(request, 'parents/list.html', {
        'parents': profiles,
        'legacy_parents': legacy_parents,
    })


@admin_required
def parent_form(request, pk=None):
    parent = get_object_or_404(ParentProfile, pk=pk) if pk else None
    if request.method == 'POST':
        form = ParentForm(request.POST, instance=parent)
        if form.is_valid():
            form.save()
            messages.success(request, 'Parent details updated.' if pk else 'Parent account created successfully with WhatsApp number.')
            return redirect('parents:list')
    else:
        form = ParentForm(instance=parent)
    return render(request, 'generic_form.html', {
        'form': form,
        'heading': 'Edit Parent' if pk else 'Add Parent',
        'cancel_url': '/parents/',
    })


@parent_required
def parent_portal(request):
    profile = getattr(request.user, 'parent_profile', None)
    children = profile.children.select_related('user', 'department', 'course').all() if profile else []
    return render(request, 'parents/portal.html', {'children': children})
