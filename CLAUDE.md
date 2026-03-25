# LCMS Portal - Claude Code Guide

## 🚀 Setup & Run Commands
- **Install dependencies**: `pip install -r requirements.txt`
- **Run local server**: `python manage.py runserver`
- **Apply migrations**: `python manage.py migrate`
- **Make migrations**: `python manage.py makemigrations`
- **Create superuser**: `python manage.py createsuperuser`
- **Collect static files**: `python manage.py collectstatic --noinput`
- **Run Celery worker**: `celery -A lcms worker -l info`

## 🧪 Testing & Linting
- **Run tests**: `python manage.py test`
- **Run specific test**: `python manage.py test <app_name>`

## 📁 Project Structure
- Django backend with `django-allauth` for authentication, `celery` for background tasks, and `redis`.
- Main configuration is in the `lcms/` folder.
- Django apps are located in the `apps/` directory.
- HTML Templates are in `templates/` and static assets in `static/`.

## 🛠️ Code Style & Guidelines
- Follow PEP 8 guidelines for Python code.
- Prefer class-based views (CBVs) or simple functional views depending on complexity.
- Keep business logic in models, managers, or separate service modules rather than in views.
- Use Django ORM efficiently (`select_related` and `prefetch_related`).
- Use informative commit messages.
