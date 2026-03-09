import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from classes.models import Class
from students.models import Student

c = Class.objects.first()
print(c)
