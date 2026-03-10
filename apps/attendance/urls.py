from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('classes/<int:class_id>/sessions/', views.session_list, name='session_list'),
    path('classes/<str:class_code>/sessions/', views.session_list, name='session_list_by_code'),
    path('classes/<int:class_id>/sessions/create/', views.session_create, name='session_create'),
    path('classes/<str:class_code>/sessions/create/', views.session_create, name='session_create_by_code'),
    path('session/<int:session_id>/', views.session_detail, name='session_detail'),
    path('session/<int:session_id>/open/', views.open_session, name='open_session'),
    path('session/<int:session_id>/end/', views.end_session, name='end_session'),
    path('session/<int:session_id>/notes/', views.save_session_notes, name='save_session_notes'),
    path('session/<int:session_id>/update-timing/', views.update_session_timing, name='update_session_timing'),
    path('attendance/<int:attendance_id>/mark/', views.mark_attendance, name='mark_attendance'),
    path('statistics/', views.session_statistics, name='session_statistics'),
    path('my-sessions/', views.my_sessions, name='my_sessions'),
]
