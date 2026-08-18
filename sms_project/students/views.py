from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404

from accounts.decorators import admin_required, teacher_required
from accounts.view_helpers import confirm_and_delete
from .models import Student
from .forms import StudentForm


@teacher_required
def student_list(request):
    query = request.GET.get('q', '')
    dept = request.GET.get('department', '')
    students = Student.objects.select_related('user', 'department', 'course', 'section').all()
    if query:
        students = students.filter(user__first_name__icontains=query) | students.filter(student_id__icontains=query)
    if dept:
        students = students.filter(department_id=dept)
    from academics.models import Department
    return render(request, 'students/student_list.html', {
        'students': students, 'query': query, 'departments': Department.objects.all(), 'selected_dept': dept,
    })


@admin_required
def student_form(request, pk=None):
    student = get_object_or_404(Student, pk=pk) if pk else None
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student saved successfully.')
            return redirect('students:list')
    else:
        form = StudentForm(instance=student)
    return render(request, 'generic_form.html', {
        'form': form,
        'heading': 'Edit Student' if student else 'Add Student',
        'cancel_url': '/students/',
    })


@admin_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return confirm_and_delete(
        request, student, 'students:list', '/students/',
        message='This permanently deletes the student\'s login account along with their attendance, marks, and fee history.',
        success_message='Student deleted.',
        delete_fn=student.user.delete,
    )


@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    user = request.user
    is_owner = user.role == 'STUDENT' and hasattr(user, 'student_profile') and user.student_profile.id == student.id
    is_parent_of = user.role == 'PARENT' and hasattr(user, 'parent_profile') and user.parent_profile.children.filter(pk=student.id).exists()
    if not (user.role in ('ADMIN', 'TEACHER') or is_owner or is_parent_of):
        raise PermissionDenied("You do not have permission to view this student's profile.")

    total = student.attendance_records.count()
    present = student.attendance_records.filter(status='PRESENT').count()
    attendance_pct = round((present / total) * 100, 1) if total else None
    marks = student.marks.select_related('exam_subject__subject', 'exam_subject__exam').all()
    fees = student.fee_records.all()
    from exams.models import Exam, calculate_cgpa
    exams_for_reports = Exam.objects.filter(exam_subjects__marks__student=student).distinct()
    cgpa = calculate_cgpa(student)
    return render(request, 'students/student_detail.html', {
        'student': student,
        'attendance_pct': attendance_pct,
        'total_classes': total,
        'present_classes': present,
        'marks': marks,
        'fees': fees,
        'exams_for_reports': exams_for_reports,
        'cgpa': cgpa,
    })
