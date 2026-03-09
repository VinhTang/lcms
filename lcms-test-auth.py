import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
from accounts.models import User

admin = User.objects.filter(role='admin').first()
c = Client()
c.force_login(admin)

response = c.get('/classes/1/')
content = response.content.decode('utf-8')

if "Thêm học sinh" in content:
    print("Found 'Thêm học sinh' button!")
else:
    print("Not found")
    print(content)
