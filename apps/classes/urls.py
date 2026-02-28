from django.urls import path
from . import views

app_name = 'classes'

urlpatterns = [
    path('classes/', views.class_list, name='list'),
    path('classes/create/', views.class_create, name='create'),
    path('classes/<int:class_id>/', views.class_detail, name='detail'),
    path('classes/<int:class_id>/edit/', views.class_edit, name='edit'),
    path('classes/<int:class_id>/delete/', views.class_delete, name='delete'),
    path('my-classes/', views.my_classes, name='my_classes'),
]
