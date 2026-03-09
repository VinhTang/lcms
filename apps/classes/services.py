from datetime import timedelta, datetime
from attendance.models import ClassSession
from django.utils import timezone

def generate_class_sessions(class_obj):
    """
    Auto-generates ClassSession records between class_obj.start_date and class_obj.end_date
    matching the schedule_days (e.g. '2,4,6')
    """
    if not class_obj.start_date or not class_obj.end_date or not class_obj.schedule_days:
        return 0

    # Parse schedule_days (e.g. "2,4,6" -> [0, 2, 4])
    # Note: user inputted Mon=2, Sun=8 so weekday() which is Mon=0, Sun=6 needs mapping
    # 2 -> 0, 3 -> 1, 4 -> 2, 5 -> 3, 6 -> 4, 7 -> 5, 1 -> 6
    day_mapping = {
        '2': 0, '3': 1, '4': 2, '5': 3, '6': 4, '7': 5, '1': 6
    }
    
    valid_weekdays = []
    for day in class_obj.schedule_days.split(','):
        day = day.strip()
        if day in day_mapping:
            valid_weekdays.append(day_mapping[day])
            
    if not valid_weekdays:
        return 0
        
    
    start_date = class_obj.start_date
    end_date = class_obj.end_date
    
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        
    current_date = start_date
    sessions_created = 0
    
    while current_date <= end_date:
        if current_date.weekday() in valid_weekdays:
            # Check if session already exists for this date and class
            exists = ClassSession.objects.filter(
                class_enrolled=class_obj,
                scheduled_date=current_date
            ).exists()
            
            if not exists:
                ClassSession.objects.create(
                    class_enrolled=class_obj,
                    teacher=class_obj.teacher,
                    scheduled_date=current_date,
                    scheduled_start=class_obj.start_time,
                    scheduled_end=class_obj.end_time,
                    status='not_started'
                )
                sessions_created += 1
                
        current_date += timedelta(days=1)
        
    return sessions_created
