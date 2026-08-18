from django.urls import path
from . import views

app_name = 'transport'

urlpatterns = [
    path('', views.route_list, name='route_list'),
    path('add/', views.route_form, name='route_add'),
    path('<int:pk>/edit/', views.route_form, name='route_edit'),
    path('<int:pk>/delete/', views.route_delete, name='route_delete'),
    path('assign/', views.assignment_form, name='assign'),
]
