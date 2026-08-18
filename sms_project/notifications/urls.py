from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='list'),
    path('send/', views.send_notification, name='send'),
    path('fee-reminder/<int:pk>/', views.send_fee_reminder, name='fee_reminder'),
]
