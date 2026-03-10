from django.urls import path
from . import views

app_name = 'classes'

urlpatterns = [
    path('classes/', views.class_list, name='list'),
    path('classes/create/', views.class_create, name='create'),
    path('classes/<int:class_id>/', views.class_detail, name='detail'),
    path('classes/<int:class_id>/edit/', views.class_edit, name='edit'),
    path('classes/<int:class_id>/delete/', views.class_delete, name='delete'),
    path('classes/<int:class_id>/enroll-students/', views.class_enroll_students, name='enroll_students'),
    path('enrollments/<int:enrollment_id>/drop/', views.drop_student, name='drop_student'),
    path('my-classes/', views.my_classes, name='my_classes'),
]
