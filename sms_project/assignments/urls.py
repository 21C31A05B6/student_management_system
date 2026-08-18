from django.urls import path
from . import views

app_name = 'assignments'

urlpatterns = [
    path('', views.assignment_list, name='list'),
    path('add/', views.assignment_form, name='add'),
    path('<int:pk>/edit/', views.assignment_form, name='edit'),
    path('<int:pk>/delete/', views.assignment_delete, name='delete'),
    path('<int:pk>/submissions/', views.assignment_submissions, name='submissions'),
    path('my/', views.my_assignments, name='my_assignments'),
    path('<int:pk>/submit/', views.submit_assignment, name='submit'),
]
