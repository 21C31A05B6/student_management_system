from django.urls import path
from . import views

app_name = 'calendarapp'

urlpatterns = [
    path('', views.event_list, name='list'),
    path('add/', views.event_form, name='add'),
    path('<int:pk>/edit/', views.event_form, name='edit'),
    path('<int:pk>/delete/', views.event_delete, name='delete'),
]
