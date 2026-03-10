from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Class, Subject, Enrollment
from payments.models import Tuition
from django.core.exceptions import ValidationError


@login_required
def class_list(request):
    if request.user.role != 'admin':
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')
    
    # --- Section 1: Active & Pending Classes ---
    active_base = Class.objects.filter(is_active=True).exclude(status='completed').select_related('subject', 'teacher')
    
    active_search = request.GET.get('active_search', '')
    if active_search:
        active_base = active_base.filter(
            models.Q(class_name__icontains=active_search) |
            models.Q(class_code__icontains=active_search) |
            models.Q(teacher__first_name__icontains=active_search) |
            models.Q(teacher__last_name__icontains=active_search)
        )
    
    active_status = request.GET.get('active_status', '')
    if active_status:
        active_base = active_base.filter(status=active_status)
    
    active_paginator = Paginator(active_base, 20)
    active_page_num = request.GET.get('active_page')
    active_page_obj = active_paginator.get_page(active_page_num)
    
    # --- Section 2: Completed Classes ---
    completed_base = Class.objects.filter(is_active=True, status='completed').select_related('subject', 'teacher')
    
    completed_search = request.GET.get('completed_search', '')
    if completed_search:
        completed_base = completed_base.filter(
            models.Q(class_name__icontains=completed_search) |
            models.Q(class_code__icontains=completed_search) |
            models.Q(teacher__first_name__icontains=completed_search) |
            models.Q(teacher__last_name__icontains=completed_search)
        )
    
    completed_paginator = Paginator(completed_base, 20)
    completed_page_num = request.GET.get('completed_page')
    completed_page_obj = completed_paginator.get_page(completed_page_num)
    
    context = {
        'active_page_obj': active_page_obj,
        'active_search': active_search,
        'active_status': active_status,
        
        'completed_page_obj': completed_page_obj,
        'completed_search': completed_search,
    }
    
    # HTMX Partial Handling
    if request.headers.get('HX-Target') == 'active-classes-container':
        return render(request, 'classes/partials/active_classes_table.html', context)
    if request.headers.get('HX-Target') == 'completed-classes-container':
        return render(request, 'classes/partials/completed_classes_table.html', context)
    
    return render(request, 'classes/list.html', context)


@login_required
def class_create(request):
    if request.user.role != 'admin':
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        class_code = request.POST.get('class_code', '').strip().replace(' ', '')
        class_name = request.POST.get('class_name', '').strip()
        
        new_subject = request.POST.get('new_subject', '').strip()
        subject_id = request.POST.get('subject')
        
        if new_subject:
            subject, created = Subject.objects.get_or_create(
                subject_name__iexact=new_subject,
                defaults={'subject_name': new_subject}
            )
            subject_id = subject.id
        elif not subject_id:
            messages.error(request, 'Vui lòng chọn hoặc tạo môn học.')
            return redirect('classes:create')
        
        teacher_id = request.POST.get('teacher')
        
        schedule_days = request.POST.getlist('schedule_days')
        schedule_days = ','.join(schedule_days)
        
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        start_date = start_date if start_date else None
        end_date = end_date if end_date else None
        
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        room = request.POST.get('room', '').strip()
        max_students = request.POST.get('max_students', 30)
        
        tuition_fee_raw = request.POST.get('tuition_fee', '').strip()
        tuition_fee = int(tuition_fee_raw) if tuition_fee_raw else None
        
        if not class_code or not class_name:
            messages.error(request, 'Mã lớp và tên lớp không được để trống.')
            return redirect('classes:create')
        
        if Class.objects.filter(class_code=class_code).exists():
            messages.error(request, 'Mã lớp đã tồn tại.')
            return redirect('classes:create')
        
        class_obj = Class.objects.create(
            class_code=class_code,
            class_name=class_name,
            subject_id=subject_id,
            teacher_id=teacher_id,
            schedule_days=schedule_days,
            start_date=start_date,
            end_date=end_date,
            start_time=start_time,
            end_time=end_time,
            room=room,
            max_students=max_students,
            tuition_fee=tuition_fee
        )
        
        messages.success(request, f'Đã tạo lớp {class_obj.class_name} thành công.')
        return redirect('classes:list')
    
    subjects = Subject.objects.filter(is_active=True)
    from accounts.models import User
    teachers = User.objects.filter(role='teacher', is_active=True)
    
    return render(request, 'classes/form.html', {
        'subjects': subjects,
        'teachers': teachers,
    })


@login_required
def class_detail(request, class_id):
    class_obj = get_object_or_404(Class, id=class_id)
    # Filter for active enrollments AND active students
    active_qs = class_obj.enrollments.filter(
        status='active', 
        student__status='active'
    ).select_related('student').order_by('student__full_name')
    
    paginator = Paginator(active_qs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'class_obj': class_obj,
        'page_obj': page_obj
    }
    
    if request.headers.get('HX-Target') == 'class-enrollments-container':
        return render(request, 'classes/partials/class_enrollments_table.html', context)
        
    return render(request, 'classes/detail.html', context)


@login_required
def class_edit(request, class_id):
    if request.user.role != 'admin':
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')
    
    class_obj = get_object_or_404(Class, id=class_id)
    
    if class_obj.status == 'completed':
        messages.error(request, f'Lớp {class_obj.class_name} đã kết thúc, không thể chỉnh sửa.')
        return redirect('classes:list')
    
    if request.method == 'POST':
        class_obj.class_name = request.POST.get('class_name', '').strip()
        
        new_subject = request.POST.get('new_subject', '').strip()
        subject_id = request.POST.get('subject')
        
        if new_subject:
            subject, created = Subject.objects.get_or_create(
                subject_name__iexact=new_subject,
                defaults={'subject_name': new_subject}
            )
            subject_id = subject.id
        elif subject_id:
            pass
        else:
            messages.error(request, 'Vui lòng chọn hoặc tạo môn học.')
            return redirect('classes:edit', class_id=class_id)
        
        class_obj.subject_id = subject_id
        class_obj.teacher_id = request.POST.get('teacher')
        
        schedule_days = request.POST.getlist('schedule_days')
        class_obj.schedule_days = ','.join(schedule_days)
        
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        class_obj.start_date = start_date if start_date else None
        class_obj.end_date = end_date if end_date else None
        
        class_obj.start_time = request.POST.get('start_time')
        class_obj.end_time = request.POST.get('end_time')
        class_obj.room = request.POST.get('room', '').strip()
        class_obj.max_students = request.POST.get('max_students', 30)
        
        tuition_fee_raw = request.POST.get('tuition_fee', '').strip()
        class_obj.tuition_fee = int(tuition_fee_raw) if tuition_fee_raw else None
        
        try:
            class_obj.save()
        except ValidationError as e:
            messages.error(request, e.message if hasattr(e, 'message') else str(e))
            return redirect('classes:edit', class_id=class_id)
        
        messages.success(request, f'Đã cập nhật lớp {class_obj.class_name}.')
        return redirect('classes:list')
    
    subjects = Subject.objects.filter(is_active=True)
    from accounts.models import User
    teachers = User.objects.filter(role='teacher', is_active=True)
    
    return render(request, 'classes/form.html', {
        'class_obj': class_obj,
        'subjects': subjects,
        'teachers': teachers,
    })


@login_required
def class_delete(request, class_id):
    if request.user.role != 'admin':
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')
    
    class_obj = get_object_or_404(Class, id=class_id)
    
    if class_obj.status == 'completed':
        messages.error(request, f'Lớp {class_obj.class_name} đã kết thúc, không thể xóa.')
        return redirect('classes:list')
    
    # Handle custom modal request (GET + HTMX)
    if request.method == 'GET' and request.headers.get('HX-Request'):
        return render(request, 'classes/partials/delete_modal.html', {'class_obj': class_obj})
    
    if request.method == 'POST':
        class_name = class_obj.class_name
        class_obj.delete()
        
        if request.headers.get('HX-Request') and not request.POST.get('from_modal'):
            # This handles the case if triggered from table but somehow skips modal (unlikely now)
            return HttpResponse("")
            
        messages.success(request, f'Đã xóa hoàn toàn lớp {class_name} và các dữ liệu liên quan.')
        return redirect('classes:list')
    
    return render(request, 'classes/confirm_delete.html', {'class_obj': class_obj})


@login_required
def my_classes(request):
    if request.user.role not in ['teacher', 'assistant']:
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')
    
    if request.user.role == 'teacher':
        classes = Class.objects.filter(teacher=request.user, is_active=True)
    else:
        classes = Class.objects.filter(assistants=request.user, is_active=True)
    
    return render(request, 'classes/my_classes.html', {'classes': classes})


def check_schedule_conflict(student, target_class):
    """
    Checks if enrolling the `student` into `target_class` causes a schedule overlap.
    Returns the conflicting Class object if an overlap exists, else None.
    """
    if not target_class.schedule_days or not target_class.start_time or not target_class.end_time:
        return None
        
    target_days = set(target_class.schedule_days.split(','))
    
    # Get active enrollments for this student
    active_enrollments = student.enrollments.filter(status='active').select_related('class_enrolled')
    
    for enrollment in active_enrollments:
        current_class = enrollment.class_enrolled
        
        # Skip if checking against the same class or if schedule is missing
        if current_class.id == target_class.id or not current_class.schedule_days or not current_class.start_time or not current_class.end_time:
            continue
            
        current_days = set(current_class.schedule_days.split(','))
        
        # Check if there's any common day
        if target_days.intersection(current_days):
            # Check time overlap
            # Overlap exists if: (StartA < EndB) and (StartB < EndA)
            if (target_class.start_time < current_class.end_time) and (current_class.start_time < target_class.end_time):
                return current_class
                
    return None


@login_required
def class_enroll_students(request, class_id):
    if request.user.role not in ['admin', 'teacher', 'assistant']:
        messages.error(request, 'Bạn không có quyền truy cập chức năng này.')
        return redirect('classes:detail', class_id=class_id)
        
    class_obj = get_object_or_404(Class, id=class_id)
    
    if request.method == 'POST':
        student_ids = request.POST.getlist('students')
        if not student_ids:
            messages.error(request, 'Vui lòng chọn ít nhất một học sinh.')
            return redirect('classes:detail', class_id=class_id)
            
        success_count = 0
        error_messages = []
        
        from students.models import Student
        from .models import Enrollment
        # Only enroll students who are currently active
        students_to_enroll = Student.objects.filter(id__in=student_ids, status='active')
        
        for student in students_to_enroll:
            # Check if already enrolled in this exact class
            if Enrollment.objects.filter(student=student, class_enrolled=class_obj, status='active').exists():
                error_messages.append(f"{student.full_name}: Đã ở trong lớp này.")
                continue
                
            conflict_class = check_schedule_conflict(student, class_obj)
            if conflict_class:
                error_messages.append(f"{student.full_name}: Trùng giờ với lớp {conflict_class.class_name}.")
                continue
                
            # If valid, create or update enrollment
            enrollment, created = Enrollment.objects.update_or_create(
                student=student,
                class_enrolled=class_obj,
                defaults={'status': 'active', 'dropped_at': None}
            )
            
            # Chỉ tạo học phí nếu lớp đang KHAI GIẢNG (status='active'), không tạo cho lớp chưa mở
            if created and class_obj.status == 'active':
                from django.utils import timezone
                import datetime
                import calendar
                
                current_date = timezone.localtime(timezone.now()).date()
                current_month_str = current_date.strftime('%Y-%m')
                
                # Calculate tuition details
                tuition_amount = class_obj.tuition_fee if class_obj.tuition_fee is not None else 0
                
                if class_obj.end_date and class_obj.end_date.strftime('%Y-%m') == current_month_str:
                    due_date = class_obj.end_date
                else:
                    _, last_day = calendar.monthrange(current_date.year, current_date.month)
                    due_date = current_date.replace(day=last_day)
                
                # Auto-create tuition record for the current month
                Tuition.objects.get_or_create(
                    enrollment=enrollment,
                    tuition_type='monthly',
                    month=current_month_str,
                    defaults={
                        'amount': tuition_amount,
                        'due_date': due_date
                    }
                )
                
            success_count += 1
            
        if success_count > 0:
            messages.success(request, f'Đã thêm thành công {success_count} học sinh vào lớp.')
            
        for error in error_messages:
            messages.error(request, error)
            
        return redirect('classes:detail', class_id=class_id)
        
    # GET request - return modal
    from students.models import Student
    from .models import Enrollment
    # Exclude students already active in this class and ensure they are active
    enrolled_student_ids = Enrollment.objects.filter(class_enrolled=class_obj, status='active').values_list('student_id', flat=True)
    available_students = Student.objects.filter(status='active').exclude(id__in=enrolled_student_ids).order_by('full_name')
    
    return render(request, 'classes/enroll_students_modal.html', {
        'class_obj': class_obj,
        'available_students': available_students
    })


@login_required
def drop_student(request, enrollment_id):
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Không có quyền'}, status=403)
    
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    
    if request.method == 'GET' and request.headers.get('HX-Request'):
        return render(request, 'classes/partials/confirm_drop_modal.html', {'enrollment': enrollment})
        
    if request.method == 'POST':
        student_name = enrollment.student.full_name
        class_name = enrollment.class_enrolled.class_name
        
        # 1. Update Enrollment Status
        from django.utils import timezone
        enrollment.status = 'dropped'
        enrollment.dropped_at = timezone.now()
        enrollment.save()
        
        # 2. Cleanup Tuition (Only current month if UNPAID)
        from payments.models import Tuition
        current_month = timezone.now().strftime('%Y-%m')
        
        Tuition.objects.filter(
            enrollment=enrollment,
            month=current_month,
            paid=False
        ).delete()
        
        messages.success(request, f'Đã gỡ học sinh {student_name} khỏi lớp {class_name}.')
        
        # Handle HTMX redirect
        if request.headers.get('HX-Request'):
            referer = request.POST.get('next_url') or request.META.get('HTTP_REFERER', '/')
            response = JsonResponse({'status': 'success'})
            response['HX-Redirect'] = referer
            return response
            
        next_url = request.POST.get('next_url')
        if next_url:
            return redirect(next_url)
            
        return redirect('classes:detail', class_id=enrollment.class_enrolled.id)

    return redirect('classes:detail', class_id=enrollment.class_enrolled.id)
