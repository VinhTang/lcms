import os
import django

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lcms.settings")
django.setup()

from accounts.models import User

def create_initial_admin():
    email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
    password = os.environ.get('ADMIN_PASSWORD', 'Admin@123')
    first_name = os.environ.get('ADMIN_FIRST_NAME', 'Admin')
    last_name = os.environ.get('ADMIN_LAST_NAME', 'System')

    if not User.objects.filter(email=email).exists():
        print(f"Creating superuser: {email}...")
        User.objects.create_superuser(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role='admin'
        )
        print("Superuser created successfully!")
    else:
        print(f"User with email {email} already exists.")

if __name__ == "__main__":
    create_initial_admin()
