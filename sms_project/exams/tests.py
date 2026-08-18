from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from academics.models import Department, Course, Section, Subject
from accounts.models import User
from students.models import Student
from .models import Exam, ExamSubject, Mark, calculate_gpa, calculate_cgpa


class MarksValidationTests(TestCase):
    """Priority 1, issue #3: marks must be within [0, max_marks] at the
    model level, not just enforced by the HTML form."""

    def setUp(self):
        self.department = Department.objects.create(code='CSE', name='Computer Science')
        self.course = Course.objects.create(department=self.department, name='B.Tech CSE', duration_years=4)
        self.section = Section.objects.create(course=self.course, year=1, semester=1, name='A')
        self.subject = Subject.objects.create(code='CS101', name='Programming', department=self.department, semester=1, credits=4)
        self.user = User.objects.create_user(username='stu1', password='pass1234', role='STUDENT')
        self.student = Student.objects.create(
            user=self.user, student_id='S001', department=self.department,
            course=self.course, section=self.section, year=1, semester=1,
        )
        self.exam = Exam.objects.create(name='Internal 1', semester=1)
        self.exam_subject = ExamSubject.objects.create(exam=self.exam, subject=self.subject, max_marks=100)

    def test_marks_exceeding_max_marks_rejected(self):
        mark = Mark(student=self.student, exam_subject=self.exam_subject, marks_obtained=Decimal('150'))
        with self.assertRaises(ValidationError):
            mark.save()

    def test_negative_marks_rejected(self):
        mark = Mark(student=self.student, exam_subject=self.exam_subject, marks_obtained=Decimal('-20'))
        with self.assertRaises(ValidationError):
            mark.save()

    def test_valid_marks_accepted(self):
        mark = Mark.objects.create(student=self.student, exam_subject=self.exam_subject, marks_obtained=Decimal('85'))
        self.assertEqual(mark.percentage, 85.0)
        self.assertEqual(mark.grade, 'A')

    def test_marks_at_exact_boundary_accepted(self):
        mark = Mark.objects.create(student=self.student, exam_subject=self.exam_subject, marks_obtained=Decimal('100'))
        self.assertEqual(mark.percentage, 100.0)
        self.assertEqual(mark.grade, 'A+')

    def test_zero_marks_accepted(self):
        mark = Mark.objects.create(student=self.student, exam_subject=self.exam_subject, marks_obtained=Decimal('0'))
        self.assertEqual(mark.grade, 'F')

    def test_different_subjects_can_have_different_max_marks(self):
        """Priority 1, issue #5: per-subject max marks within the same exam."""
        subject2 = Subject.objects.create(code='CS102', name='Lab', department=self.department, semester=1, credits=2)
        exam_subject2 = ExamSubject.objects.create(exam=self.exam, subject=subject2, max_marks=50)
        mark2 = Mark.objects.create(student=self.student, exam_subject=exam_subject2, marks_obtained=Decimal('45'))
        self.assertEqual(mark2.percentage, 90.0)
        # 45 would be invalid against a 100-max subject's boundary logic but
        # valid here against the 50-max — confirms independence per subject.
        with self.assertRaises(ValidationError):
            Mark(student=self.student, exam_subject=exam_subject2, marks_obtained=Decimal('60')).save()


class GpaCgpaTests(TestCase):
    """Priority 2, issue #8: GPA = sum(credit * grade_point) / sum(credits)."""

    def setUp(self):
        self.department = Department.objects.create(code='CSE', name='Computer Science')
        self.course = Course.objects.create(department=self.department, name='B.Tech CSE', duration_years=4)
        self.section = Section.objects.create(course=self.course, year=1, semester=1, name='A')
        self.user = User.objects.create_user(username='stu2', password='pass1234', role='STUDENT')
        self.student = Student.objects.create(
            user=self.user, student_id='S002', department=self.department,
            course=self.course, section=self.section, year=1, semester=1,
        )
        self.exam = Exam.objects.create(name='Internal 1', semester=1)

        self.subj_a = Subject.objects.create(code='A1', name='Subject A', department=self.department, semester=1, credits=4)
        self.subj_b = Subject.objects.create(code='B1', name='Subject B', department=self.department, semester=1, credits=3)

        self.es_a = ExamSubject.objects.create(exam=self.exam, subject=self.subj_a, max_marks=100)
        self.es_b = ExamSubject.objects.create(exam=self.exam, subject=self.subj_b, max_marks=100)

    def test_gpa_calculation(self):
        # Subject A: 95% -> A+ -> 10 points, 4 credits
        # Subject B: 85% -> A  -> 9 points, 3 credits
        # GPA = (4*10 + 3*9) / (4+3) = 67/7 = 9.57
        Mark.objects.create(student=self.student, exam_subject=self.es_a, marks_obtained=Decimal('95'))
        Mark.objects.create(student=self.student, exam_subject=self.es_b, marks_obtained=Decimal('85'))

        marks = Mark.objects.filter(student=self.student, exam_subject__exam=self.exam)
        gpa = calculate_gpa(marks)
        self.assertAlmostEqual(float(gpa), 9.57, places=2)

    def test_cgpa_across_multiple_exams(self):
        Mark.objects.create(student=self.student, exam_subject=self.es_a, marks_obtained=Decimal('95'))
        Mark.objects.create(student=self.student, exam_subject=self.es_b, marks_obtained=Decimal('85'))

        exam2 = Exam.objects.create(name='Internal 2', semester=1)
        es_a2 = ExamSubject.objects.create(exam=exam2, subject=self.subj_a, max_marks=100)
        Mark.objects.create(student=self.student, exam_subject=es_a2, marks_obtained=Decimal('50'))

        cgpa = calculate_cgpa(self.student)
        self.assertIsNotNone(cgpa)

    def test_gpa_none_when_no_marks(self):
        gpa = calculate_gpa(Mark.objects.none())
        self.assertIsNone(gpa)
