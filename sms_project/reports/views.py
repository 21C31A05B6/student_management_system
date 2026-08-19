import io
import qrcode
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from accounts.decorators import teacher_required
from students.models import Student
from exams.models import Mark, Exam, calculate_gpa


def _can_view(request, student):
    """Admin/teacher can view any student; a student can only view their own; a parent can view their children."""
    user = request.user
    if not user.is_authenticated:
        return False
    role = getattr(user, 'role', None)
    if role in ('ADMIN', 'TEACHER'):
        return True
    if role == 'STUDENT' and hasattr(user, 'student_profile') and user.student_profile.id == student.id:
        return True
    if role == 'PARENT' and hasattr(user, 'parent_profile') and user.parent_profile.children.filter(id=student.id).exists():
        return True
    return False


@login_required
def report_card_pdf(request, pk, exam_id):
    student = get_object_or_404(Student, pk=pk)
    exam = get_object_or_404(Exam, pk=exam_id)
    if not _can_view(request, student):
        raise Http404()

    marks = Mark.objects.filter(student=student, exam_subject__exam=exam).select_related('exam_subject__subject')

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    c.setFillColor(colors.HexColor('#2d3a8c'))
    c.rect(0, height - 30 * mm, width, 30 * mm, fill=True, stroke=False)
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 18)
    c.drawCentredString(width / 2, height - 15 * mm, "STUDENT MANAGEMENT SYSTEM")
    c.setFont('Helvetica', 12)
    c.drawCentredString(width / 2, height - 23 * mm, f"Report Card — {exam.name}")

    c.setFillColor(colors.black)
    y = height - 45 * mm
    c.setFont('Helvetica-Bold', 11)
    c.drawString(20 * mm, y, f"Student: {student.user.get_full_name()}")
    c.drawString(120 * mm, y, f"ID: {student.student_id}")
    y -= 7 * mm
    c.setFont('Helvetica', 10)
    c.drawString(20 * mm, y, f"Course: {student.course}")
    c.drawString(120 * mm, y, f"Section: {student.section}")

    data = [["Subject", "Marks Obtained", "Max Marks", "Percentage", "Grade"]]
    total_obtained = 0
    total_max = 0
    for m in marks:
        data.append([m.subject.name, str(m.marks_obtained), str(m.max_marks), f"{m.percentage}%", m.grade])
        total_obtained += float(m.marks_obtained)
        total_max += m.max_marks
    overall_pct = round((total_obtained / total_max) * 100, 2) if total_max else 0
    data.append(["Overall", str(total_obtained), str(total_max), f"{overall_pct}%", ""])

    gpa = calculate_gpa(marks)

    table = Table(data, colWidths=[55 * mm, 35 * mm, 30 * mm, 30 * mm, 20 * mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3a8c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#eef1fb')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    table.wrapOn(c, width, height)
    table_y = y - 10 * mm - (len(data) * 8 * mm)
    table.drawOn(c, 20 * mm, table_y)

    if gpa is not None:
        c.setFont('Helvetica-Bold', 11)
        c.drawString(20 * mm, table_y - 10 * mm, f"GPA (this exam): {gpa}")

    c.setFont('Helvetica-Oblique', 8)
    c.drawString(20 * mm, 15 * mm, "This is a system-generated report card.")
    c.showPage()
    c.save()
    buf.seek(0)
    return FileResponse(buf, as_attachment=True, filename=f"report_card_{student.student_id}_{exam.name}.pdf")


@login_required
def id_card_pdf(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if not _can_view(request, student):
        raise Http404()

    buf = io.BytesIO()
    card_w, card_h = 85.6 * mm, 54 * mm  # standard ID card size
    c = canvas.Canvas(buf, pagesize=(card_w, card_h))

    c.setFillColor(colors.HexColor('#2d3a8c'))
    c.rect(0, card_h - 14 * mm, card_w, 14 * mm, fill=True, stroke=False)
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 10)
    c.drawCentredString(card_w / 2, card_h - 9 * mm, "STUDENT ID CARD")

    c.setFillColor(colors.HexColor('#f4f6fb'))
    c.rect(0, 0, card_w, card_h - 14 * mm, fill=True, stroke=False)

    c.setFillColor(colors.black)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(5 * mm, card_h - 20 * mm, student.user.get_full_name())
    c.setFont('Helvetica', 7)
    c.drawString(5 * mm, card_h - 25 * mm, f"ID: {student.student_id}")
    c.drawString(5 * mm, card_h - 29 * mm, f"Course: {student.course}")
    c.drawString(5 * mm, card_h - 33 * mm, f"Section: {student.section}")
    c.drawString(5 * mm, card_h - 37 * mm, f"Dept: {student.department}")

    c.setFont('Helvetica-Oblique', 6)
    c.drawString(5 * mm, 3 * mm, "Valid for current academic year only.")

    c.showPage()
    c.save()
    buf.seek(0)
    return FileResponse(buf, as_attachment=True, filename=f"id_card_{student.student_id}.pdf")


from django.shortcuts import get_object_or_404, render
from academics.models import Subject, Section


@login_required
def student_qr_png(request, pk):
    """Generates a QR code PNG encoding the student's unique attendance token
    (Module: QR-code attendance). Teachers scan this to mark attendance instantly."""
    student = get_object_or_404(Student, pk=pk)
    if not _can_view(request, student):
        raise Http404()
    img = qrcode.make(str(student.qr_token))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return HttpResponse(buf.getvalue(), content_type='image/png')


@login_required
def session_qr_png(request, subject_id, date_str):
    """Generates a QR code PNG for a live class attendance session."""
    subject = get_object_or_404(Subject, pk=subject_id)
    user = request.user
    if user.role == 'TEACHER':
        if not subject.teachers.filter(user=user).exists():
            raise PermissionDenied('You are not assigned to this subject.')
    elif user.role != 'ADMIN':
        raise PermissionDenied('Only teachers and admins may generate session QR codes.')

    qr_data = f"SMS_SESSION:{subject.id}:{date_str}"
    img = qrcode.make(qr_data)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return HttpResponse(buf.getvalue(), content_type='image/png')


@teacher_required
def student_qr_cards(request):
    """Printable sheet of all student QR codes for badges/ID scanning."""
    section_id = request.GET.get('section')
    students = Student.objects.all().select_related('user', 'course', 'section', 'department')
    if section_id:
        students = students.filter(section_id=section_id)
    sections = Section.objects.all()
    return render(request, 'reports/student_qr_cards.html', {
        'students': students,
        'sections': sections,
        'section_id': section_id,
    })
