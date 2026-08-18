from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from accounts.decorators import admin_required
from accounts.view_helpers import confirm_and_delete
from .models import Department, Course, Section, Subject
from .forms import DepartmentForm, CourseForm, SectionForm, SubjectForm


# ---------------- Departments ----------------
@admin_required
def department_list(request):
    departments = Department.objects.select_related('head_of_department').all()
    return render(request, 'academics/department_list.html', {'departments': departments})


@admin_required
def department_form(request, pk=None):
    department = get_object_or_404(Department, pk=pk) if pk else None
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department saved successfully.')
            return redirect('academics:department_list')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'generic_form.html', {
        'form': form,
        'heading': 'Edit Department' if department else 'Add Department',
        'cancel_url': '/academics/departments/',
    })


@admin_required
def department_delete(request, pk):
    department = Department.objects.filter(pk=pk).first()
    return confirm_and_delete(
        request, department, 'academics:department_list', '/academics/departments/',
        message='Deleting a department also removes its courses, sections, and subjects.',
        success_message='Department deleted.',
    )


# ---------------- Courses ----------------
@admin_required
def course_list(request):
    courses = Course.objects.select_related('department').all()
    return render(request, 'academics/course_list.html', {'courses': courses})


@admin_required
def course_form(request, pk=None):
    course = get_object_or_404(Course, pk=pk) if pk else None
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course saved successfully.')
            return redirect('academics:course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'generic_form.html', {
        'form': form,
        'heading': 'Edit Course' if course else 'Add Course',
        'cancel_url': '/academics/courses/',
    })


@admin_required
def course_delete(request, pk):
    course = Course.objects.filter(pk=pk).first()
    return confirm_and_delete(
        request, course, 'academics:course_list', '/academics/courses/',
        message='Deleting a course also removes its sections.',
        success_message='Course deleted.',
    )


# ---------------- Sections ----------------
@admin_required
def section_list(request):
    sections = Section.objects.select_related('course').all()
    return render(request, 'academics/section_list.html', {'sections': sections})


@admin_required
def section_form(request, pk=None):
    section = get_object_or_404(Section, pk=pk) if pk else None
    if request.method == 'POST':
        form = SectionForm(request.POST, instance=section)
        if form.is_valid():
            form.save()
            messages.success(request, 'Section saved successfully.')
            return redirect('academics:section_list')
    else:
        form = SectionForm(instance=section)
    return render(request, 'generic_form.html', {
        'form': form,
        'heading': 'Edit Section' if section else 'Add Section',
        'cancel_url': '/academics/sections/',
    })


@admin_required
def section_delete(request, pk):
    section = Section.objects.filter(pk=pk).first()
    return confirm_and_delete(
        request, section, 'academics:section_list', '/academics/sections/',
        success_message='Section deleted.',
    )


# ---------------- Subjects ----------------
@admin_required
def subject_list(request):
    subjects = Subject.objects.select_related('department').all()
    return render(request, 'academics/subject_list.html', {'subjects': subjects})


@admin_required
def subject_form(request, pk=None):
    subject = get_object_or_404(Subject, pk=pk) if pk else None
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject saved successfully.')
            return redirect('academics:subject_list')
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'generic_form.html', {
        'form': form,
        'heading': 'Edit Subject' if subject else 'Add Subject',
        'cancel_url': '/academics/subjects/',
    })


@admin_required
def subject_delete(request, pk):
    subject = Subject.objects.filter(pk=pk).first()
    return confirm_and_delete(
        request, subject, 'academics:subject_list', '/academics/subjects/',
        success_message='Subject deleted.',
    )
