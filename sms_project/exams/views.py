from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import render, redirect, get_object_or_404

from accounts.decorators import teacher_required, student_required, admin_required
from accounts.view_helpers import confirm_and_delete
from academics.models import Subject, Section
from students.models import Student
from .models import Exam, ExamSubject, Mark, calculate_gpa, calculate_cgpa
from .forms import ExamForm, ExamSubjectForm


# ---------------- Exam management (Admin) ----------------

@admin_required
def exam_list(request):
    exams = Exam.objects.prefetch_related('exam_subjects__subject').all()
    return render(request, 'exams/exam_list.html', {'exams': exams})


@admin_required
def exam_form(request, pk=None):
    exam = get_object_or_404(Exam, pk=pk) if pk else None
    if request.method == 'POST':
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exam saved successfully.')
            return redirect('exams:exam_list')
    else:
        form = ExamForm(instance=exam)
    return render(request, 'generic_form.html', {
        'form': form, 'heading': 'Edit Exam' if exam else 'Add Exam', 'cancel_url': '/exams/manage/',
    })


@admin_required
def exam_delete(request, pk):
    exam = Exam.objects.filter(pk=pk).first()
    return confirm_and_delete(
        request, exam, 'exams:exam_list', '/exams/manage/',
        message='All exam-subjects and marks recorded under this exam will also be deleted.',
        success_message='Exam deleted.',
    )


@admin_required
def exam_subject_form(request, pk=None):
    """Add/edit the per-subject max marks for a given exam."""
    exam_subject = get_object_or_404(ExamSubject, pk=pk) if pk else None
    if request.method == 'POST':
        form = ExamSubjectForm(request.POST, instance=exam_subject)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exam subject saved.')
            return redirect('exams:exam_list')
    else:
        form = ExamSubjectForm(instance=exam_subject)
    return render(request, 'generic_form.html', {
        'form': form, 'heading': 'Edit Exam Subject' if exam_subject else 'Add Exam Subject',
        'cancel_url': '/exams/manage/',
    })


@admin_required
def exam_subject_delete(request, pk):
    exam_subject = ExamSubject.objects.filter(pk=pk).first()
    return confirm_and_delete(
        request, exam_subject, 'exams:exam_list', '/exams/manage/',
        message='Marks recorded for this exam-subject will also be deleted.',
        success_message='Exam subject deleted.',
    )


# ---------------- Marks entry (Admin/Teacher) ----------------

@teacher_required
def marks_entry(request):
    subjects = Subject.objects.all()
    if request.user.role == 'TEACHER':
        subjects = subjects.filter(teachers__user=request.user)
    exams = Exam.objects.all()
    sections = Section.objects.all()

    section_id = request.GET.get('section') or request.POST.get('section')
    subject_id = request.GET.get('subject') or request.POST.get('subject')
    exam_id = request.GET.get('exam') or request.POST.get('exam')

    # Priority 1, issue: teachers may only enter marks for subjects they teach.
    if request.user.role == 'TEACHER' and subject_id and not Subject.objects.filter(pk=subject_id, teachers__user=request.user).exists():
        raise PermissionDenied('You are not assigned to this subject.')

    students = []
    existing = {}
    exam_subject = None

    if section_id and subject_id and exam_id:
        students = Student.objects.filter(section_id=section_id).select_related('user')
        exam_subject = ExamSubject.objects.filter(exam_id=exam_id, subject_id=subject_id).first()
        if exam_subject:
            records = Mark.objects.filter(exam_subject=exam_subject, student__section_id=section_id)
            existing = {r.student_id: r.marks_obtained for r in records}

    if request.method == 'POST' and section_id and subject_id and exam_id:
        if not exam_subject:
            messages.error(request, 'This subject has no max-marks configured for this exam yet. Ask an admin to add it under Exam Management.')
            return redirect(f"{request.path}?section={section_id}&subject={subject_id}&exam={exam_id}")
        errors = []
        for student in students:
            value = request.POST.get(f'marks_{student.id}', '').strip()
            if value != '':
                try:
                    mark = Mark(student=student, exam_subject=exam_subject, marks_obtained=value)
                    existing_mark = Mark.objects.filter(student=student, exam_subject=exam_subject).first()
                    if existing_mark:
                        mark.pk = existing_mark.pk
                    mark.save()
                except ValidationError as e:
                    errors.append(f"{student.student_id}: {'; '.join(e.messages)}")
        if errors:
            messages.error(request, "Some marks were rejected — " + " | ".join(errors))
        else:
            messages.success(request, 'Marks saved successfully.')
        return redirect(f"{request.path}?section={section_id}&subject={subject_id}&exam={exam_id}")

    return render(request, 'exams/marks_entry.html', {
        'subjects': subjects, 'sections': sections, 'exams': exams, 'students': students,
        'existing': existing, 'section_id': section_id, 'subject_id': subject_id, 'exam_id': exam_id,
        'exam_subject': exam_subject,
    })


@student_required
def my_marks(request):
    student = getattr(request.user, 'student_profile', None)
    marks = student.marks.select_related('exam_subject__subject', 'exam_subject__exam').all() if student else []
    cgpa = calculate_cgpa(student) if student else None

    # GPA per exam (Priority 2, issue #8)
    gpa_by_exam = {}
    if student:
        exam_ids = marks.values_list('exam_subject__exam_id', flat=True).distinct()
        for exam_id in exam_ids:
            exam = Exam.objects.get(pk=exam_id)
            exam_marks = marks.filter(exam_subject__exam_id=exam_id)
            gpa_by_exam[exam] = calculate_gpa(exam_marks)

    return render(request, 'exams/my_marks.html', {'marks': marks, 'cgpa': cgpa, 'gpa_by_exam': gpa_by_exam})
