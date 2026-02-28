from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from classes.models import Class, Enrollment
from .models import ClassSession, Attendance


@login_required
def session_list(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    sessions = class_obj.sessions.all().order_by('-scheduled_date', '-scheduled_start')
    
    per_page = request.GET.get('per_page', 30)
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 30
    
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
def session_create(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    
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
        
        messages.success(request, f'Đã tạo buổi học ngày {scheduled_date}.')
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
    
    existing_student_ids = set(attendances.values_list('enrollment__student_id', flat=True))
    
    for enrollment in enrollments:
        if enrollment.student.id not in existing_student_ids:
            Attendance.objects.create(
                class_session=session,
                enrollment=enrollment,
                status='not_marked'
            )
    
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
        return JsonResponse({'error': 'Buổi học đã bắt đầu'}, status=400)
    
    session.open_class()
    return JsonResponse({'status': 'success', 'message': 'Đã mở lớp'})


@login_required
def end_session(request, session_id):
    session = get_object_or_404(ClassSession, id=session_id)
    
    if request.user.role not in ['admin', 'teacher', 'assistant']:
        return JsonResponse({'error': 'Không có quyền'}, status=403)
    
    if session.status != 'in_progress':
        return JsonResponse({'error': 'Buổi học chưa bắt đầu'}, status=400)
    
    session.end_class()
    return JsonResponse({'status': 'success', 'message': 'Đã kết thúc buổi học'})


@login_required
def mark_attendance(request, attendance_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    attendance = get_object_or_404(Attendance, id=attendance_id)
    
    if request.user.role not in ['admin', 'teacher', 'assistant']:
        return JsonResponse({'error': 'Không có quyền'}, status=403)
    
    status = request.POST.get('status')
    valid_statuses = ['present', 'absent_with_permission', 'absent_without_permission', 'not_marked']
    
    if status not in valid_statuses:
        return JsonResponse({'error': 'Trạng thái không hợp lệ'}, status=400)
    
    attendance.mark(status, request.user)
    return JsonResponse({'status': 'success'})


@login_required
def my_sessions(request):
    if request.user.role not in ['teacher', 'assistant']:
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')
    
    sessions = ClassSession.objects.filter(
        class_enrolled__teacher=request.user
    ).select_related('class_enrolled__subject').order_by('-scheduled_date', '-scheduled_start')
    
    return render(request, 'attendance/my_sessions.html', {'sessions': sessions})
