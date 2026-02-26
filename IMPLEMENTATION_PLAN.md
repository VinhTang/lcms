# Implementation Plan - Education Center Management System (LCMS)

---

## 1. Project Overview

- **Project Name**: LCMS (Learning Center Management System)
- **Type**: Web Application
- **Backend**: Django 5.x (Server-rendered)
- **Frontend**: Django Templates + HTMX + Alpine.js + TailwindCSS
- **Database**: SQLite (dev) / PostgreSQL (prod)

---

## 2. Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | Django 5.x |
| Database | SQLite (dev), PostgreSQL (prod) |
| Auth | django-allauth + Google OAuth |
| Dynamic | HTMX |
| UI State | Alpine.js |
| Styling | TailwindCSS |
| Template | startbootstrap SB Admin 2 |

---

## 3. User Roles

| Role | Description |
|------|-------------|
| admin | Full system access |
| teacher | Teach max 2 classes, take attendance |
| assistant | Assist attendance for max 2 classes |
| parent | View child's info, attendance, payments |

---

## 4. Domain Generation Logic

```
Example: Nguyễn Văn Nam
├── First name: Nam
├── Last name: Nguyễn → N
└── Middle name: Văn → V

Domain = Nam + N + V = NamNV

If duplicate: NamNV2, NamNV3 (no NamNV1)
```

---

## 5. Database Schema

### 5.1 users (Custom User Model)

| Field | Type | Description |
|-------|------|-------------|
| id | PK | Auto increment |
| username | VARCHAR(150) | Unique |
| domain | VARCHAR(100) | Auto-generated: NamNV |
| password_hash | VARCHAR | Django auth |
| first_name | VARCHAR(100) | Required |
| last_name | VARCHAR(100) | Required |
| gender | VARCHAR(10) | male/female/other |
| phone | VARCHAR(20) | |
| email | EMAIL | |
| role | VARCHAR(20) | admin/teacher/assistant/parent |
| is_active | BOOLEAN | Default True |
| created_at | DATETIME | Auto now_add |

### 5.2 students

| Field | Type | Description |
|-------|------|-------------|
| id | PK | Auto increment |
| domain | VARCHAR(100) | Auto-generated, unique |
| full_name | VARCHAR(200) | Required |
| gender | VARCHAR(10) | male/female/other |
| emergency_call | VARCHAR(20) | Emergency phone |
| status | VARCHAR(20) | active/inactive/deleted |
| deleted_at | DATETIME | Nullable |
| restored_at | DATETIME | Nullable |
| created_at | DATETIME | Auto now_add |
| updated_at | DATETIME | Auto now |

### 5.3 subjects

| Field | Type | Description |
|-------|------|-------------|
| id | PK | Auto increment |
| subject_name | VARCHAR(200) | Required |
| description | TEXT | |
| is_active | BOOLEAN | Default True |

### 5.4 classes

| Field | Type | Description |
|-------|------|-------------|
| id | PK | Auto increment |
| class_code | VARCHAR(50) | Unique, no spaces |
| class_name | VARCHAR(200) | Required |
| subject_id | FK | subjects |
| teacher_id | FK | users (teacher) |
| assistants | M2M | users (optional) |
| schedule_days | VARCHAR(50) | e.g., "2,4,6" (Mon=1) |
| start_time | TIME | |
| end_time | TIME | |
| room | VARCHAR(100) | |
| max_students | INT | Default 30 |
| is_active | BOOLEAN | Default True |
| created_at | DATETIME | Auto now_add |

### 5.5 enrollments

| Field | Type | Description |
|-------|------|-------------|
| id | PK | Auto increment |
| student_id | FK | students |
| class_id | FK | classes |
| status | VARCHAR(20) | active/dropped |
| enrolled_at | DATETIME | Auto now_add |
| dropped_at | DATETIME | Nullable |

**Unique**: (student_id, class_id)

### 5.6 class_sessions (Nhật ký nhận lớp)

| Field | Type | Description |
|-------|------|-------------|
| id | PK | Auto increment |
| class_id | FK | classes |
| teacher_id | FK | users |
| scheduled_date | DATE | Ngày học theo lịch |
| scheduled_start | TIME | Giờ bắt đầu theo lịch |
| scheduled_end | TIME | Giờ kết thúc theo lịch |
| actual_start | DATETIME | Thời gian thực mở lớp |
| actual_end | DATETIME | Thời gian thực kết thúc |
| status | VARCHAR | not_started/in_progress/ended |
| notes | TEXT | Ghi chú |
| created_at | DATETIME | |

### 5.7 attendance

| Field | Type | Description |
|-------|------|-------------|
| id | PK | Auto increment |
| class_session_id | FK | class_sessions |
| enrollment_id | FK | enrollments |
| status | VARCHAR(30) | present/absent_with_permission/absent_without_permission/not_marked |
| marked_by_id | FK | users |
| marked_at | DATETIME | |
| notes | TEXT | |

**Default Status**: not_marked  
**Unique**: (class_session_id, enrollment_id)

### 5.8 attendance_edit_logs

| Field | Type | Description |
|-------|------|-------------|
| id | PK | Auto increment |
| attendance_id | FK | attendance |
| old_status | VARCHAR(30) | |
| new_status | VARCHAR(30) | |
| edited_by_id | FK | users |
| reason | TEXT | Required |
| edited_at | DATETIME | |

### 5.9 tuition

| Field | Type | Description |
|-------|------|-------------|
| id | PK | Auto increment |
| enrollment_id | FK | enrollments |
| tuition_type | VARCHAR | monthly/course |
| month | VARCHAR(7) | YYYY-MM (if monthly) |
| course_name | VARCHAR(200) | (if course) |
| amount | DECIMAL(10,2) | |
| due_date | DATE | |
| paid | BOOLEAN | Default False |
| paid_at | DATETIME | |
| payment_method | VARCHAR(50) | cash/transfer/card |
| notes | TEXT | |

**Unique**: (enrollment_id, month) OR (enrollment_id, course_name)

### 5.10 payment_histories

| Field | Type | Description |
|-------|------|-------------|
| id | PK | Auto increment |
| tuition_id | FK | tuition |
| amount | DECIMAL(10,2) | |
| paid_at | DATETIME | |
| payment_method | VARCHAR(50) | |
| notes | TEXT | |

### 5.11 parent_student

| Field | Type | Description |
|-------|------|-------------|
| id | PK | Auto increment |
| parent_id | FK | users (parent) |
| student_id | FK | students |
| relationship | VARCHAR(50) | father/mother/guardian |

**Unique**: (parent_id, student_id)

---

## 6. Functionality Matrix

### 6.1 Admin Capabilities

| Feature | Access |
|---------|--------|
| Manage all users | ✓ |
| Manage students (full CRUD + soft delete) | ✓ |
| Manage subjects | ✓ |
| Manage classes | ✓ |
| Assign teachers/assistants | ✓ |
| Take attendance (all classes) | ✓ |
| Edit/delete attendance (with reason) | ✓ |
| Manage tuition/payments | ✓ |
| View all reports | ✓ |
| Restore deleted students | ✓ |

### 6.2 Teacher Capabilities

| Feature | Access |
|---------|--------|
| Login/Logout | ✓ |
| View assigned classes (max 2) | ✓ |
| Open class (15min before → 30min after end) | ✓ |
| Take attendance for assigned classes | ✓ |
| End class session | ✓ |
| View students in assigned classes | ✓ |
| View attendance stats | ✓ |
| Cannot create/delete students | ✗ |
| Cannot manage tuition | ✗ |
| Cannot create classes/subjects | ✗ |
| Cannot view outside assigned classes | ✗ |
| Cannot edit attendance | ✗ |

### 6.3 Teaching Assistant Capabilities

| Feature | Access |
|---------|--------|
| Login/Logout | ✓ |
| View assigned classes (max 2) | ✓ |
| Assist attendance | ✓ |
| View students | ✓ |
| Cannot open/end class | ✗ |
| Cannot edit attendance | ✗ |

### 6.4 Parent Capabilities

| Feature | Access |
|---------|--------|
| Login/Logout | ✓ |
| View child's information | ✓ |
| View child's attendance | ✓ |
| View child's payments | ✓ |
| Cannot modify data | ✗ |

---

## 7. Attendance Logic

### 7.1 Class Session Flow

| Scenario | Action |
|----------|--------|
| Teacher opens class (15min before start) | ClassSession created, status=in_progress |
| Teacher marks attendance | Update attendance record |
| Teacher clicks "End class" | Unmarked students → not_marked |
| Auto-end (30min after end time) | Unmarked students → not_marked |
| Teacher doesn't open class | Students auto marked not_marked |

### 7.2 Attendance Status

| Status | Vietnamese | Description |
|--------|------------|-------------|
| present | Có mặt | Student attended |
| absent_with_permission | Vắng có phép | Absent with permission |
| absent_without_permission | Vắng không phép | Absent without permission |
| not_marked | Chưa điểm danh | Default, not yet marked |

### 7.3 Attendance Edit

- Admin can edit attendance anytime
- Required reason for edit
- Log stored in attendance_edit_logs

---

## 8. Tuition Management

| Feature | Access |
|---------|--------|
| Create tuition (monthly/course) | Admin only |
| Edit tuition | Admin only |
| Delete tuition | Admin only |
| Mark as paid | Admin only |
| View payment history | Admin + Parent |
| Statistics by class/month | Admin only |
| Payment reminders | Deferred to future |

---

## 9. URL Structure

```
/                           - Login/Landing
/dashboard/                 - Role-based dashboard
/accounts/                  - Authentication
    /login/                 - Login
    /logout/                - Logout
    /signup/                - Register

/students/                  - Student CRUD (Admin)
    /deleted/               - Deleted students list
    /<id>/restore/          - Restore student
/subjects/                  - Subject CRUD (Admin)
/classes/                   - Class CRUD (Admin)
    /<id>/attendance/       - Take attendance (Teacher)
    /<id>/enroll/           - Manage enrollments
/attendance/                - Reports (Admin)
    /<id>/edit/             - Edit attendance (Admin)
/tuition/                   - Tuition management (Admin)
    /<student_id>/          - Student tuition (Admin + Parent)

/class-sessions/            - Class session logs
    /<id>/                  - Session detail
    /<id>/open/             - Open class (Teacher)
    /<id>/end/              - End class (Teacher)
```

---

## 10. HTMX Patterns

| Action | HTMX |
|--------|------|
| Mark attendance | hx-post → swap row |
| Load class students | hx-get → target |
| Toggle modal | Alpine.js |
| Loading indicator | hx-indicator |

---

## 11. Implementation Phases

### Phase 1: Project Setup
- [x] Create IMPLEMENTATION_PLAN.md
- [ ] Create Django project `lcms`
- [ ] Install dependencies
- [ ] Configure settings
- [ ] Set up TailwindCSS
- [ ] Configure allauth (Google OAuth placeholder)

### Phase 2: Models
- [ ] Custom User model + Domain generation
- [ ] Student model + soft delete
- [ ] Subject model
- [ ] Class model + class_code
- [ ] Enrollment model
- [ ] ClassSession model
- [ ] Attendance model + EditLog
- [ ] Tuition model + PaymentHistory
- [ ] ParentStudent model

### Phase 3: Authentication
- [ ] Login/Register views
- [ ] Role-based redirects
- [ ] Permission decorators

### Phase 4: Admin Panel
- [ ] Register models
- [ ] CRUD operations

### Phase 5: Class Management
- [ ] Class CRUD
- [ ] Enrollment management
- [ ] Teacher assignment (max 2)
- [ ] Assistant (optional)

### Phase 6: Attendance System
- [ ] ClassSession (open/end)
- [ ] Attendance marking (HTMX)
- [ ] Auto-end logic
- [ ] Reports

### Phase 7: Tuition
- [ ] Tuition CRUD
- [ ] Payment tracking
- [ ] Reports

### Phase 8: Dashboard & Polish
- [ ] Role-based dashboards
- [ ] Responsive design

---

## 12. File Structure

```
lcms-portal/
├── lcms/                    # Django project
├── accounts/                # Authentication + User
├── students/                # Student management
├── classes/                 # Class + Enrollment
├── attendance/              # Attendance + ClassSession
├── payments/               # Tuition + PaymentHistory
├── templates/
├── static/
├── startbootstrap-template/
├── manage.py
├── requirements.txt
└── IMPLEMENTATION_PLAN.md
```
