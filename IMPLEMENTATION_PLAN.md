# LCMS - Learning Center Management System

## Project Overview

Django-based Education Center Management System with SPA-like experience using HTMX + Alpine.js + TailwindCSS.

## Tech Stack

- **Backend**: Django 5.0+
- **Frontend**: TailwindCSS (CDN), Alpine.js, HTMX
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Auth**: django-allauth

## Features

### 1. Authentication

- Custom login with email/username
- Role-based access (admin, teacher, assistant, parent)
- Domain generation: `<lastname><firstname>` (e.g., "Nguyễn Văn Nam" → "namnv")

### 2. User Management (Admin)

- Create/Edit/Delete users
- Roles: Admin, Teacher, Assistant, Parent

### 3. Student Management

- Create/Edit/Delete students (soft delete)
- Fields: full_name, domain, birth_year, school, gender, emergency_call, status
- Link students to parents

### 4. Class Management

- Create/Edit/Delete classes
- Subjects (auto-create on-the-fly)
- Schedule: checkbox days + time pickers
- Teacher assignment
- Enrollment management

### 5. Attendance System

- Class sessions with scheduled date/time
- Open class 15min before, auto-end 30min after
- Mark attendance: present, absent with permission, absent without permission
- Attendance history

### 6. Payment/Tuition Management

- Monthly or course-based tuition
- Due date tracking
- Payment history
- Parent view for children's tuition

## Project Structure

```
lcms-portal/
├── lcms/                    # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/               # Authentication & User
│   ├── models.py          # Custom User with domain generation
│   ├── views.py           # Login, logout, dashboard
│   └── urls.py
├── users/                 # User CRUD (Admin)
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── students/              # Student CRUD
│   ├── models.py          # Student with soft delete
│   ├── views.py
│   └── urls.py
├── classes/               # Class & Subject management
│   ├── models.py          # Class, Subject, Enrollment
│   ├── views.py
│   └── urls.py
├── attendance/            # Attendance tracking
│   ├── models.py          # ClassSession, Attendance
│   ├── views.py
│   └── urls.py
├── payments/              # Tuition management
│   ├── models.py          # Tuition, PaymentHistory
│   ├── views.py
│   └── urls.py
├── templates/
│   ├── base.html          # SPA layout with HTMX + Alpine.js
│   ├── accounts/          # Login, Dashboard
│   ├── users/             # List, Form, Delete
│   ├── students/          # List, Form, Detail, Delete
│   ├── classes/           # List, Form, Detail, Delete
│   ├── attendance/        # Session management
│   └── payments/         # Tuition management
└── requirements.txt
```

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

## Default Credentials

- Email: admin@lcms.com
- Password: admin123

## Frontend Libraries (CDN)

| Library      | CDN                                                                       |
| ------------ | ------------------------------------------------------------------------- |
| TailwindCSS  | https://cdn.tailwindcss.com                                               |
| Alpine.js    | https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js                          |
| HTMX         | https://unpkg.com/htmx.org@1.9.10                                         |
| Font Awesome | https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css |

## API Endpoints

### Users

- `GET /users/` - List users
- `GET /users/create/` - Create user form
- `POST /users/create/` - Create user
- `GET /users/<id>/edit/` - Edit user form
- `POST /users/<id>/edit/` - Update user
- `GET /users/<id>/delete/` - Delete confirmation
- `POST /users/<id>/delete/` - Delete user

### Students

- `GET /students/` - List students
- `GET /students/create/` - Create student form
- `POST /students/create/` - Create student
- `GET /students/<id>/` - Student detail
- `GET /students/<id>/edit/` - Edit student form
- `POST /students/<id>/edit/` - Update student
- `GET /students/<id>/delete/` - Delete confirmation
- `POST /students/<id>/delete/` - Soft delete student

### Classes

- `GET /classes/` - List classes
- `GET /classes/create/` - Create class form
- `POST /classes/create/` - Create class
- `GET /classes/<id>/` - Class detail
- `GET /classes/<id>/edit/` - Edit class form
- `POST /classes/<id>/edit/` - Update class
- `GET /classes/<id>/delete/` - Delete confirmation
- `POST /classes/<id>/delete/` - Delete class

### Attendance

- `GET /class/<id>/sessions/` - List sessions
- `GET /class/<id>/sessions/create/` - Create session form
- `POST /class/<id>/sessions/create/` - Create session
- `GET /session/<id>/` - Session detail & attendance
- `POST /session/<id>/open/` - Open session
- `POST /session/<id>/end/` - End session
- `POST /attendance/<id>/mark/` - Mark attendance

### Payments

- `GET /tuitions/` - List tuitions
- `GET /tuitions/create/` - Create tuition form
- `POST /tuitions/create/` - Create tuition
- `GET /tuitions/<id>/` - Tuition detail
- `POST /tuitions/<id>/mark-paid/` - Mark as paid
- `GET /payments/history/` - Payment history
- `GET /my-tuitions/` - Parent's children tuition

## Domain Generation Logic

```python
# Example: "Nguyễn Văn Nam"
# - Last name: "Nguyễn" (cleaned, no spaces)
# - First name: "Văn Nam" (cleaned, no special chars)
# - Combined: "nguyễn" + "vănnam" = "nguyenvannam"
# - If exists, add counter: "nguyenvannam2"
```

## Rollback

```bash
# Rollback migrations
python manage.py migrate <app> zero

# Reset database
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```
