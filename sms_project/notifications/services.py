"""Central place that sends email/SMS and always logs a Notification record."""
from django.conf import settings
from django.core.mail import send_mail
from .models import Notification


def send_email_notification(user, subject, message):
    status = Notification.Status.SENT
    try:
        if user.email:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
        else:
            status = Notification.Status.FAILED
    except Exception:
        status = Notification.Status.FAILED
    return Notification.objects.create(
        recipient_user=user, channel=Notification.Channel.EMAIL,
        subject=subject, message=message, status=status,
    )


def send_sms_notification(user, message):
    """Sends SMS via Twilio if TWILIO_* env vars are configured, otherwise
    logs the message to console + the Notification table (safe local default)."""
    status = Notification.Status.SENT
    phone = getattr(user, 'phone', '')
    if settings.SMS_BACKEND == 'twilio' and settings.TWILIO_ACCOUNT_SID and phone:
        try:
            from twilio.rest import Client
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(body=message, from_=settings.TWILIO_FROM_NUMBER, to=phone)
        except Exception:
            status = Notification.Status.FAILED
    else:
        print(f"[SMS to {phone or 'unknown number'}] {message}")
        if not phone:
            status = Notification.Status.FAILED
    return Notification.objects.create(
        recipient_user=user, channel=Notification.Channel.SMS,
        message=message, status=status,
    )


import urllib.parse


def get_whatsapp_url(phone, message):
    """Generates a direct WhatsApp web/app link to send the message in 1 click."""
    if not phone:
        return ""
    # Extract only digits
    digits = ''.join(c for c in str(phone) if c.isdigit())
    if len(digits) == 10:
        digits = '91' + digits  # Default India country code if 10 digits
    encoded = urllib.parse.quote(message)
    return f"https://api.whatsapp.com/send?phone={digits}&text={encoded}"


def send_whatsapp_notification(phone, message, user=None):
    """Sends WhatsApp message to parent via Twilio WhatsApp API if configured,
    otherwise prints to console and records in the Notification model (zero-setup mode)."""
    status = Notification.Status.SENT
    phone_clean = (phone or '').strip()
    
    # Format phone number for international format if missing '+'
    if phone_clean and not phone_clean.startswith('+'):
        if len(phone_clean) == 10:
            phone_clean = '+91' + phone_clean
        else:
            phone_clean = '+' + phone_clean

    whatsapp_backend = getattr(settings, 'WHATSAPP_BACKEND', 'console')
    twilio_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
    twilio_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
    twilio_from = getattr(settings, 'TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886')

    if whatsapp_backend == 'twilio' and twilio_sid and twilio_token and phone_clean:
        try:
            from twilio.rest import Client
            client = Client(twilio_sid, twilio_token)
            from_wa = twilio_from if twilio_from.startswith('whatsapp:') else f"whatsapp:{twilio_from}"
            to_wa = f"whatsapp:{phone_clean}"
            client.messages.create(body=message, from_=from_wa, to=to_wa)
            print(f"[WhatsApp SENT via Twilio to {to_wa}] {message}")
        except Exception as e:
            print(f"[WhatsApp Error to {phone_clean}] {e}")
            status = Notification.Status.FAILED
    else:
        print(f"\n💬 [WhatsApp to Parent: {phone_clean or 'No Phone Listed'}]\n{message}\n")
        if not phone_clean:
            status = Notification.Status.FAILED

    return Notification.objects.create(
        recipient_user=user,
        channel=Notification.Channel.WHATSAPP,
        subject="Attendance WhatsApp Notification",
        message=f"[Parent WhatsApp: {phone_clean}] {message}",
        status=status,
    )


def notify_attendance(student, subject, date, status='PRESENT'):
    """Sends WhatsApp notification (and Email/SMS) to parents when attendance is marked PRESENT or ABSENT."""
    student_name = student.user.get_full_name() or student.user.username
    subject_name = subject.name if subject else "Class"
    
    # WhatsApp message formatting
    if status == 'PRESENT':
        msg = (
            f"✅ *Attendance Update - SMS Academy*\n\n"
            f"Dear Parent,\n"
            f"Your ward *{student_name}* (ID: {student.student_id}) has been marked *PRESENT* "
            f"for *{subject_name}* on *{date}*.\n\n"
            f"Best regards,\nSMS Academy"
        )
    elif status == 'ABSENT':
        msg = (
            f"⚠️ *Attendance Alert - SMS Academy*\n\n"
            f"Dear Parent,\n"
            f"Your ward *{student_name}* (ID: {student.student_id}) was marked *ABSENT* "
            f"for *{subject_name}* on *{date}*.\n\n"
            f"Please contact the administration if you have any questions."
        )
    else:
        msg = (
            f"ℹ️ *Attendance Update - SMS Academy*\n\n"
            f"Dear Parent,\n"
            f"Your ward *{student_name}* (ID: {student.student_id}) status is *{status}* "
            f"for *{subject_name}* on *{date}*."
        )

    # Collect parent phone numbers
    parent_phones = []
    if student.parent_phone:
        parent_phones.append(student.parent_phone)

    # Check linked parent accounts (Module: Parents)
    for p_prof in student.parent_profiles.all():
        if p_prof.user.phone and p_prof.user.phone not in parent_phones:
            parent_phones.append(p_prof.user.phone)

    # Fallback to student phone if no parent phone
    if not parent_phones and student.user.phone:
        parent_phones.append(student.user.phone)

    recipient_user = None
    if student.parent_profiles.exists():
        recipient_user = student.parent_profiles.first().user
    else:
        recipient_user = student.user

    # Send WhatsApp notification to all parent numbers found
    if parent_phones:
        for ph in parent_phones:
            send_whatsapp_notification(ph, msg, user=recipient_user)
    else:
        send_whatsapp_notification('', msg, user=recipient_user)

    # If ABSENT, also trigger SMS & Email for redundancy
    if status == 'ABSENT':
        if student.user.email:
            send_email_notification(student.user, "Attendance Alert: Absent", msg)
        if student.user.phone:
            send_sms_notification(student.user, msg)


def notify_absentee(student, subject, date):
    """Backwards-compatible wrapper calling notify_attendance with ABSENT."""
    notify_attendance(student, subject, date, status='ABSENT')


def notify_fee_due(fee_record):
    text = f"Fee due for {fee_record.academic_year}: ₹{fee_record.due_amount}. Please pay at the earliest."
    send_email_notification(fee_record.student.user, "Fee Reminder", text)
    send_sms_notification(fee_record.student.user, text)

