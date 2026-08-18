from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('add/', views.book_form, name='book_add'),
    path('<int:pk>/edit/', views.book_form, name='book_edit'),
    path('<int:pk>/delete/', views.book_delete, name='book_delete'),
    path('issues/', views.issue_list, name='issue_list'),
    path('issues/add/', views.issue_form, name='issue_add'),
    path('issues/<int:pk>/return/', views.issue_return, name='issue_return'),
    path('issues/<int:pk>/fine-paid/', views.fine_paid, name='fine_paid'),
    path('my-books/', views.my_books, name='my_books'),
]
