from django.core.management.base import BaseCommand
from apps.payments.tasks import generate_monthly_tuitions_task

class Command(BaseCommand):
    help = 'Triggers the Monthly Tuitions generation task synchronously for testing/manual runs.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Đang kích hoạt Task tạo học phí hàng tháng...")
        created_count = generate_monthly_tuitions_task()
        self.stdout.write(self.style.SUCCESS(f"Hoàn tất! Đã khởi tạo {created_count} record học phí."))
