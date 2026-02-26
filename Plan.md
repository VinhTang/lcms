Project Context: Education Center Management System

#### 1. Overview

This project is a web-based Education Center Management System built using:

- Backend: Django (server-rendered architecture)
- Frontend Rendering: Django Templates
- Dynamic Interactions: HTMX
- Lightweight Client Interactivity: Alpine.js
- Styling: TailwindCSS
- The system is designed to manage operations of a private education center, including students, teachers, assistants, parents, attendance, and tuition tracking.
- The architecture follows a server-rendered, progressive enhancement approach, avoiding heavy SPA frameworks such as React or Vue.
- The goal is to build a maintainable, scalable, and production-ready system with minimal frontend complexity.

#### 2. Technology Stack

Backend

- Django
- PostgreSQL (production)
- SQLite (development)

Frontend

- Django Templates
- HTMX (AJAX + partial updates)
- Alpine.js (UI state handling, modals, toggles)
- TailwindCSS (utility-first styling)

Optional Future Extensions

- Django Channels (WebSocket)
- Celery (background tasks)
- Docker deployment

#### 3. Architecture Philosophy

This project follows:

- Server-Side Rendering (SSR)
- HTML-over-the-wire pattern (HTMX)
- Minimal JavaScript
- Componentized template structure
- Role-based access control
- All business logic remains on the server.
- The frontend is responsible only for:
  - UI behavior (Alpine.js)
  - Partial updates (HTMX)
  - Styling (TailwindCSS)
- Use template in folder `startbootstrap-template`

#### 4. User Roles

##### 4.1. Admin

- Full system access
- Manage users (Teachers, Assistants, Parents)
- Manage students and classes
- View attendance reports (Teacher, Student)
- Manage tuition and payments

##### 4.2. Teacher

- View/Check-in assigned classes
- Mark attendance
- View student list

##### 4.3. Teaching Assistant

- Assist attendance marking
- View assigned classes

##### 4.4. Parent

- View child information
- Check attendance history
- View payment status

#### 5. Core Functional Modules

##### 5.1 Authentication & Authorization

- Django authentication system ( 2 option login via Google or localpassword)
- Role-based permission control
- Access restriction per role

##### 5.2 Class Management

- Create / Edit / Delete classes
- Assign teachers and assistants
- Assign students to classes

##### 5.3 Student Management

- Add / Edit / Delete students
- Link students to parents
- Track status (active/inactive)

##### 5.4 Attendance System (HTMX-driven)

Attendance flow:

- Teacher opens class detail page (check-in class in system)
- Student list is rendered server-side
- Teacher clicks “Present” / “Absent”
- HTMX sends POST request
- Server updates attendance record
- Server returns updated HTML partial
- HTMX swaps DOM section without page reload
  Optional:
  - Auto-refresh list via HTMX polling
  - WebSocket support in future
  - Alpine.js may be used for:
  - Dropdown filters
  - Toggle views
  - Modal confirmations

##### 5.5 Tuition & Payment Tracking

- Record payments
- Track outstanding balances
- View payment history
- Admin-only editing permissions

#### 6. Frontend Behavior Design

- HTMX Usage
- hx-post for form submissions
- hx-get for dynamic content loading
- hx-trigger for polling (optional)
- hx-target + hx-swap for partial updates
- Alpine.js Usage
- UI state (dropdown open/close)
- Modal visibility
- Confirmation dialogs
- Light interactive components
- No complex frontend state management.

#### 7. Template Structure Philosophy

- base.html (layout shell)
- components/ (reusable template components)
- partials/ (HTMX response fragments)
- pages/ (full page templates)
- Clear separation between:
  - Full page render
  - Partial HTML fragments for HTMX

#### 8. Non-Functional Requirements

- Clean modular app structure
- Production-ready architecture
- Easy to maintain and extend
- Minimal frontend build complexity
- Secure role-based access
- Mobile-friendly responsive layout

#### 9. Future Extensions

- Real-time WebSocket updates
- Dashboard analytics
- Export to Excel / PDF
- Parent notification system
- REST API for mobile app

#### 10. Design Principles

- Keep business logic in Django
- Return HTML, not JSON (unless necessary)
- Keep JavaScript minimal
- Prefer progressive enhancement
- Optimize developer productivity over frontend trendiness
