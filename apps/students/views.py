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
    
    status_filter = request.GET.get('status', '')
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
    return render(request, 'students/detail.html', {'student': student})


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
