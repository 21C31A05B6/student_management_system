from django.urls import path
from . import views

app_name = 'announcements'

urlpatterns = [
    path('', views.announcement_list, name='list'),
    path('add/', views.announcement_form, name='add'),
    path('<int:pk>/edit/', views.announcement_form, name='edit'),
    path('<int:pk>/delete/', views.announcement_delete, name='delete'),
]
