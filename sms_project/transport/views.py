from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from accounts.decorators import admin_required
from accounts.view_helpers import confirm_and_delete
from .models import Route, StudentTransport
from .forms import RouteForm, StudentTransportForm


@admin_required
def route_list(request):
    routes = Route.objects.all()
    return render(request, 'transport/route_list.html', {'routes': routes})


@admin_required
def route_form(request, pk=None):
    route = get_object_or_404(Route, pk=pk) if pk else None
    if request.method == 'POST':
        form = RouteForm(request.POST, instance=route)
        if form.is_valid():
            form.save()
            messages.success(request, 'Route saved.')
            return redirect('transport:route_list')
    else:
        form = RouteForm(instance=route)
    return render(request, 'generic_form.html', {
        'form': form, 'heading': 'Edit Route' if route else 'Add Route', 'cancel_url': '/transport/',
    })


@admin_required
def route_delete(request, pk):
    route = Route.objects.filter(pk=pk).first()
    return confirm_and_delete(request, route, 'transport:route_list', '/transport/', success_message='Route deleted.')


@admin_required
def assignment_form(request):
    if request.method == 'POST':
        form = StudentTransportForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student assigned to route.')
            return redirect('transport:route_list')
    else:
        form = StudentTransportForm()
    return render(request, 'generic_form.html', {
        'form': form, 'heading': 'Assign Student to Route', 'cancel_url': '/transport/',
    })
