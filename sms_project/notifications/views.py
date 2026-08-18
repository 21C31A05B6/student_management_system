from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from accounts.decorators import admin_required
from students.models import Student
from fees.models import FeeRecord
from .models import Notification
from .services import send_email_notification, send_sms_notification, send_whatsapp_notification, notify_fee_due


@admin_required
def notification_list(request):
    notifications = Notification.objects.select_related('recipient_user').all()[:200]
    return render(request, 'notifications/list.html', {'notifications': notifications})


@admin_required
def send_notification(request):
    students = Student.objects.select_related('user').all()
    if request.method == 'POST':
        student_id = request.POST.get('student')
        channel = request.POST.get('channel')
        subject = request.POST.get('subject', 'Notice')
        message = request.POST.get('message', '')
        student = get_object_or_404(Student, pk=student_id)
        if channel == 'EMAIL':
            send_email_notification(student.user, subject, message)
        elif channel == 'WHATSAPP':
            phone = student.parent_phone or student.user.phone
            send_whatsapp_notification(phone, message, user=student.user)
        else:
            send_sms_notification(student.user, message)
        messages.success(request, f'{channel} notification sent to {student.user.get_full_name()}.')
        return redirect('notifications:list')
    return render(request, 'notifications/send.html', {'students': students})


@admin_required
def send_fee_reminder(request, pk):
    fee_record = get_object_or_404(FeeRecord, pk=pk)
    notify_fee_due(fee_record)
    messages.success(request, 'Fee reminder sent.')
    return redirect('fees:detail', pk=pk)
