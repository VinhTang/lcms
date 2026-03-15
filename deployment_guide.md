# 🚀 GIẢI PHÁP DEPLOY LCMS VỚI DOCKER COMPOSE (UBUNTU)

Đây là giải pháp toàn diện để bạn tự host dự án trên Server riêng (Ubuntu), đảm bảo tính ổn định, dễ quản lý và đầy đủ các thành phần (DB, Cache, Worker).

## 1. Thành phần hệ thống trong giải pháp này
- **Web (Django)**: Chạy bằng `Gunicorn`, phục vụ CSS/JS qua `WhiteNoise`.
- **Database (PostgreSQL)**: Lưu trữ dữ liệu chính.
- **Redis**: Làm "trạm trung chuyển" dữ liệu cho Celery.
- **Worker (Celery)**: Xử lý các tác vụ ngầm (gửi mail, dọn dẹp data...).
- **Beat (Celery)**: Lập lịch các tác vụ định kỳ.

## 2. Các file cấu hình đã được tạo
1. `Dockerfile`: Hướng dẫn Docker cách đóng gói code Python.
2. `docker-compose.yml`: Kiến trúc toàn hệ thống.
3. `docker-entrypoint.sh`: Script tự động chạy `migrate` và `collectstatic` mỗi khi bật server.
4. `.dockerignore`: Loại bỏ rác khi đóng gói.

## 3. Quy trình thực hiện trên Ubuntu Server

### Bước 1: Cài đặt Docker (Nếu chưa có)
Trên terminal của Ubuntu, chạy các lệnh sau:
```bash
# Cập nhật hệ thống
sudo apt update && sudo apt upgrade -y

# Cài đặt docker và docker-compose
sudo apt install docker.io docker-compose -y

# Cho phép user hiện tại dùng docker không cần sudo
sudo usermod -aG docker $USER
# (Sau đó logout và login lại để lệnh usermod có hiệu lực)
```

### Bước 2: Chuẩn bị code
```bash
# Di chuyển vào thư mục dự án (ví dụ clone từ git)
cd /path/to/lcms-portal

# Cấp quyền thực thi cho script khởi động
chmod +x docker-entrypoint.sh
```

### Bước 3: Khởi động hệ thống
```bash
# Build và chạy ngầm (detach mode)
docker-compose up --build -d
```

### Bước 4: Kiểm tra trạng thái
```bash
# Xem các container đang chạy
docker-compose ps

# Xem log nếu có lỗi
docker-compose logs -f web
```

## 4. Các lệnh quản lý quan trọng
- **Dừng hệ thống**: `docker-compose down`
- **Tạo Superuser (Admin)**: 
  `docker-compose exec web python manage.py createsuperuser`
- **Xem log Database**: `docker-compose logs -f db`
- **Restart lại app**: `docker-compose restart web`

## 5. Lưu ý về Production
1. **Security**: Hãy thay đổi password trong file `docker-compose.yml` (phần `POSTGRES_PASSWORD` và `DATABASE_URL`).
2. **Domain**: Cập nhật `ALLOWED_HOSTS` và `CSRF_TRUSTED_ORIGINS` trong `docker-compose.yml` thành domain thật của bạn.
3. **SSL**: Bạn nên cài thêm `Nginx` và `Certbot` làm Reverse Proxy phía trước Docker để có HTTPS (Port 443).
