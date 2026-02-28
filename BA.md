# BA - Yêu cầu dự án LCMS
## Learning Center Management System - Hệ thống Quản lý Trung tâm Học tập

---

## 1. Tổng quan dự án

### 1.1 Mô tả dự án
Xây dựng hệ thống quản lý trung tâm học tập (Learning Center Management System - LCMS) giúp quản lý người dùng, học sinh, lớp học, điểm danh và học phí một cách hiệu quả.

### 1.2 Công nghệ sử dụng
- **Backend**: Django 5.0+ với Python
- **Frontend**: TailwindCSS (CDN), Alpine.js, HTMX
- **Database**: SQLite (development), PostgreSQL (production)
- **Authentication**: django-allauth

### 1.3 Đối tượng sử dụng
| Vai trò | Mô tả |
|---------|-------|
| Admin | Quản trị viên - toàn quyền hệ thống |
| Teacher | Giáo viên - quản lý lớp và điểm danh |
| Assistant | Trợ giảng - hỗ trợ giáo viên |
| Parent | Phụ huynh - xem thông tin con |

---

## 2. Yêu cầu chức năng

### 2.1 Xác thực & Phân quyền
- [x] Đăng nhập bằng email/username
- [x] Phân quyền theo vai trò (admin, teacher, assistant, parent)
- [x] Tự động tạo domain từ họ tên
- [x] Cấu hình trang admin tùy chỉnh (không dùng Django admin)

### 2.2 Quản lý người dùng (User Management)
- [x] Danh sách người dùng với phân trang
- [x] Tìm kiếm và lọc theo vai trò
- [x] Tạo người dùng mới
- [x] Chỉnh sửa thông tin người dùng
- [x] Xóa người dùng
- [x] Các trường: họ, tên, email, điện thoại, giới tính, vai trò

### 2.3 Quản lý học sinh (Student Management)
- [x] Danh sách học sinh với phân trang
- [x] Tìm kiếm và lọc theo trạng thái
- [x] Tạo học sinh mới
- [x] Xem chi tiết học sinh
- [x] Chỉnh sửa thông tin học sinh
- [x] Xóa mềm (soft delete) học sinh
- [x] Các trường bổ sung: năm sinh (birth_year), trường học (school)

### 2.4 Quản lý lớp học (Class Management)
- [x] Danh sách lớp học với phân trang
- [x] Tìm kiếm lớp học
- [x] Tạo lớp học mới
- [x] Tạo môn học mới ngay trong form tạo lớp (get_or_create)
- [x] Chỉnh sửa thông tin lớp học
- [x] Xóa lớp học
- [x] Xem chi tiết lớp học
- [x] Lịch học: chọn ngày trong tuần bằng checkbox
- [x] Giờ bắt đầu và kết thúc bằng time picker

### 2.5 Quản lý điểm danh (Attendance)
- [x] Tạo buổi học (ClassSession) cho từng lớp
- [x] Mở lớp điểm danh trước 15 phút
- [x] Tự động kết thúc sau 30 phút
- [x] Điểm danh học sinh: có mặt, vắng có phép, vắng không phép
- [x] Danh sách buổi học của giáo viên/trợ giảng

### 2.6 Quản lý học phí (Payment/Tuition)
- [x] Tạo học phí theo tháng hoặc theo khóa học
- [x] Theo dõi ngày đến hạn
- [x] Đánh dấu đã thanh toán
- [x] Lịch sử thanh toán
- [x] Phụ huynh xem học phí của con

---

## 3. Yêu cầu phi chức năng

### 3.1 Giao diện người dùng
- [x] Thiết kế responsive (desktop, tablet, mobile)
- [x] Giao diện SPA (Single Page Application) với HTMX
- [x] Sử dụng TailwindCSS cho styling
- [x] Alpine.js cho tương tác động
- [x] Sidebar điều hướng với menu động
- [x] Trang đăng nhập với gradient/glassmorphism

### 3.2 Trải nghiệm người dùng
- [x] Tải trang nhanh với HTMX
- [x] Chuyển trang mượt mà
- [x] Thông báo message sau thao tác
- [x] Xác nhận trước khi xóa

### 3.3 Bảo mật
- [x] CSRF protection (Django built-in)
- [x] Authentication required cho các trang nội bộ
- [x] Phân quyền theo vai trò
- [x] Password hashing (Django built-in)

---

## 4. Luật sinh domain (Domain Generation)

### 4.1 Quy tắc
```
Họ tên: Nguyễn Văn Nam
→ Họ (last_name): Nguyễn (không dấu cách)
→ Tên (first_name): Văn Nam (không số, không ký tự đặc biệt)
→ Domain: nguyenvannam
→ Nếu trùng: nguyenvannam2, nguyenvannam3, ...
```

### 4.2 Ví dụ
| Họ tên | Domain |
|--------|--------|
| Nguyễn Văn Nam | nguyenvannam |
| Trần Thị Hồng | tranthihong |
| Lê Hoàng Nam | lehoangnam |

---

## 5. Cấu trúc dữ liệu

### 5.1 User Model
| Trường | Loại | Mô tả |
|--------|------|-------|
| id | PK | |
| username | CharField | Tự động = domain |
| domain | CharField | Domain duy nhất |
| first_name | CharField | Tên |
| last_name | CharField | Họ |
| email | EmailField | Email |
| phone | CharField | Số điện thoại |
| gender | CharField | Giới tính (male/female/other) |
| role | CharField | Vai trò (admin/teacher/assistant/parent) |
| is_active | Boolean | Trạng thái hoạt động |

### 5.2 Student Model
| Trường | Loại | Mô tả |
|--------|------|-------|
| id | PK | |
| full_name | CharField | Họ và tên |
| domain | CharField | Domain duy nhất |
| birth_year | IntegerField | Năm sinh |
| school | CharField | Trường học |
| gender | CharField | Giới tính |
| emergency_call | CharField | SDT khẩn cấp |
| status | CharField | Trạng thái (active/inactive/deleted) |
| deleted_at | DateTimeField | Thời điểm xóa (soft delete) |

### 5.3 Class Model
| Trường | Loại | Mô tả |
|--------|------|-------|
| id | PK | |
| class_code | CharField | Mã lớp (duy nhất) |
| class_name | CharField | Tên lớp |
| subject | ForeignKey | Môn học |
| teacher | ForeignKey | Giáo viên |
| assistants | ManyToManyField | Trợ giảng |
| schedule_days | CharField | Ngày học (2,4,6) |
| start_time | TimeField | Giờ bắt đầu |
| end_time | TimeField | Giờ kết thúc |
| room | CharField | Phòng học |
| max_students | IntegerField | Sĩ số tối đa |
| is_active | Boolean | Trạng thái |

### 5.4 ClassSession Model
| Trường | Loại | Mô tả |
|--------|------|-------|
| id | PK | |
| class_enrolled | ForeignKey | Lớp học |
| teacher | ForeignKey | Giáo viên |
| scheduled_date | DateField | Ngày học |
| scheduled_start | TimeField | Giờ bắt đầu |
| scheduled_end | TimeField | Giờ kết thúc |
| actual_start | DateTimeField | Thời điểm thực tế bắt đầu |
| actual_end | DateTimeField | Thời điểm thực tế kết thúc |
| status | CharField | Trạng thái |

### 5.5 Attendance Model
| Trường | Loại | Mô tả |
|--------|------|-------|
| id | PK | |
| class_session | ForeignKey | Buổi học |
| enrollment | ForeignKey | Học sinh đăng ký |
| status | CharField | Trạng thái điểm danh |
| marked_by | ForeignKey | Người điểm danh |
| marked_at | DateTimeField | Thời điểm điểm danh |

### 5.6 Tuition Model
| Trường | Loại | Mô tả |
|--------|------|-------|
| id | PK | |
| enrollment | ForeignKey | Đăng ký học |
| tuition_type | CharField | Loại (monthly/course) |
| month | CharField | Tháng (YYYY-MM) |
| course_name | CharField | Tên khóa học |
| amount | DecimalField | Số tiền |
| due_date | DateField | Ngày đến hạn |
| paid | Boolean | Đã thanh toán |
| paid_at | DateTimeField | Thời điểm thanh toán |
| payment_method | CharField | Phương thức |

---

## 6. API Endpoints

### 6.1 Authentication
- `GET /accounts/login/` - Trang đăng nhập
- `POST /accounts/login/` - Xử lý đăng nhập
- `GET /accounts/logout/` - Đăng xuất
- `GET /dashboard/` - Trang chủ

### 6.2 Users (Admin)
- `GET /users/` - Danh sách
- `GET /users/create/` - Tạo mới
- `POST /users/create/` - Lưu mới
- `GET /users/<id>/edit/` - Chỉnh sửa
- `POST /users/<id>/edit/` - Lưu chỉnh sửa
- `GET /users/<id>/delete/` - Xác nhận xóa
- `POST /users/<id>/delete/` - Xóa

### 6.3 Students
- `GET /students/` - Danh sách
- `GET /students/create/` - Tạo mới
- `POST /students/create/` - Lưu mới
- `GET /students/<id>/` - Chi tiết
- `GET /students/<id>/edit/` - Chỉnh sửa
- `POST /students/<id>/edit/` - Lưu chỉnh sửa
- `GET /students/<id>/delete/` - Xác nhận xóa
- `POST /students/<id>/delete/` - Xóa mềm
- `GET /my-children/` - Con của phụ huynh

### 6.4 Classes
- `GET /classes/` - Danh sách
- `GET /classes/create/` - Tạo mới
- `POST /classes/create/` - Lưu mới
- `GET /classes/<id>/` - Chi tiết
- `GET /classes/<id>/edit/` - Chỉnh sửa
- `POST /classes/<id>/edit/` - Lưu chỉnh sửa
- `GET /classes/<id>/delete/` - Xác nhận xóa
- `POST /classes/<id>/delete/` - Xóa
- `GET /my-classes/` - Lớp của giáo viên/trợ giảng

### 6.5 Attendance
- `GET /class/<id>/sessions/` - Danh sách buổi học
- `GET /class/<id>/sessions/create/` - Tạo buổi học
- `POST /class/<id>/sessions/create/` - Lưu buổi học
- `GET /session/<id>/` - Chi tiết & điểm danh
- `POST /session/<id>/open/` - Mở lớp
- `POST /session/<id>/end/` - Kết thúc
- `POST /attendance/<id>/mark/` - Đánh dấu điểm danh
- `GET /my-sessions/` - Buổi học của tôi

### 6.6 Payments
- `GET /tuitions/` - Danh sách học phí
- `GET /tuitions/create/` - Tạo học phí
- `POST /tuitions/create/` - Lưu học phí
- `GET /tuitions/<id>/` - Chi tiết
- `POST /tuitions/<id>/mark-paid/` - Đánh dấu đã trả
- `GET /payments/history/` - Lịch sử thanh toán
- `GET /my-tuitions/` - Học phí của con

---

## 7. Giao diện (UI/UX)

### 7.1 Layout
- Sidebar bên trái cố định (collapse trên mobile)
- Header top với user dropdown
- Content chính bên phải
- Full-screen, không bị giới hạn chiều rộng

### 7.2 Components
- Cards với shadow nhẹ
- Tables với hover effects
- Forms với floating labels
- Buttons với hover animations
- Badges cho trạng thái
- Alerts cho messages

### 7.3 Colors
- Primary: Blue (#3b82f6)
- Success: Green
- Warning: Amber
- Danger: Red
- Gray cho text và borders

---

## 8. Triển khai

### 8.1 Cài đặt
```bash
# Tạo virtual environment
python -m venv venv
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy migrations
python manage.py migrate

# Tạo superuser
python manage.py createsuperuser

# Chạy server
python manage.py runserver
```

### 8.2 Tài khoản mặc định
- Email: admin@lcms.com
- Password: admin123

---

## 9. Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0 | 2026-02-27 | Initial release with all features |
