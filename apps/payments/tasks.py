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
    """
    now = timezone.localtime(timezone.now())
    current_date = now.date()
    current_month_str = current_date.strftime('%Y-%m')
    
    # Lấy enrolment đang active
    active_enrollments = Enrollment.objects.filter(
        status='active'
    ).select_related('class_enrolled')
    
    created_count = 0
    for enrollment in active_enrollments:
        class_obj = enrollment.class_enrolled
        
        # Lấy học phí, mặc định 0 nếu None
        tuition_amount = class_obj.tuition_fee if class_obj.tuition_fee is not None else 0
        
        # Chỉ sinh học phí nếu tháng hiện tại nằm trong thời gian của lớp học
        # Nếu start_date k có, xem như bắt đầu từ trước.
        if class_obj.start_date and current_date < class_obj.start_date.replace(day=1):
            continue
            
        # Nếu end_date k có, xem như ko thời hạn.
        # Nếu có end_date, chỉ sinh nếu tháng hiện tại chưa vượt quá tháng kết thúc
        if class_obj.end_date:
            end_month_str = class_obj.end_date.strftime('%Y-%m')
            if current_month_str > end_month_str:
                continue
                
        import calendar
        
        if class_obj.end_date and class_obj.end_date.strftime('%Y-%m') == current_month_str:
            due_date = class_obj.end_date
        else:
            _, last_day = calendar.monthrange(current_date.year, current_date.month)
            due_date = current_date.replace(day=last_day)
        
        tuition, created = Tuition.objects.get_or_create(
            enrollment=enrollment,
            tuition_type='monthly',
            month=current_month_str,
            defaults={
                'amount': tuition_amount,
                'due_date': due_date
            }
        )
        if created:
            created_count += 1
            
    logger.info(f"Generated {created_count} monthly tuitions for {current_month_str}.")
    return created_count
