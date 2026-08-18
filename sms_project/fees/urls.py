from django.urls import path
from . import views

app_name = 'fees'

urlpatterns = [
    path('', views.fee_list, name='list'),
    path('add/', views.fee_form, name='add'),
    path('<int:pk>/', views.fee_detail, name='detail'),
    path('<int:pk>/edit/', views.fee_form, name='edit'),
    path('<int:pk>/delete/', views.fee_delete, name='delete'),
    path('payments/<int:pk>/delete/', views.payment_delete, name='payment_delete'),
    path('my/', views.my_fees, name='my_fees'),
]
