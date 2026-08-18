"""
Seeds the database with demo data so you can explore the system immediately:
- 1 admin, 2 teachers, 5 students
- 1 department, 1 course, 2 sections, 3 subjects
- Sample attendance, marks, fees, and timetable entries

Run with: python manage.py seed_demo_data
"""
import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.utils import timezone

from accounts.models import User
from academics.models import Department, Course, Section, Subject
from teachers.models import Teacher
from students.models import Student
from attendance.models import AttendanceRecord
from exams.models import Exam, ExamSubject, Mark
from fees.models import FeeRecord, Payment
from timetable.models import TimetableEntry
from announcements.models import Announcement
from calendarapp.models import AcademicEvent
from library.models import Book, IssueBook
from transport.models import Route, StudentTransport
from hostel.models import Room, HostelAllocation
from parents.models import ParentProfile


class Command(BaseCommand):
    help = "Seed demo data for the Student Management System"

    def handle(self, *args, **options):
        self.stdout.write("Seeding demo data...")

        # --- Admin ---
        if not User.objects.filter(username='admin').exists():
            User.objects.create(
                username='admin', first_name='System', last_name='Admin',
                email='admin@sms.local', role=User.Role.ADMIN,
                password=make_password('admin123'), is_staff=True, is_superuser=True,
            )
            self.stdout.write(self.style.SUCCESS("Created admin (admin / admin123)"))

        # --- Department / Course / Sections / Subjects ---
        dept, _ = Department.objects.get_or_create(code='CSE', defaults={'name': 'Computer Science & Engineering'})
        course, _ = Course.objects.get_or_create(department=dept, name='B.Tech CSE', defaults={'duration_years': 4})
        sec_a, _ = Section.objects.get_or_create(course=course, year=2, semester=3, name='A')
        sec_b, _ = Section.objects.get_or_create(course=course, year=2, semester=3, name='B')

        subjects_data = [
            ('CS201', 'Data Structures', 3),
            ('CS202', 'Database Management Systems', 3),
            ('CS203', 'Operating Systems', 3),
        ]
        subjects = []
        for code, name, credits in subjects_data:
            subj, _ = Subject.objects.get_or_create(
                code=code, defaults={'name': name, 'department': dept, 'semester': 3, 'credits': credits}
            )
            subj.sections.add(sec_a, sec_b)
            subjects.append(subj)

        # --- Teachers ---
        teacher_names = [('rprasad', 'Ramesh', 'Prasad'), ('spatel', 'Sneha', 'Patel')]
        teachers = []
        for username, first, last in teacher_names:
            user, created = User.objects.get_or_create(
                username=username, defaults={
                    'first_name': first, 'last_name': last, 'email': f'{username}@sms.local',
                    'role': User.Role.TEACHER, 'password': make_password('teacher123'),
                }
            )
            teacher, _ = Teacher.objects.get_or_create(
                user=user, defaults={'teacher_id': f'T{100+len(teachers)+1}', 'department': dept,
                                      'qualification': 'M.Tech', 'joining_date': datetime.date(2020, 6, 1)}
            )
            teachers.append(teacher)

        for subj, teacher in zip(subjects, teachers * 2):
            subj.teachers.add(teacher)

        # --- Students ---
        student_names = [
            ('rahul', 'Rahul', 'Sharma'), ('prashanth', 'Prashanth', 'Kumar'),
            ('arun', 'Arun', 'Verma'), ('suresh', 'Suresh', 'Reddy'), ('priya', 'Priya', 'Singh'),
        ]
        students = []
        for i, (username, first, last) in enumerate(student_names):
            user, created = User.objects.get_or_create(
                username=username, defaults={
                    'first_name': first, 'last_name': last, 'email': f'{username}@sms.local',
                    'role': User.Role.STUDENT, 'password': make_password('student123'),
                }
            )
            student, _ = Student.objects.get_or_create(
                user=user, defaults={
                    'student_id': f'S{2001+i}', 'department': dept, 'course': course,
                    'section': sec_a if i % 2 == 0 else sec_b, 'year': 2, 'semester': 3,
                    'admission_date': datetime.date(2024, 7, 1),
                    'parent_name': f'{last} Guardian', 'parent_phone': '9999900000',
                }
            )
            students.append(student)

        # --- Attendance (last 10 days for CS201) ---
        today = datetime.date.today()
        for i in range(10):
            date = today - datetime.timedelta(days=i)
            for idx, student in enumerate(students):
                status = 'PRESENT' if (idx + i) % 4 != 0 else 'ABSENT'
                AttendanceRecord.objects.update_or_create(
                    student=student, subject=subjects[0], date=date,
                    defaults={'status': status, 'teacher': teachers[0]},
                )

        # --- Exams & Marks ---
        exam, _ = Exam.objects.get_or_create(name='Internal 1', semester=3, defaults={'academic_year': '2025-2026', 'date': today})
        for subj in subjects:
            ExamSubject.objects.get_or_create(exam=exam, subject=subj, defaults={'max_marks': 100})
        for idx, student in enumerate(students):
            for subj in subjects:
                exam_subject = ExamSubject.objects.get(exam=exam, subject=subj)
                Mark.objects.update_or_create(
                    student=student, exam_subject=exam_subject,
                    defaults={'marks_obtained': 60 + (idx * 7) % 40}
                )

        # --- Fees ---
        for idx, student in enumerate(students):
            fee, _ = FeeRecord.objects.get_or_create(
                student=student, academic_year='2025-2026',
                defaults={'total_amount': 50000, 'paid_amount': 0}
            )
            if not fee.payments.exists():
                paid_now = 30000 if idx % 2 == 0 else 50000
                Payment.objects.create(
                    fee_record=fee, amount=paid_now, method=Payment.Method.UPI,
                    receipt_number=f'RCPT-{fee.student.student_id}-1'
                )  # Payment.save() auto-updates fee.paid_amount — don't set it manually above.

        # --- Timetable ---
        slots = [(datetime.time(9, 0), datetime.time(10, 0)), (datetime.time(10, 0), datetime.time(11, 0))]
        for day in [1, 2, 3]:
            for si, subj in enumerate(subjects[:2]):
                TimetableEntry.objects.get_or_create(
                    section=sec_a, subject=subj, teacher=teachers[si % 2],
                    day_of_week=day, start_time=slots[si][0], end_time=slots[si][1],
                )

        # --- Announcements ---
        Announcement.objects.get_or_create(
            title='Welcome to the new semester!',
            defaults={'body': 'Classes begin Monday. Please check your timetable.',
                      'audience': Announcement.Audience.ALL, 'pinned': True}
        )
        Announcement.objects.get_or_create(
            title='Internal 1 exam schedule released',
            defaults={'body': 'Check the exams section for your Internal 1 dates.',
                      'audience': Announcement.Audience.STUDENTS}
        )

        # --- Academic calendar ---
        AcademicEvent.objects.get_or_create(
            title='Independence Day', defaults={'category': AcademicEvent.Category.HOLIDAY,
                                                 'start_date': datetime.date(today.year, 8, 15)}
        )
        AcademicEvent.objects.get_or_create(
            title='Internal 1 Exams', defaults={'category': AcademicEvent.Category.EXAM,
                                                 'start_date': today + datetime.timedelta(days=10),
                                                 'end_date': today + datetime.timedelta(days=14)}
        )

        # --- Library ---
        book1, _ = Book.objects.get_or_create(title='Introduction to Algorithms', author='Cormen et al.',
                                               defaults={'quantity': 3, 'isbn': '9780262046305'})
        book2, _ = Book.objects.get_or_create(title='Database System Concepts', author='Silberschatz',
                                               defaults={'quantity': 2, 'isbn': '9780078022159'})
        IssueBook.objects.get_or_create(
            book=book1, student=students[0],
            defaults={'due_date': today + datetime.timedelta(days=14), 'issued_by': teachers[0]}
        )

        # --- Transport ---
        route, _ = Route.objects.get_or_create(
            name='Route 1 - City Center', vehicle_number='TS09AB1234',
            defaults={'driver_name': 'Mohan Rao', 'driver_phone': '9888800000', 'capacity': 40}
        )
        StudentTransport.objects.get_or_create(student=students[0], defaults={'route': route, 'pickup_point': 'Clock Tower'})

        # --- Hostel ---
        room, _ = Room.objects.get_or_create(block='A', room_number='101', defaults={'room_type': Room.RoomType.SHARED, 'capacity': 2})
        HostelAllocation.objects.get_or_create(student=students[1], defaults={'room': room})

        # --- Parent portal ---
        parent_user, created = User.objects.get_or_create(
            username='parent1', defaults={
                'first_name': 'Suresh', 'last_name': 'Sharma (Parent)', 'email': 'parent1@sms.local',
                'role': User.Role.PARENT, 'password': make_password('parent123'),
            }
        )
        parent_profile, _ = ParentProfile.objects.get_or_create(user=parent_user, defaults={'relation': 'Father'})
        parent_profile.children.add(students[0])

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully!"))
        self.stdout.write("Login credentials:")
        self.stdout.write("  Admin:    admin / admin123")
        self.stdout.write("  Teacher:  rprasad / teacher123")
        self.stdout.write("  Student:  rahul / student123")
        self.stdout.write("  Parent:   parent1 / parent123 (linked to Rahul)")