from django.urls import path
from . import views

app_name = 'hostel'

urlpatterns = [
    path('', views.room_list, name='room_list'),
    path('add/', views.room_form, name='room_add'),
    path('<int:pk>/edit/', views.room_form, name='room_edit'),
    path('<int:pk>/delete/', views.room_delete, name='room_delete'),
    path('allocate/', views.allocate_form, name='allocate'),
    path('vacate/<int:pk>/', views.vacate, name='vacate'),
]
