from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models
from .models import Class, Subject


@login_required
def class_list(request):
    if request.user.role != 'admin':
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')
    
    classes = Class.objects.all().select_related('subject', 'teacher')
    
    search = request.GET.get('search', '')
    if search:
        classes = classes.filter(
            models.Q(class_name__icontains=search) |
            models.Q(class_code__icontains=search) |
            models.Q(teacher__first_name__icontains=search) |
            models.Q(teacher__last_name__icontains=search)
        )
    
    per_page = request.GET.get('per_page', 30)
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 30
        
    paginator = Paginator(classes, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    extra_query = ''
    if search: extra_query += f'&search={search}'
    extra_query += f'&per_page={per_page}'
    
    return render(request, 'classes/list.html', {
        'page_obj': page_obj,
        'search': search,
        'per_page': per_page,
        'extra_query': extra_query,
    })


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
        
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        room = request.POST.get('room', '').strip()
        max_students = request.POST.get('max_students', 30)
        
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
            start_time=start_time,
            end_time=end_time,
            room=room,
            max_students=max_students
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
    return render(request, 'classes/detail.html', {'class_obj': class_obj})


@login_required
def class_edit(request, class_id):
    if request.user.role != 'admin':
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')
    
    class_obj = get_object_or_404(Class, id=class_id)
    
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
        
        class_obj.start_time = request.POST.get('start_time')
        class_obj.end_time = request.POST.get('end_time')
        class_obj.room = request.POST.get('room', '').strip()
        class_obj.max_students = request.POST.get('max_students', 30)
        class_obj.save()
        
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
    
    if request.method == 'POST':
        class_name = class_obj.class_name
        class_obj.delete()
        messages.success(request, f'Đã xóa lớp {class_name}.')
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
