from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from academics.models import Department, Course, Section, Subject
from accounts.models import User
from exams.models import Exam, ExamSubject, Mark
from fees.models import FeeRecord
from parents.models import ParentProfile
from students.models import Student
from teachers.models import Teacher


class ApiRoleAccessTests(APITestCase):
    def setUp(self):
        self.department = Department.objects.create(code='CSE', name='Computer Science')
        self.course = Course.objects.create(department=self.department, name='B.Tech CSE', duration_years=4)
        self.section_a = Section.objects.create(course=self.course, year=1, semester=1, name='A')
        self.section_b = Section.objects.create(course=self.course, year=1, semester=1, name='B')

        self.admin_user = User.objects.create_user(username='admin', password='pass1234', role='ADMIN')

        self.teacher_user = User.objects.create_user(username='teacher1', password='pass1234', role='TEACHER')
        self.teacher_profile = Teacher.objects.create(user=self.teacher_user, teacher_id='T001', department=self.department)

        self.other_teacher_user = User.objects.create_user(username='teacher2', password='pass1234', role='TEACHER')
        self.other_teacher_profile = Teacher.objects.create(user=self.other_teacher_user, teacher_id='T002', department=self.department)

        self.student_user = User.objects.create_user(username='student1', password='pass1234', role='STUDENT')
        self.student = Student.objects.create(
            user=self.student_user,
            student_id='S001',
            department=self.department,
            course=self.course,
            section=self.section_a,
            year=1,
            semester=1,
        )

        self.other_student_user = User.objects.create_user(username='student2', password='pass1234', role='STUDENT')
        self.other_student = Student.objects.create(
            user=self.other_student_user,
            student_id='S002',
            department=self.department,
            course=self.course,
            section=self.section_b,
            year=1,
            semester=1,
        )

        self.parent_user = User.objects.create_user(username='parent1', password='pass1234', role='PARENT')
        self.parent_profile = ParentProfile.objects.create(user=self.parent_user, relation='Father')
        self.parent_profile.children.add(self.student)

        self.subject = Subject.objects.create(code='CS101', name='Programming', department=self.department, semester=1)
        self.subject.teachers.add(self.teacher_profile)

        self.other_subject = Subject.objects.create(code='CS102', name='Database', department=self.department, semester=1)
        self.other_subject.teachers.add(self.other_teacher_profile)

        self.exam = Exam.objects.create(name='Unit Test', semester=1)
        self.other_exam = Exam.objects.create(name='Midterm', semester=1)

        self.exam_subject = ExamSubject.objects.create(exam=self.exam, subject=self.subject, max_marks=100)
        self.other_exam_subject = ExamSubject.objects.create(exam=self.other_exam, subject=self.other_subject, max_marks=100)

        self.mark = Mark.objects.create(student=self.student, exam_subject=self.exam_subject, marks_obtained=85)
        self.other_mark = Mark.objects.create(student=self.other_student, exam_subject=self.other_exam_subject, marks_obtained=90)

        self.fee_record = FeeRecord.objects.create(student=self.student, academic_year='2025-2026', total_amount=5000, paid_amount=2000)
        self.other_fee_record = FeeRecord.objects.create(student=self.other_student, academic_year='2025-2026', total_amount=6000, paid_amount=3000)

    def test_teacher_sees_only_assigned_subject_marks(self):
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.get(reverse('mark-list'), secure=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item['id'] for item in response.data['results']]
        self.assertIn(self.mark.id, ids)
        self.assertNotIn(self.other_mark.id, ids)

    def test_parent_sees_only_linked_child_records(self):
        self.client.force_authenticate(user=self.parent_user)
        url = reverse('mark-list')
        # Use secure=True to use HTTPS protocol in test
        response = self.client.get(url, secure=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item['id'] for item in response.data['results']]
        self.assertIn(self.mark.id, ids)
        self.assertNotIn(self.other_mark.id, ids)

    def test_student_sees_only_own_marks(self):
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(reverse('mark-list'), secure=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item['id'] for item in response.data['results']]
        self.assertIn(self.mark.id, ids)
        self.assertNotIn(self.other_mark.id, ids)

    # --- Priority 1, issue #2: students/parents must be read-only, even on
    # their own records; teachers may create/update but never delete. ---

    def test_student_cannot_patch_own_mark(self):
        self.client.force_authenticate(user=self.student_user)
        url = reverse('mark-detail', args=[self.mark.id])
        response = self.client.patch(url, {'marks_obtained': 100}, secure=True)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.mark.refresh_from_db()
        self.assertEqual(self.mark.marks_obtained, 85)

    def test_student_cannot_delete_own_mark(self):
        self.client.force_authenticate(user=self.student_user)
        url = reverse('mark-detail', args=[self.mark.id])
        response = self.client.delete(url, secure=True)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Mark.objects.filter(pk=self.mark.id).exists())

    def test_parent_cannot_patch_child_mark(self):
        self.client.force_authenticate(user=self.parent_user)
        url = reverse('mark-detail', args=[self.mark.id])
        response = self.client.patch(url, {'marks_obtained': 100}, secure=True)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_can_patch_assigned_subject_mark(self):
        self.client.force_authenticate(user=self.teacher_user)
        url = reverse('mark-detail', args=[self.mark.id])
        response = self.client.patch(url, {'marks_obtained': 95}, secure=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.mark.refresh_from_db()
        self.assertEqual(self.mark.marks_obtained, 95)

    def test_teacher_cannot_delete_mark(self):
        self.client.force_authenticate(user=self.teacher_user)
        url = reverse('mark-detail', args=[self.mark.id])
        response = self.client.delete(url, secure=True)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Mark.objects.filter(pk=self.mark.id).exists())

    def test_teacher_cannot_patch_other_teachers_subject_mark(self):
        self.client.force_authenticate(user=self.teacher_user)
        url = reverse('mark-detail', args=[self.other_mark.id])
        response = self.client.patch(url, {'marks_obtained': 10}, secure=True)
        self.assertIn(response.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND))

    def test_admin_can_delete_mark(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('mark-detail', args=[self.mark.id])
        response = self.client.delete(url, secure=True)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Mark.objects.filter(pk=self.mark.id).exists())

    def test_marks_obtained_cannot_exceed_max_marks_via_api(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('mark-list')
        response = self.client.post(url, {
            'student': self.student.id, 'exam_subject': self.exam_subject.id, 'marks_obtained': 150,
        }, secure=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_marks_obtained_cannot_be_negative_via_api(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('mark-list')
        response = self.client.post(url, {
            'student': self.student.id, 'exam_subject': self.exam_subject.id, 'marks_obtained': -5,
        }, secure=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_student_cannot_delete_own_fee_record(self):
        self.client.force_authenticate(user=self.student_user)
        url = reverse('feerecord-detail', args=[self.fee_record.id])
        response = self.client.delete(url, secure=True)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(FeeRecord.objects.filter(pk=self.fee_record.id).exists())

    def test_student_cannot_create_student_record(self):
        """A student must not be able to POST a brand new Student row via the API."""
        self.client.force_authenticate(user=self.student_user)
        url = reverse('student-list')
        response = self.client.post(url, {
            'student_id': 'S999', 'department': self.department.id, 'course': self.course.id,
            'section': self.section_a.id, 'year': 1, 'semester': 1,
        }, secure=True)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
