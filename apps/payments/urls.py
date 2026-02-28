from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('tuitions/', views.tuition_list, name='tuition_list'),
    path('tuitions/create/', views.tuition_create, name='tuition_create'),
    path('tuitions/<int:tuition_id>/', views.tuition_detail, name='tuition_detail'),
    path('tuitions/<int:tuition_id>/mark-paid/', views.mark_paid, name='mark_paid'),
    path('enrollment/<int:enrollment_id>/tuitions/', views.get_enrollment_tuitions, name='get_enrollment_tuitions'),
    path('payments/history/', views.payment_history, name='payment_history'),
    path('my-tuitions/', views.my_tuitions, name='my_tuitions'),
]
