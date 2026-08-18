from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('mark/', views.mark_attendance, name='mark'),
    path('qr-scan/', views.qr_scan, name='qr_scan'),
    path('my/', views.my_attendance, name='my_attendance'),
]
