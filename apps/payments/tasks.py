from celery import shared_task
from django.utils import timezone
import datetime
from classes.models import Enrollment
from payments.models import Tuition
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

@shared_task
def generate_monthly_tuitions_task():
    """
    Task định kỳ chạy mỗi tháng/ngày để sinh học phí (loại monthly)
    cho những học sinh đang học ở các lớp có thu phí.
    Hỗ trợ tạo bù các tháng còn thiếu tính từ khi lớp bắt đầu hoặc khi HS nhập học.
    """
    from dateutil.relativedelta import relativedelta
    import calendar
    
    now = timezone.localtime(timezone.now())
    current_date = now.date()
    current_month_start = current_date.replace(day=1)
    
    # Chỉ lấy enrollment của lớp đang KHAI GIẢNG (status='active'), bỏ qua lớp chưa mở (pending)
    active_enrollments = Enrollment.objects.filter(
        status='active',
        class_enrolled__status='active'
    ).select_related('class_enrolled', 'student')
    
    created_count = 0
    for enrollment in active_enrollments:
        class_obj = enrollment.class_enrolled
        
        # Xác định tháng bắt đầu tính phí: max(tháng lớp bắt đầu, tháng HS nhập học)
        class_start = class_obj.start_date if class_obj.start_date else enrollment.enrolled_at.date()
        enroll_start = enrollment.enrolled_at.date()
        
        start_date_calc = max(class_start, enroll_start)
        start_month_iter = start_date_calc.replace(day=1)
        
        # Xác định tháng kết thúc tính phí: min(tháng lớp kết thúc, tháng hiện tại)
        end_date_limit = current_date
        if class_obj.end_date and class_obj.end_date < current_date:
            end_date_limit = class_obj.end_date
        
        end_month_limit = end_date_limit.replace(day=1)
        
        # Duyệt qua từng tháng từ khi bắt đầu đến hiện tại
        current_iter = start_month_iter
        while current_iter <= end_month_limit:
            month_str = current_iter.strftime('%Y-%m')
            
            # Tính tuition_amount
            tuition_amount = class_obj.tuition_fee if class_obj.tuition_fee is not None else 0
            
            # Tính due_date cho tháng này
            if class_obj.end_date and class_obj.end_date.strftime('%Y-%m') == month_str:
                due_date = class_obj.end_date
            else:
                _, last_day = calendar.monthrange(current_iter.year, current_iter.month)
                due_date = current_iter.replace(day=last_day)
            
            # Kiểm tra xem record đã tồn tại chưa
            existing_tuition = Tuition.objects.filter(
                enrollment=enrollment,
                tuition_type='monthly',
                month=month_str
            ).first()

            if existing_tuition:
                # Nếu tồn tại nhưng chưa thanh toán và số tiền khác với thiết lập hiện tại -> Cập nhật
                if not existing_tuition.paid and existing_tuition.amount != tuition_amount:
                    existing_tuition.amount = tuition_amount
                    existing_tuition.due_date = due_date
                    existing_tuition.save()
                    created_count += 1
            else:
                # Tạo mới record (kể cả 0.00 để giữ tính nhất quán)
                Tuition.objects.create(
                    enrollment=enrollment,
                    tuition_type='monthly',
                    month=month_str,
                    amount=tuition_amount,
                    due_date=due_date
                )
                created_count += 1
            
            # Tăng lên 1 tháng
            current_iter += relativedelta(months=1)
            
    logger.info(f"Generated/Updated {created_count} monthly tuition records.")
    return created_count
