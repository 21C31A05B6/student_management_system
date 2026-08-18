from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('departments', views.DepartmentViewSet)
router.register('courses', views.CourseViewSet)
router.register('subjects', views.SubjectViewSet)
router.register('students', views.StudentViewSet)
router.register('teachers', views.TeacherViewSet)
router.register('attendance', views.AttendanceViewSet)
router.register('exams', views.ExamViewSet)
router.register('exam-subjects', views.ExamSubjectViewSet)
router.register('marks', views.MarkViewSet)
router.register('fees', views.FeeRecordViewSet)

urlpatterns = router.urls
