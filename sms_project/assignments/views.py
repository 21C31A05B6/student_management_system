from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404

from accounts.decorators import teacher_required, student_required
from accounts.view_helpers import confirm_and_delete
from .models import Assignment, Submission
from .forms import AssignmentForm, SubmissionForm, GradeSubmissionForm


@teacher_required
def assignment_list(request):
    assignments = Assignment.objects.select_related('subject', 'section').all()
    if request.user.role == 'TEACHER':
        assignments = assignments.filter(teacher__user=request.user)
    return render(request, 'assignments/list.html', {'assignments': assignments})


@teacher_required
def assignment_form(request, pk=None):
    assignment = get_object_or_404(Assignment, pk=pk) if pk else None
    if request.user.role == 'TEACHER' and assignment and assignment.teacher_id != getattr(request.user.teacher_profile, 'id', None):
        raise PermissionDenied('You are not allowed to edit this assignment.')
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES, instance=assignment)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.teacher = getattr(request.user, 'teacher_profile', None)
            obj.save()
            messages.success(request, 'Assignment saved.')
            return redirect('assignments:list')
    else:
        form = AssignmentForm(instance=assignment)
    return render(request, 'generic_form.html', {
        'form': form, 'heading': 'Edit Assignment' if assignment else 'New Assignment', 'cancel_url': '/assignments/',
    })


@teacher_required
def assignment_delete(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    if request.user.role == 'TEACHER' and assignment.teacher_id != getattr(request.user.teacher_profile, 'id', None):
        raise PermissionDenied('You are not allowed to delete this assignment.')
    return confirm_and_delete(
        request, assignment, 'assignments:list', '/assignments/',
        message='All student submissions for this assignment will also be deleted.',
        success_message='Assignment deleted.',
    )


@teacher_required
def assignment_submissions(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    if request.user.role == 'TEACHER' and assignment.teacher_id != getattr(request.user.teacher_profile, 'id', None):
        raise PermissionDenied('You are not allowed to view submissions for this assignment.')
    submissions = assignment.submissions.select_related('student', 'student__user').all()
    if request.method == 'POST':
        sub = get_object_or_404(Submission, pk=request.POST.get('submission_id'))
        form = GradeSubmissionForm(request.POST, instance=sub)
        if form.is_valid():
            form.save()
            messages.success(request, 'Grade saved.')
            return redirect('assignments:submissions', pk=pk)
    return render(request, 'assignments/submissions.html', {'assignment': assignment, 'submissions': submissions})


@student_required
def my_assignments(request):
    student = getattr(request.user, 'student_profile', None)
    assignments = Assignment.objects.filter(section=student.section).select_related('subject') if student else []
    my_subs = {s.assignment_id: s for s in student.submissions.all()} if student else {}
    return render(request, 'assignments/my_assignments.html', {'assignments': assignments, 'my_subs': my_subs})


@student_required
def submit_assignment(request, pk):
    student = getattr(request.user, 'student_profile', None)
    assignment = get_object_or_404(Assignment, pk=pk)
    if student and assignment.section_id != student.section_id:
        raise PermissionDenied('This assignment is not for your section.')
    submission, _ = Submission.objects.get_or_create(assignment=assignment, student=student)
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            form.save()
            messages.success(request, 'Assignment submitted.')
            return redirect('assignments:my_assignments')
    else:
        form = SubmissionForm(instance=submission)
    return render(request, 'generic_form.html', {
        'form': form, 'heading': f'Submit: {assignment.title}', 'cancel_url': '/assignments/my/',
    })
