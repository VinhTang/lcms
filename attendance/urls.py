from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('class/<int:class_id>/sessions/', views.session_list, name='session_list'),
    path('class/<int:class_id>/sessions/create/', views.session_create, name='session_create'),
    path('session/<int:session_id>/', views.session_detail, name='session_detail'),
    path('session/<int:session_id>/open/', views.open_session, name='open_session'),
    path('session/<int:session_id>/end/', views.end_session, name='end_session'),
    path('attendance/<int:attendance_id>/mark/', views.mark_attendance, name='mark_attendance'),
    path('my-sessions/', views.my_sessions, name='my_sessions'),
]
