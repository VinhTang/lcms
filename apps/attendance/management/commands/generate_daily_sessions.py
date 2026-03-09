from django.core.management.base import BaseCommand
from tasks.attendance.tasks import generate_daily_sessions_task

class Command(BaseCommand):
    help = 'Triggers the Daily Class Sessions generation task synchronously for testing/manual runs.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Đang kích hoạt Task tạo tiết học hàng ngày...")
        created_count = generate_daily_sessions_task()
        self.stdout.write(self.style.SUCCESS(f"Hoàn tất! Đã khởi tạo {created_count} tiết học."))
