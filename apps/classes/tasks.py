from celery import shared_task
from django.utils import timezone
from .models import Class

@shared_task
def auto_update_class_status():
    """
    Auto update class status:
    - pending -> active: when start_date is today or passed.
    - active -> completed: when end_date has passed today.
    Additionally, mark active enrollments as completed when class is completed.
    """
    now_date = timezone.now().date()
    # 1. Update from pending -> active
    # Active if start_date <= today and end_date >= today (or simply passed start_date)
    classes_to_activate = Class.objects.filter(
        status='pending',
        start_date__lte=now_date
    )
    activated_count = classes_to_activate.update(status='active')

    # 2. Update from active -> completed
    # Completed if end_date < today
    classes_to_complete = Class.objects.filter(
        status='active',
        end_date__lt=now_date
    )
    
    completed_count = 0
    for c in classes_to_complete:
        c.status = 'completed'
        c.save() # Trigger save to ensure we can capture history potentially
        completed_count += 1
        
        # Mark all active enrollments as completed
        for enrollment in c.enrollments.filter(status='active'):
            enrollment.status = 'completed'
            enrollment.dropped_at = timezone.now()
            enrollment.save()

    return f"Activated: {activated_count}, Completed: {completed_count}"
