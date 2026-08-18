from django.urls import path
from . import views

app_name = 'parents'

urlpatterns = [
    path('', views.parent_list, name='list'),
    path('add/', views.parent_form, name='add'),
    path('edit/<int:pk>/', views.parent_form, name='edit'),
    path('portal/', views.parent_portal, name='portal'),
]
