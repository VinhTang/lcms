from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Sum, Count, F, ExpressionWrapper, DurationField, Case, When
from datetime import datetime, timedelta
from classes.models import Class, Enrollment
from accounts.models import User
from .models import ClassSession, Attendance, AttendanceEditLog


@login_required
def session_list(request, class_id=None, class_code=None):
    if class_id:
        class_obj = get_object_or_404(Class, id=class_id)
    else:
        class_obj = get_object_or_404(Class, class_code=class_code)
        
    sessions = class_obj.sessions.all().order_by('-scheduled_date', '-scheduled_start')
    
    per_page = request.GET.get('per_page', 20)
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 20
    
    paginator = Paginator(sessions, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    extra_query = f'&per_page={per_page}'
    
    return render(request, 'attendance/session_list.html', {
        'class_obj': class_obj,
        'page_obj': page_obj,
        'per_page': per_page,
        'extra_query': extra_query,
    })


@login_required
def session_create(request, class_id=None, class_code=None):
    if class_id:
        class_obj = get_object_or_404(Class, id=class_id)
    else:
        class_obj = get_object_or_404(Class, class_code=class_code)
    
    if class_obj.status == 'completed':
        messages.error(request, f'Lớp {class_obj.class_name} đã kết thúc, không thể tạo thêm tiết học.')
        return redirect('attendance:session_list', class_id=class_obj.id)
    
    if class_obj.status == 'pending':
        messages.error(request, f'Lớp {class_obj.class_name} chưa khai giảng, không thể tạo tiết học.')
        return redirect('attendance:session_list', class_id=class_obj.id)
    
    if request.user.role not in ['admin', 'teacher', 'assistant']:
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        scheduled_date = request.POST.get('scheduled_date')
        
        if class_obj.start_time and class_obj.end_time:
            scheduled_start = class_obj.start_time
            scheduled_end = class_obj.end_time
        else:
            scheduled_start = request.POST.get('scheduled_start')
            scheduled_end = request.POST.get('scheduled_end')
        
        session = ClassSession.objects.create(
            class_enrolled=class_obj,
            teacher=request.user,
            scheduled_date=scheduled_date,
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
            status='not_started'
        )
        
        messages.success(request, f'Đã tạo tiết học ngày {scheduled_date}.')
        return redirect('attendance:session_detail', session_id=session.id)
    
    return render(request, 'attendance/session_form.html', {'class_obj': class_obj})


@login_required
def session_detail(request, session_id):
    session = get_object_or_404(ClassSession, id=session_id)
    attendances = session.attendances.all().select_related('enrollment__student')
    
    enrollments = Enrollment.objects.filter(
        class_enrolled=session.class_enrolled,
        status='active'
    )
    
    if session.status == 'not_started':
        existing_student_ids = set(attendances.values_list('enrollment__student_id', flat=True))
        
        for enrollment in enrollments:
            if enrollment.student.id not in existing_student_ids:
                Attendance.objects.create(
                    class_session=session,
                    enrollment=enrollment,
                    status='not_marked'
                )
        
        # Re-fetch after appending new enrollments
        attendances = session.attendances.all().select_related('enrollment__student')
    
    return render(request, 'attendance/session_detail.html', {
        'session': session,
        'attendances': attendances,
    })


@login_required
def open_session(request, session_id):
    session = get_object_or_404(ClassSession, id=session_id)
    
    if request.user.role not in ['admin', 'teacher', 'assistant']:
        return JsonResponse({'error': 'Không có quyền'}, status=403)
    
    if session.status != 'not_started':
        return JsonResponse({'error': 'Tiết học đã bắt đầu hoặc kết thúc'}, status=400)
        
    if session.class_enrolled.status == 'completed':
        return JsonResponse({'error': 'Lớp học đã kết thúc, không thể nhận lớp (mở tiết)'}, status=400)
    
    if session.class_enrolled.status == 'pending':
        return JsonResponse({'error': 'Lớp học chưa đến ngày khai giảng, không thể mở tiết học'}, status=400)
        
    now = timezone.now()
    scheduled_datetime = timezone.make_aware(datetime.combine(session.scheduled_date, session.scheduled_start))
    scheduled_end_datetime = timezone.make_aware(datetime.combine(session.scheduled_date, session.scheduled_end))
    
    if now < scheduled_datetime - timedelta(minutes=15):
        return JsonResponse({'error': 'Chưa đến giờ nhận lớp (chỉ được nhận trước 15 phút)'}, status=400)
        
    if now > scheduled_end_datetime:
        return JsonResponse({'error': 'Tiết học đã quát thời gian mở lớp'}, status=400)
    
    session.open_class()
    return JsonResponse({'status': 'success', 'message': 'Đã nhận lớp'})


@login_required
def end_session(request, session_id):
    session = get_object_or_404(ClassSession, id=session_id)
    
    if request.user.role not in ['admin', 'teacher', 'assistant']:
        return JsonResponse({'error': 'Không có quyền'}, status=403)
    
    if session.status != 'in_progress':
        return JsonResponse({'error': 'Tiết học chưa bắt đầu'}, status=400)
    
    session.end_class()
    return JsonResponse({'status': 'success', 'message': 'Đã kết thúc tiết học'})


@login_required
@require_POST
def save_session_notes(request, session_id):
    session = get_object_or_404(ClassSession, id=session_id)
    
    if request.user.role not in ['admin', 'teacher', 'assistant']:
        return JsonResponse({'error': 'Không có quyền'}, status=403)
        
    if session.status == 'ended':
        return JsonResponse({'error': 'Lớp học đã kết thúc không thể sửa ghi chú'}, status=400)
        
    notes = request.POST.get('notes', '')
    session.notes = notes
    session.save(update_fields=['notes'])
    
    return JsonResponse({'status': 'success'})




@login_required
def mark_attendance(request, attendance_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    attendance = get_object_or_404(Attendance, id=attendance_id)
    
    if request.user.role not in ['admin', 'teacher', 'assistant']:
        return JsonResponse({'error': 'Không có quyền'}, status=403)
        
    session_status = attendance.class_session.status
    is_admin = request.user.role == 'admin'
    
    if session_status == 'not_started':
        return JsonResponse({'error': 'Chưa thể điểm danh khi lớp chưa bắt đầu'}, status=400)
        
    if session_status == 'ended' and not is_admin:
        return JsonResponse({'error': 'Chỉ Admin mới có quyền sửa điểm danh khi lớp đã kết thúc'}, status=403)
    
    status = request.POST.get('status')
    reason = request.POST.get('reason', '').strip()
    
    valid_statuses = ['present', 'absent_with_permission', 'absent_without_permission', 'not_marked']
    
    if status not in valid_statuses:
        return JsonResponse({'error': 'Trạng thái không hợp lệ'}, status=400)
        
    if session_status == 'ended' and is_admin:
        if not reason:
            return JsonResponse({'error': 'Vui lòng nhập lý do thay đổi điểm danh'}, status=400)
            
        old_status = attendance.status
        if old_status != status:
            AttendanceEditLog.objects.create(
                attendance=attendance,
                old_status=old_status,
                new_status=status,
                edited_by=request.user,
                reason=reason
            )
            
            # Sync reason to the attendance notes for display in table
            admin_note = f"[Admin Edit: {reason}]"
            if attendance.notes:
                attendance.notes = f"{attendance.notes} | {admin_note}"
            else:
                attendance.notes = admin_note
            attendance.save(update_fields=['notes'])
    
    attendance.mark(status, request.user)
    return JsonResponse({'status': 'success'})


@login_required
def my_sessions(request):
    if request.user.role not in ['teacher', 'assistant']:
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')
    
    base_qs = ClassSession.objects.filter(
        class_enrolled__teacher=request.user
    ).select_related('class_enrolled__subject').order_by('-scheduled_date', '-scheduled_start')
    
    active_sessions = base_qs.filter(status__in=['not_started', 'in_progress'])
    history_sessions = base_qs.filter(status='ended')
    
    return render(request, 'attendance/my_sessions.html', {
        'active_sessions': active_sessions,
        'history_sessions': history_sessions
    })

@login_required
def session_statistics(request):
    if request.user.role != 'admin':
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')
        
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    teacher_id = request.GET.get('teacher_id', '')
    class_id = request.GET.get('class_id', '')
    
    qs = ClassSession.objects.all().select_related('class_enrolled', 'teacher', 'class_enrolled__subject')
    
    if date_from:
        qs = qs.filter(scheduled_date__gte=date_from)
    if date_to:
        qs = qs.filter(scheduled_date__lte=date_to)
        
    if teacher_id:
        qs = qs.filter(teacher_id=teacher_id)
        
    if class_id:
        qs = qs.filter(class_enrolled_id=class_id)
        
    # Aggregate Stats
    total_sessions = qs.count()
    ended_sessions = qs.count()  # This should be filtered
    ended_sessions = qs.filter(status='ended').count()
    in_progress_sessions = qs.filter(status='in_progress').count()
    not_started_sessions = qs.filter(status='not_started').count()

    selected_teacher_obj = None
    if teacher_id:
        selected_teacher_obj = User.objects.filter(id=teacher_id).first()
    
    selected_class_obj = None
    if class_id:
        selected_class_obj = Class.objects.filter(id=class_id).first()
    
    # Sort for display
    sessions = qs.order_by('-scheduled_date', '-scheduled_start')
    
    per_page = request.GET.get('per_page', 20)
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 20
        
    paginator = Paginator(sessions, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    teachers = User.objects.filter(role__in=['teacher', 'assistant'], is_active=True)
    teachers_options = [{'id': t.id, 'label': t.get_full_name() or t.username} for t in teachers]
    
    classes = Class.objects.all()
    classes_options = [{'id': c.id, 'label': f"{c.class_code} - {c.class_name}"} for c in classes]
    
    extra_query = ''
    if date_from: extra_query += f'&date_from={date_from}'
    if date_to: extra_query += f'&date_to={date_to}'
    if teacher_id: extra_query += f'&teacher_id={teacher_id}'
    if class_id: extra_query += f'&class_id={class_id}'
    if per_page != 50: extra_query += f'&per_page={per_page}'

    context = {
        'page_obj': page_obj,
        'total_sessions': total_sessions,
        'ended_sessions': ended_sessions,
        'in_progress_sessions': in_progress_sessions,
        'not_started_sessions': not_started_sessions,
        'teachers': teachers_options,
        'classes': classes_options,
        'date_from': date_from,
        'date_to': date_to,
        'selected_teacher': int(teacher_id) if teacher_id else '',
        'selected_teacher_label': selected_teacher_obj.get_full_name() or selected_teacher_obj.username if selected_teacher_obj else "Tất cả giáo viên",
        'selected_class': int(class_id) if class_id else '',
        'selected_class_label': f"{selected_class_obj.class_code} - {selected_class_obj.class_name}" if selected_class_obj else "Tất cả lớp",
        'extra_query': extra_query,
        'per_page': per_page
    }
    
    return render(request, 'attendance/session_statistics.html', context)
