from celery import shared_task
from django.utils import timezone
from attendance.models import ClassSession
from classes.models import Class
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

@shared_task
def generate_daily_sessions_task():
    today = timezone.localtime(timezone.now()).date()
    
    # User requirement: 0=Sunday, 1=Monday, ..., 6=Saturday
    # Python weekday(): 0=Monday, 1=Tuesday, ..., 6=Sunday
    # We map Python's weekday() to our new model representation
    day_mapping_reverse = {
        0: '1',  # Monday -> 1
        1: '2',  # Tuesday -> 2
        2: '3',  # Wednesday -> 3
        3: '4',  # Thursday -> 4
        4: '5',  # Friday -> 5
        5: '6',  # Saturday -> 6
        6: '0'   # Sunday -> 0
    }
    today_str = day_mapping_reverse[today.weekday()]
    classes = Class.objects.filter(
        start_date__lte=today,
        end_date__gte=today,
    )
    created_count = 0
    for cls in classes:
        if not cls.schedule_days:
            continue
            
        schedule_days = [d.strip() for d in cls.schedule_days.split(',')]
        if today_str in schedule_days:
            exists = ClassSession.objects.filter(
                class_enrolled=cls,
                scheduled_date=today
            ).exists()
            
            if not exists:
                ClassSession.objects.create(
                    class_enrolled=cls,
                    teacher=cls.teacher,
                    scheduled_date=today,
                    scheduled_start=cls.start_time,
                    scheduled_end=cls.end_time,
                    status='not_started'
                )
                created_count += 1
                
    logger.info(f"Daily Sessions Job Generated {created_count} sessions for {today}.")
    return created_count

@shared_task
def auto_end_sessions_task():
    """
    Checks all in-progress sessions. If current time is past the scheduled_end time,
    automatically marks the session as 'ended' and leaves a note.
    """
    now = timezone.localtime(timezone.now())
    current_time = now.time()
    
    in_progress_sessions = ClassSession.objects.filter(
        Q(status='in_progress') | Q(status='not_started'),
        scheduled_date__lte=now.date()
    )
    
    ended_count = 0
    for session in in_progress_sessions:
        if session.scheduled_date < now.date() or (session.scheduled_date == now.date() and session.scheduled_end < current_time):
            session.status = 'ended'
            session.actual_end = now
            
            auto_note = "[Hệ thống] Lớp đã kết thúc tự động do quá thời gian quy định."
            if session.notes:
                session.notes = f"{session.notes}\n{auto_note}"
            else:
                session.notes = auto_note
                
            session.save(update_fields=['status', 'actual_end', 'notes'])
            ended_count += 1
            
    if ended_count > 0:
        logger.info(f"Auto-ended {ended_count} overdue sessions.")
    return ended_count
