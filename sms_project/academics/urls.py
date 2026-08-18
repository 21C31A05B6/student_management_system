from django.urls import path
from . import views

app_name = 'academics'

urlpatterns = [
    path('departments/', views.department_list, name='department_list'),
    path('departments/add/', views.department_form, name='department_add'),
    path('departments/<int:pk>/edit/', views.department_form, name='department_edit'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),

    path('courses/', views.course_list, name='course_list'),
    path('courses/add/', views.course_form, name='course_add'),
    path('courses/<int:pk>/edit/', views.course_form, name='course_edit'),
    path('courses/<int:pk>/delete/', views.course_delete, name='course_delete'),

    path('sections/', views.section_list, name='section_list'),
    path('sections/add/', views.section_form, name='section_add'),
    path('sections/<int:pk>/edit/', views.section_form, name='section_edit'),
    path('sections/<int:pk>/delete/', views.section_delete, name='section_delete'),

    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/add/', views.subject_form, name='subject_add'),
    path('subjects/<int:pk>/edit/', views.subject_form, name='subject_edit'),
    path('subjects/<int:pk>/delete/', views.subject_delete, name='subject_delete'),
]
