from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    path('manage/', views.exam_list, name='exam_list'),
    path('manage/add/', views.exam_form, name='exam_add'),
    path('manage/<int:pk>/edit/', views.exam_form, name='exam_edit'),
    path('manage/<int:pk>/delete/', views.exam_delete, name='exam_delete'),
    path('manage/subjects/add/', views.exam_subject_form, name='exam_subject_add'),
    path('manage/subjects/<int:pk>/edit/', views.exam_subject_form, name='exam_subject_edit'),
    path('manage/subjects/<int:pk>/delete/', views.exam_subject_delete, name='exam_subject_delete'),
    path('marks-entry/', views.marks_entry, name='marks_entry'),
    path('my/', views.my_marks, name='my_marks'),
]
