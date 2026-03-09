from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.user_list, name='list'),
    path('create/', views.user_create, name='create'),
    path('<int:user_id>/edit/', views.user_edit, name='edit'),
    path('<int:user_id>/delete/', views.user_delete, name='delete'),
    path('<int:user_id>/toggle-lock/', views.user_toggle_lock, name='toggle_lock'),
    path('<int:user_id>/', views.user_detail, name='detail'),
    path('activity-logs/', views.activity_logs, name='activity_logs'),
    path('<str:app_label>/<str:model_name>/<int:object_id>/history/', views.object_history, name='object_history'),
]
