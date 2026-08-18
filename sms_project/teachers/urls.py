from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [
    path('', views.teacher_list, name='list'),
    path('add/', views.teacher_form, name='add'),
    path('<int:pk>/', views.teacher_detail, name='detail'),
    path('<int:pk>/edit/', views.teacher_form, name='edit'),
    path('<int:pk>/delete/', views.teacher_delete, name='delete'),
]
