import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module for 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lcms.settings')

app = Celery('lcms')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'generate-daily-sessions-at-1am': {
        'task': 'tasks.attendance.tasks.generate_daily_sessions_task',
        'schedule': crontab(hour=1, minute=0),
    },
    'auto-end-sessions': {
        'task': 'tasks.attendance.tasks.auto_end_sessions_task',
        'schedule': crontab(minute='*/5'),
    },
    'generate-monthly-tuitions': {
        'task': 'apps.payments.tasks.generate_monthly_tuitions_task',
        'schedule': crontab(hour=2, minute=0),
    },
    'auto-update-class-status': {
        'task': 'classes.tasks.auto_update_class_status',
        'schedule': crontab(hour=3, minute=0),
    },
}
