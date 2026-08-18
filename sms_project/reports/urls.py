from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('report-card/<int:pk>/<int:exam_id>/', views.report_card_pdf, name='report_card'),
    path('id-card/<int:pk>/', views.id_card_pdf, name='id_card'),
    path('qr/<int:pk>/', views.student_qr_png, name='student_qr'),
    path('session-qr/<int:subject_id>/<str:date_str>/', views.session_qr_png, name='session_qr'),
    path('qr-cards/', views.student_qr_cards, name='student_qr_cards'),
]
