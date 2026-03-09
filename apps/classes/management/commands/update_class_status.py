from django.core.management.base import BaseCommand
from classes.tasks import auto_update_class_status

class Command(BaseCommand):
    help = 'Cập nhật tự động trạng thái của Lớp học và Học sinh dựa theo thời gian bắt đầu / kết thúc'

    def handle(self, *args, **options):
        self.stdout.write("Bắt đầu kiểm tra và cập nhật trạng thái lớp học...")
        
        # Gọi trực tiếp logic của task
        result = auto_update_class_status()
        
        self.stdout.write(self.style.SUCCESS(f"Hoàn tất. Kết quả: {result}"))
