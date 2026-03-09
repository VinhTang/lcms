from django.core.management.base import BaseCommand
from tasks.attendance.tasks import auto_end_sessions_task

class Command(BaseCommand):
    help = 'Triggers the Auto End Class Sessions task synchronously for testing/manual runs.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Đang kích hoạt Task tự động kết thúc tiết học...")
        ended_count = auto_end_sessions_task()
        self.stdout.write(self.style.SUCCESS(f"Hoàn tất! Đã tự động kết thúc {ended_count} tiết học."))
