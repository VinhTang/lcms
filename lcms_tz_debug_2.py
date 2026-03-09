import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lcms.settings')
django.setup()

from django.utils import timezone
from datetime import datetime, timedelta
from attendance.models import ClassSession

now = timezone.now()
print(f"now(): {now}")

try:
    sessions = ClassSession.objects.filter(scheduled_date='2026-03-01', class_enrolled__class_name__icontains='Ly')
    for session in sessions:
        print(f"Session {session.id} for {session.class_enrolled.class_name} | {session.scheduled_start} - {session.scheduled_end} | Status: {session.status}")
        
        scheduled_datetime = timezone.make_aware(datetime.combine(session.scheduled_date, session.scheduled_start))
        scheduled_end_datetime = timezone.make_aware(datetime.combine(session.scheduled_date, session.scheduled_end))
        
        min_time = scheduled_datetime - timedelta(minutes=15)
        print(f"  min_time: {min_time}")
        print(f"  now < min_time (Quá sớm): {now < min_time}")
        print(f"  now > scheduled_end_datetime (Đã kết thúc): {now > scheduled_end_datetime}")
        
        if now < min_time:
            print("  -> ERROR: Chưa đến giờ nhận lớp")
        elif now > scheduled_end_datetime:
            print("  -> ERROR: Buổi học đã kết thúc")
        else:
            print("  -> OK: Có thể nhận lớp")
            
except Exception as e:
    print("Error:", e)
