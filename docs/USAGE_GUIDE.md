# Hướng dẫn sử dụng Hệ thống Quản lý Trung tâm (LCMS)

Chào mừng bạn đến với hệ thống LCMS. Tài liệu này cung cấp các bước cơ bản để cài đặt và vận hành hệ thống, bao gồm cả các tiến trình chạy ngầm (daemon).

## 1. Cài đặt môi trường

1.  **Clone repository** và truy cập vào thư mục dự án.
2.  **Tạo môi trường ảo (Virtual Env)**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Trên macOS/Linux
    # venv\Scripts\activate    # Trên Windows
    ```
3.  **Cài đặt các thư viện cần thiết**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Cập nhật cơ sở dữ liệu**:
    ```bash
    python manage.py migrate
    ```

## 2. Vận hành hệ thống

### Chạy Web Server
```bash
python manage.py runserver
```
Truy cập tại: `http://127.0.0.1:8000`

### Chạy các tiến trình ngầm (Daemon Jobs)
Hệ thống sử dụng **Celery** để xử lý các tác vụ tự động (như tính học phí, điểm danh tự động). Bạn cần có **Redis** đang chạy.

1.  **Chạy Celery Worker** (Để thực thi các task):
    ```bash
    celery -A lcms worker -l info
    ```

2.  **Chạy Celery Beat** (Để lập lịch các task định kỳ):
    ```bash
    celery -A lcms beat -l info
    ```

## 3. Danh sách các Job chạy tự động (Daemon Jobs)

Hệ thống đã cấu hình sẵn các job sau trong `lcms/celery.py`:

| Tên Job | Tác vụ | Tần suất |
| :--- | :--- | :--- |
| `generate-daily-sessions` | Tự động tạo các buổi học cho ngày mới | Hàng ngày (01:00 AM) |
| `auto-end-sessions` | Tự động kết thúc các buổi học đã hết giờ | Mỗi 5 phút |
| `generate-monthly-tuitions`| Tự động sinh biên lai học phí hàng tháng | Hàng ngày (02:00 AM) |
| `auto-update-class-status` | Cập nhật trạng thái lớp học (bắt đầu/kết thúc) | Hàng ngày (03:00 AM) |

## 4. Các tính năng nổi bật

- **Menu thu gọn (Sidebar)**: Bấm vào biểu tượng mũi tên trên thanh tiêu đề để thu gọn menu, giúp mở rộng không gian làm việc.
- **Thay đổi giao diện**: Bấm vào biểu tượng bảng màu (Palette) để chọn các tông màu rực rỡ hoặc chế độ tối (Dark Mode).
- **Điểm danh QR**: Quét mã QR của học sinh để ghi nhận điểm danh nhanh chóng.

---
*Lưu ý: Đảm bảo Redis Server đã được cài đặt và đang chạy trước khi khởi động Celery.*
