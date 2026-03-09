from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models
from .models import Student


@login_required
def student_list(request):
    if request.user.role != 'admin':
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')
    
    students = Student.objects.all()
    
    search = request.GET.get('search', '')
    if search:
        students = students.filter(
            models.Q(full_name__icontains=search) |
            models.Q(domain__icontains=search) |
            models.Q(emergency_call__icontains=search)
        )
    
    # Default to 'active' if 'status' isn't explicitly provided in GET params, 
    # but allow empty string '' to mean 'All statuses' if the user explicitly submitted the form.
    status_filter = request.GET.get('status', 'active')
    
    # If the user explicitly asks for "all" (which is an empty string in the dropdown value)
    if 'status' in request.GET and request.GET['status'] == '':
        status_filter = ''
        
    if status_filter:
        students = students.filter(status=status_filter)
        
    per_page = request.GET.get('per_page', 30)
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 30
    
    paginator = Paginator(students, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    extra_query = ''
    if search: extra_query += f'&search={search}'
    if status_filter: extra_query += f'&status={status_filter}'
    extra_query += f'&per_page={per_page}'
    
    return render(request, 'students/list.html', {
        'page_obj': page_obj,
        'search': search,
        'status_filter': status_filter,
        'per_page': per_page,
        'extra_query': extra_query,
    })


@login_required
def student_create(request):
    if request.user.role != 'admin':
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        gender = request.POST.get('gender', '')
        birth_year = request.POST.get('birth_year', '')
        school = request.POST.get('school', '').strip()
        emergency_call = request.POST.get('emergency_call', '').strip()
        
        if not full_name:
            messages.error(request, 'Tên học sinh không được để trống.')
            return redirect('students:create')
            
        force_create = request.POST.get('force_create')
        restore_user_id = request.POST.get('restore_user_id')

        if restore_user_id:
            student = get_object_or_404(Student, id=restore_user_id)
            student.full_name = full_name
            student.gender = gender
            student.birth_year = birth_year if birth_year else None
            student.school = school
            student.emergency_call = emergency_call
            student.status = 'active'
            student.save()
            messages.success(request, f'Đã khôi phục và cập nhật học sinh {student.full_name}.')
            return redirect('students:list')

        if not force_create:
            duplicate = Student.objects.filter(full_name__iexact=full_name)
            if birth_year:
                duplicate = duplicate.filter(birth_year=birth_year)
            duplicate_record = duplicate.first()
            
            if duplicate_record:
                temp_student = Student(
                    full_name=full_name,
                    gender=gender,
                    birth_year=birth_year if birth_year else None,
                    school=school,
                    emergency_call=emergency_call
                )
                return render(request, 'students/form.html', {
                    'student': temp_student,
                    'duplicate_student': duplicate_record
                })
        
        student = Student.objects.create(
            full_name=full_name,
            gender=gender,
            birth_year=birth_year if birth_year else None,
            school=school,
            emergency_call=emergency_call
        )
        
        messages.success(request, f'Đã thêm học sinh {student.full_name}.')
        return redirect('students:list')
    
    return render(request, 'students/form.html')


@login_required
def student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    # Lấy danh sách lớp đang học
    active_enrollments = student.enrollments.filter(status='active').select_related('class_enrolled__subject', 'class_enrolled__teacher').order_by('-enrolled_at')
    # Lấy danh sách lớp đã nghỉ/kết thúc
    completed_enrollments = student.enrollments.exclude(status='active').select_related('class_enrolled__subject', 'class_enrolled__teacher').order_by('-enrolled_at')
    
    # Lấy lịch sử học phí
    from payments.models import Tuition
    tuitions = Tuition.objects.filter(enrollment__student=student).select_related('enrollment__class_enrolled').order_by('-created_at')

    context = {
        'student': student,
        'active_enrollments': active_enrollments,
        'completed_enrollments': completed_enrollments,
        'tuitions': tuitions,
    }
    return render(request, 'students/detail.html', context)


@login_required
def student_edit(request, student_id):
    if request.user.role != 'admin':
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')
    
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        student.full_name = request.POST.get('full_name', '').strip()
        student.gender = request.POST.get('gender', '')
        birth_year = request.POST.get('birth_year', '')
        student.birth_year = birth_year if birth_year else None
        student.school = request.POST.get('school', '').strip()
        student.emergency_call = request.POST.get('emergency_call', '').strip()
        student.status = request.POST.get('status', 'active')
        student.save()
        
        messages.success(request, f'Đã cập nhật học sinh {student.full_name}.')
        return redirect('students:list')
    
    return render(request, 'students/form.html', {'student': student})


@login_required
def student_delete(request, student_id):
    if request.user.role != 'admin':
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')
    
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        student.soft_delete()
        messages.success(request, f'Đã xóa học sinh {student.full_name}.')
        return redirect('students:list')
    
    return render(request, 'students/confirm_delete.html', {'student': student})


@login_required
def my_children(request):
    if request.user.role != 'parent':
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')
    
    from classes.models import ParentStudent
    children = ParentStudent.objects.filter(parent=request.user).select_related('student')
    
    return render(request, 'students/my_children.html', {'children': children})


@login_required
def student_enroll_class(request, student_id):
    if request.user.role not in ['admin', 'teacher', 'assistant']:
        messages.error(request, 'Bạn không có quyền truy cập chức năng này.')
        return redirect('students:detail', student_id=student_id)
        
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        if not class_id:
            messages.error(request, 'Vui lòng chọn một lớp học.')
            return redirect('students:detail', student_id=student_id)
            
        from classes.models import Class, Enrollment
        from classes.views import check_schedule_conflict
        
        target_class = get_object_or_404(Class, id=class_id)
        
        # Check if already enrolled in this exact class
        if Enrollment.objects.filter(student=student, class_enrolled=target_class, status='active').exists():
            messages.error(request, f'Học sinh đã tham gia lớp {target_class.class_name}.')
            return redirect('students:detail', student_id=student_id)
            
        # Check schedule overlap
        conflict_class = check_schedule_conflict(student, target_class)
        if conflict_class:
            messages.error(request, f'Trùng lịch học với lớp {conflict_class.class_name} ({conflict_class.schedule_days} {conflict_class.start_time.strftime("%H:%M")}-{conflict_class.end_time.strftime("%H:%M")}).')
            return redirect('students:detail', student_id=student_id)
            
        # Proceed to enroll
        Enrollment.objects.update_or_create(
            student=student,
            class_enrolled=target_class,
            defaults={'status': 'active', 'dropped_at': None}
        )
        
        messages.success(request, f'Đã thêm học sinh vào lớp {target_class.class_name} thành công.')
        return redirect('students:detail', student_id=student_id)
        
    # GET request - return modal
    from classes.models import Class, Enrollment
    # Exclude classes this student is already active in
    enrolled_class_ids = Enrollment.objects.filter(student=student, status='active').values_list('class_enrolled_id', flat=True)
    available_classes = Class.objects.filter(is_active=True).exclude(id__in=enrolled_class_ids).order_by('class_name')
    
    return render(request, 'students/enroll_class_modal.html', {
        'student': student,
        'available_classes': available_classes
    })
