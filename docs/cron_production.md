# Hướng dẫn thiết lập Cronjob trên Server Production

Ở môi trường Production (thường là Linux Ubuntu/Debian), cách đơn giản và phổ biến nhất để chạy các công việc ngầm (Background Job/Daemon) mà không cần cài thêm thư viện phức tạp là sử dụng **Crontab**.

### Cách 1: Sử dụng Crontab (Khuyên dùng)

Trình lên lịch mặc định của Linux giúp bạn kích hoạt script Django `generate_daily_sessions` tự động mỗi ngày:

1. Đăng nhập vào VPS/Server bằng SSH.
2. Gõ lệnh mở crontab:
   ```bash
   crontab -e
   ```
3. Khai báo chỉ thị chạy với đường dẫn **tuyệt đối** của source code trên Server (Giả sử thư mục code của bạn là `/var/www/lcms`):
   ```bash
   # Chạy vào 01:00 am mỗi ngày
   0 1 * * * /var/www/lcms/venv/bin/python /var/www/lcms/manage.py generate_daily_sessions >> /var/www/lcms/logs/cron.log 2>&1
   ```
   Lưu và thoát, Linux sẽ tự vào việc.

---

### Cách 2: Sử dụng Systemd Timers (Hệ thống lớn)

Nếu dùng Ubuntu, có thể dùng `systemd` cho bài bản để quản lý log dễ dàng hơn qua `journalctl`:

1. File Service: `/etc/systemd/system/lcms-daily-session.service`

   ```ini
   [Unit]
   Description=LCMS Daily Session Generator

   [Service]
   Type=oneshot
   User=www-data
   WorkingDirectory=/var/www/lcms
   ExecStart=/var/www/lcms/venv/bin/python manage.py generate_daily_sessions
   ```

2. File Timer (Schedule): `/etc/systemd/system/lcms-daily-session.timer`

   ```ini
   [Unit]
   Description=Run LCMS Task daily at 1AM

   [Timer]
   OnCalendar=*-*-* 01:00:00
   Persistent=true

   [Install]
   WantedBy=timers.target
   ```

   Khởi động timer: `sudo systemctl enable --now lcms-daily-session.timer`

---

### Cách 3: Sử dụng Celery (Cho quy mô Scale lớn)

Nếu LCMS sau này có nhu cầu bắn Email hàng loạt, tự động xuất file Excel cực nặng, hay tạo Notification real-time:
Việc nâng cấp lên sử dụng thư viện **Celery** kẹp chung với **Redis** sẽ là hướng đi chính thống.
Lúc này Command `generate_daily_sessions` sẽ được chuyển thành một `@shared_task` nằm trong thư mục `apps/attendance/tasks.py` và sẽ do `Celery Beat` tự điều phối. Tuy nhiên, nếu hiện tại dự án mới chỉ có 1 job auto tạo Session đơn giản này, thì áp dụng Celery là hơi rườm rà (over-engineering), bạn có thể xài Cách 1 cho khỏe.
