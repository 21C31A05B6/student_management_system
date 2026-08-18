from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from students.models import Student
from teachers.models import Teacher
from academics.models import Department, Subject, Course
from attendance.models import AttendanceRecord
from exams.models import Mark
from fees.models import FeeRecord
import json


@login_required
def home(request):
    user = request.user

    if user.role == 'ADMIN':
        total_students = Student.objects.count()
        total_teachers = Teacher.objects.count()
        total_courses = Course.objects.count()
        total_departments = Department.objects.count()
        total_subjects = Subject.objects.count()

        total_att = AttendanceRecord.objects.count()
        present_att = AttendanceRecord.objects.filter(status='PRESENT').count()
        attendance_pct = round((present_att / total_att) * 100, 1) if total_att else 0

        recent_students = Student.objects.select_related('user').order_by('-id')[:5]
        recent_payments = FeeRecord.objects.select_related('student', 'student__user').order_by('-id')[:5]

        # Performance charts data (Module: Performance Charts)
        dept_labels = []
        dept_counts = []
        for dept in Department.objects.all():
            dept_labels.append(dept.code)
            dept_counts.append(dept.students.count())

        last_7_days = [timezone.localdate() - timezone.timedelta(days=i) for i in range(6, -1, -1)]
        attendance_trend_labels = [d.strftime('%d %b') for d in last_7_days]
        attendance_trend_data = []
        for d in last_7_days:
            day_total = AttendanceRecord.objects.filter(date=d).count()
            day_present = AttendanceRecord.objects.filter(date=d, status='PRESENT').count()
            attendance_trend_data.append(round((day_present / day_total) * 100, 1) if day_total else 0)

        return render(request, 'dashboard/admin_dashboard.html', {
            'total_students': total_students,
            'total_teachers': total_teachers,
            'total_courses': total_courses,
            'total_departments': total_departments,
            'total_subjects': total_subjects,
            'attendance_pct': attendance_pct,
            'recent_students': recent_students,
            'recent_payments': recent_payments,
            'dept_labels': json.dumps(dept_labels),
            'dept_counts': json.dumps(dept_counts),
            'attendance_trend_labels': json.dumps(attendance_trend_labels),
            'attendance_trend_data': json.dumps(attendance_trend_data),
        })

    elif user.role == 'TEACHER':
        teacher = getattr(user, 'teacher_profile', None)
        subjects = teacher.subjects_taught.all() if teacher else []
        classes_today = 0
        if teacher:
            today_dow = timezone.localdate().isoweekday()
            classes_today = teacher.timetable_entries.filter(day_of_week=today_dow).count()
        marked_today = AttendanceRecord.objects.filter(
            teacher=teacher, date=timezone.localdate()
        ).count() if teacher else 0

        return render(request, 'dashboard/teacher_dashboard.html', {
            'teacher': teacher,
            'subjects': subjects,
            'classes_today': classes_today,
            'marked_today': marked_today,
        })

    elif user.role == 'PARENT':
        from django.shortcuts import redirect
        return redirect('parents:portal')

    else:  # STUDENT
        student = getattr(user, 'student_profile', None)
        attendance_pct = None
        avg_pct = None
        fees_due = None
        marks_chart_labels = json.dumps([])
        marks_chart_data = json.dumps([])
        if student:
            total = student.attendance_records.count()
            present = student.attendance_records.filter(status='PRESENT').count()
            attendance_pct = round((present / total) * 100, 1) if total else None

            marks = student.marks.select_related('exam_subject__subject').all()
            if marks:
                avg_pct = round(sum(m.percentage for m in marks) / marks.count(), 1)
                marks_chart_labels = json.dumps([m.subject.code for m in marks])
                marks_chart_data = json.dumps([m.percentage for m in marks])

            fee_record = student.fee_records.order_by('-academic_year').first()
            fees_due = fee_record.due_amount if fee_record else None

        return render(request, 'dashboard/student_dashboard.html', {
            'student': student,
            'attendance_pct': attendance_pct,
            'avg_pct': avg_pct,
            'fees_due': fees_due,
            'marks_chart_labels': marks_chart_labels,
            'marks_chart_data': marks_chart_data,
        })
