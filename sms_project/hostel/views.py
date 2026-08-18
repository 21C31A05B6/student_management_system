from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.decorators import admin_required
from accounts.view_helpers import confirm_and_delete
from .models import Room, HostelAllocation
from .forms import RoomForm, HostelAllocationForm


@admin_required
def room_list(request):
    rooms = Room.objects.all()
    return render(request, 'hostel/room_list.html', {'rooms': rooms})


@admin_required
def room_form(request, pk=None):
    room = get_object_or_404(Room, pk=pk) if pk else None
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, 'Room saved.')
            return redirect('hostel:room_list')
    else:
        form = RoomForm(instance=room)
    return render(request, 'generic_form.html', {
        'form': form, 'heading': 'Edit Room' if room else 'Add Room', 'cancel_url': '/hostel/',
    })


@admin_required
def room_delete(request, pk):
    room = Room.objects.filter(pk=pk).first()
    return confirm_and_delete(
        request, room, 'hostel:room_list', '/hostel/',
        message='Allocation history for this room will also be deleted.',
        success_message='Room deleted.',
    )


@admin_required
def allocate_form(request):
    if request.method == 'POST':
        form = HostelAllocationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student allocated to room.')
            return redirect('hostel:room_list')
    else:
        form = HostelAllocationForm()
    return render(request, 'generic_form.html', {
        'form': form, 'heading': 'Allocate Room', 'cancel_url': '/hostel/',
    })


@admin_required
@require_POST
def vacate(request, pk):
    alloc = get_object_or_404(HostelAllocation, pk=pk)
    alloc.vacated_date = timezone.localdate()
    alloc.save()
    messages.success(request, 'Room vacated.')
    return redirect('hostel:room_list')
