from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('students/', views.student_list, name='list'),
    path('students/create/', views.student_create, name='create'),
    path('students/<int:student_id>/', views.student_detail, name='detail'),
    path('students/<int:student_id>/edit/', views.student_edit, name='edit'),
    path('students/<int:student_id>/delete/', views.student_delete, name='delete'),
    path('my-children/', views.my_children, name='my_children'),
]
