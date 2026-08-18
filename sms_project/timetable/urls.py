from django.urls import path
from . import views

app_name = 'timetable'

urlpatterns = [
    path('', views.view_timetable, name='view'),
    path('manage/', views.timetable_manage, name='manage'),
    path('manage/add/', views.timetable_form, name='add'),
    path('manage/<int:pk>/edit/', views.timetable_form, name='edit'),
    path('manage/<int:pk>/delete/', views.timetable_delete, name='delete'),
]
