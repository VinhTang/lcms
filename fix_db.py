import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lcms.settings')
django.setup()

from attendance.models import Attendance, ClassSession, AttendanceEditLog

session_ids = set(ClassSession.objects.values_list('id', flat=True))
invalid_attendances = Attendance.objects.exclude(class_session_id__in=session_ids)

count, _ = invalid_attendances.delete()
print(f"Deleted {count} invalid Attendance records.")

invalid_logs = AttendanceEditLog.objects.exclude(attendance_id__in=set(Attendance.objects.values_list('id', flat=True)))
logs_count, _ = invalid_logs.delete()
print(f"Deleted {logs_count} invalid AttendanceEditLog records.")
