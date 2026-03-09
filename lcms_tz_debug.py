import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lcms.settings')
django.setup()

from django.utils import timezone
from datetime import datetime, timedelta
from attendance.models import ClassSession
from django.conf import settings

print(f"USE_TZ: {settings.USE_TZ}")
print(f"TIME_ZONE: {settings.TIME_ZONE}")

now = timezone.now()
print(f"now(): {now}")

try:
    session = ClassSession.objects.get(id=14)
    print(f"Session {session.id}: {session.scheduled_date} | {session.scheduled_start} - {session.scheduled_end}")
    
    scheduled_datetime = timezone.make_aware(datetime.combine(session.scheduled_date, session.scheduled_start))
    scheduled_end_datetime = timezone.make_aware(datetime.combine(session.scheduled_date, session.scheduled_end))
    
    print(f"scheduled_datetime: {scheduled_datetime}")
    print(f"scheduled_end_datetime: {scheduled_end_datetime}")
    
    min_time = scheduled_datetime - timedelta(minutes=15)
    print(f"min_time to check in: {min_time}")
    
    print(f"session status: {session.status}")
    print(f"now < min_time: {now < min_time}")
    print(f"now > scheduled_end_datetime: {now > scheduled_end_datetime}")
except Exception as e:
    print("Error:", e)
