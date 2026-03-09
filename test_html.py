import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lcms.settings')
django.setup()
from django.test.client import Client
from accounts.models import User
c = Client()
c.force_login(User.objects.filter(role='admin').first())
response = c.get('/users/activity-logs/')
if response.status_code == 500:
    import sys, traceback
    try:
        c.get('/users/activity-logs/')
    except Exception as e:
        traceback.print_exc()
print("Status:", response.status_code)
