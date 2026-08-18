import datetime
from django.contrib import messages
from django.core.exceptions import ValidationError, PermissionDenied
from django.shortcuts import render, redirect

from accounts.decorators import teacher_required, student_required
from academics.models import Subject, Section
from students.models import Student
from .models import AttendanceRecord


from django.http import JsonResponse
import json


def _ensure_teacher_subject_access(request, subject_id):
    if request.user.role != 'TEACHER':
        return
    if not subject_id:
        return
    if not Subject.objects.filter(pk=subject_id, teachers__user=request.user).exists():
        raise PermissionDenied('You are not assigned to this subject.')


@teacher_required
def qr_scan(request):
    """QR-code attendance: teacher selects subject/date, then scans (or types)
    each student's QR token one at a time to mark them PRESENT instantly.
    Supports camera scanning via AJAX, USB scanners, manual entry, and session QR codes."""
    subjects = Subject.objects.all()
    if request.user.role == 'TEACHER':
        subjects = subjects.filter(teachers__user=request.user)

    subject_id = request.GET.get('subject') or request.POST.get('subject')
    _ensure_teacher_subject_access(request, subject_id)
    date_str = request.GET.get('date') or request.POST.get('date') or str(datetime.date.today())
    last_scanned = None
    selected_subject = None
    students_in_class = []
    records = []

    if subject_id:
        try:
            selected_subject = Subject.objects.get(pk=subject_id)
            # Find students in this subject's sections or department
            sub_sections = selected_subject.sections.all()
            if sub_sections.exists():
                students_in_class = Student.objects.filter(section__in=sub_sections).select_related('user', 'section', 'course').distinct()
            else:
                students_in_class = Student.objects.filter(department=selected_subject.department, semester=selected_subject.semester).select_related('user', 'section', 'course').distinct()
            
            if not students_in_class.exists():
                students_in_class = Student.objects.filter(status='ACTIVE').select_related('user', 'section', 'course')

            records = AttendanceRecord.objects.filter(
                subject_id=subject_id, date=date_str
            ).select_related('student__user').order_by('-id')
        except Subject.DoesNotExist:
            pass

    if request.method == 'POST':
        token = request.POST.get('token')
        if not token and request.body:
            try:
                body_data = json.loads(request.body)
                token = body_data.get('token')
                if not subject_id:
                    subject_id = body_data.get('subject')
                if not date_str:
                    date_str = body_data.get('date') or str(datetime.date.today())
            except Exception:
                pass

        if token:
            token = token.strip()
            is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.META.get('HTTP_ACCEPT', '') or request.content_type == 'application/json'
            try:
                # Try finding by qr_token (UUID) or by student_id as fallback
                try:
                    student = Student.objects.get(qr_token=token)
                except (Student.DoesNotExist, ValueError, ValidationError):
                    student = Student.objects.get(student_id=token)

                teacher = getattr(request.user, 'teacher_profile', None)
                record, created = AttendanceRecord.objects.update_or_create(
                    student=student, subject_id=subject_id, date=date_str,
                    defaults={'status': 'PRESENT', 'teacher': teacher},
                )
                last_scanned = student

                # Send WhatsApp & parent notification for PRESENT
                try:
                    from notifications.services import notify_attendance
                    subject_obj = Subject.objects.get(pk=subject_id)
                    notify_attendance(student, subject_obj, date_str, status='PRESENT')
                except Exception as e:
                    print(f"[Attendance WhatsApp Alert Error] {e}")

                if is_ajax:
                    total_present = AttendanceRecord.objects.filter(subject_id=subject_id, date=date_str, status='PRESENT').count()
                    return JsonResponse({
                        'success': True,
                        'message': f"Marked present: {student.user.get_full_name() or student.user.username} ({student.student_id}) — WhatsApp notification sent to parent.",
                        'student_name': student.user.get_full_name() or student.user.username,
                        'student_id': student.student_id,
                        'time': datetime.datetime.now().strftime('%H:%M:%S'),
                        'total_present': total_present,
                    })

                messages.success(request, f"Marked present: {student.user.get_full_name()} ({student.student_id}) — Parent notified on WhatsApp.")
            except (Student.DoesNotExist, ValueError, ValidationError):
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'message': "No student matches that QR code / Token."
                    }, status=404)
                messages.error(request, "No student matches that QR code.")

    return render(request, 'attendance/qr_scan.html', {
        'subjects': subjects,
        'subject_id': subject_id,
        'selected_subject': selected_subject,
        'date_str': date_str,
        'last_scanned': last_scanned,
        'students_in_class': students_in_class,
        'records': records,
    })


@teacher_required
def mark_attendance(request):
    subjects = Subject.objects.all()
    if request.user.role == 'TEACHER':
        subjects = subjects.filter(teachers__user=request.user)

    section_id = request.GET.get('section') or request.POST.get('section')
    subject_id = request.GET.get('subject') or request.POST.get('subject')
    _ensure_teacher_subject_access(request, subject_id)
    date_str = request.GET.get('date') or request.POST.get('date') or str(datetime.date.today())

    sections = Section.objects.all()
    students = []
    existing = {}

    if section_id and subject_id:
        students = Student.objects.filter(section_id=section_id).select_related('user')
        records = AttendanceRecord.objects.filter(subject_id=subject_id, date=date_str, student__section_id=section_id)
        existing = {r.student_id: r.status for r in records}

    if request.method == 'POST' and section_id and subject_id:
        teacher = getattr(request.user, 'teacher_profile', None)
        try:
            from notifications.services import notify_attendance
            subject_obj = Subject.objects.get(pk=subject_id)
        except Exception:
            subject_obj = None

        for student in students:
            status = request.POST.get(f'status_{student.id}', 'ABSENT')
            AttendanceRecord.objects.update_or_create(
                student=student, subject_id=subject_id, date=date_str,
                defaults={'status': status, 'teacher': teacher},
            )
            # Send WhatsApp notification to parents for PRESENT and ABSENT
            if subject_obj:
                try:
                    notify_attendance(student, subject_obj, date_str, status=status)
                except Exception as e:
                    print(f"[Attendance WhatsApp Alert Error] {e}")

        messages.success(request, 'Attendance saved successfully & WhatsApp notifications sent to parents.')
        return redirect(f"{request.path}?section={section_id}&subject={subject_id}&date={date_str}")

    return render(request, 'attendance/mark.html', {
        'subjects': subjects, 'sections': sections, 'students': students,
        'existing': existing, 'section_id': section_id, 'subject_id': subject_id, 'date_str': date_str,
    })


@student_required
def my_attendance(request):
    student = getattr(request.user, 'student_profile', None)
    records = []
    summary = []
    if student:
        records = student.attendance_records.select_related('subject').order_by('-date')
        subjects = Subject.objects.filter(attendance_records__student=student).distinct()
        for subject in subjects:
            subject_records = records.filter(subject=subject)
            total = subject_records.count()
            present = subject_records.filter(status='PRESENT').count()
            pct = round((present / total) * 100, 1) if total else 0
            summary.append({'subject': subject, 'total': total, 'present': present, 'pct': pct})
    return render(request, 'attendance/my_attendance.html', {'records': records, 'summary': summary, 'student': student})
