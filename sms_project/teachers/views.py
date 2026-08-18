from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from accounts.decorators import admin_required
from accounts.view_helpers import confirm_and_delete
from .models import Teacher
from .forms import TeacherForm


@admin_required
def teacher_list(request):
    query = request.GET.get('q', '')
    teachers = Teacher.objects.select_related('user', 'department').all()
    if query:
        teachers = teachers.filter(user__first_name__icontains=query) | teachers.filter(teacher_id__icontains=query)
    return render(request, 'teachers/teacher_list.html', {'teachers': teachers, 'query': query})


@admin_required
def teacher_form(request, pk=None):
    teacher = get_object_or_404(Teacher, pk=pk) if pk else None
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, 'Teacher saved successfully.')
            return redirect('teachers:list')
    else:
        form = TeacherForm(instance=teacher)
    return render(request, 'generic_form.html', {
        'form': form,
        'heading': 'Edit Teacher' if teacher else 'Add Teacher',
        'cancel_url': '/teachers/',
    })


@admin_required
def teacher_delete(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    return confirm_and_delete(
        request, teacher, 'teachers:list', '/teachers/',
        message='This permanently deletes the teacher\'s login account.',
        success_message='Teacher deleted.',
        delete_fn=teacher.user.delete,
    )


@admin_required
def teacher_detail(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    return render(request, 'teachers/teacher_detail.html', {'teacher': teacher})
