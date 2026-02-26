from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models
from django.http import JsonResponse
from datetime import datetime
from classes.models import Class, Enrollment
from .models import Tuition, PaymentHistory


@login_required
def tuition_list(request):
    if request.user.role != 'admin':
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')
    
    tuitions = Tuition.objects.all().select_related(
        'enrollment__student', 
        'enrollment__class_enrolled__subject'
    )
    
    search = request.GET.get('search', '')
    if search:
        tuitions = tuitions.filter(
            models.Q(enrollment__student__full_name__icontains=search) |
            models.Q(enrollment__class_enrolled__class_code__icontains=search) |
            models.Q(enrollment__class_enrolled__class_name__icontains=search) |
            models.Q(month__icontains=search)
        )
    
    status_filter = request.GET.get('status', '')
    if status_filter == 'paid':
        tuitions = tuitions.filter(paid=True)
    elif status_filter == 'unpaid':
        tuitions = tuitions.filter(paid=False)
    
    paginator = Paginator(tuitions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'payments/tuition_list.html', {
        'page_obj': page_obj,
        'search': search,
        'status_filter': status_filter,
    })


@login_required
def tuition_create(request):
    if request.user.role != 'admin':
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        enrollment_id = request.POST.get('enrollment')
        tuition_type = request.POST.get('tuition_type')
        month = request.POST.get('month', '').strip()
        course_name = request.POST.get('course_name', '').strip()
        amount = request.POST.get('amount')
        due_date = request.POST.get('due_date')
        
        if not enrollment_id or not amount or not due_date:
            messages.error(request, 'Vui lòng điền đầy đủ thông tin.')
            return redirect('payments:tuition_create')
        
        if tuition_type == 'monthly' and not month:
            messages.error(request, 'Vui lòng chọn tháng.')
            return redirect('payments:tuition_create')
        
        if tuition_type == 'course' and not course_name:
            messages.error(request, 'Vui lòng nhập tên khóa học.')
            return redirect('payments:tuition_create')
        
        Tuition.objects.create(
            enrollment_id=enrollment_id,
            tuition_type=tuition_type,
            month=month,
            course_name=course_name,
            amount=amount,
            due_date=due_date
        )
        
        messages.success(request, 'Đã tạo học phí thành công.')
        return redirect('payments:tuition_list')
    
    enrollments = Enrollment.objects.filter(status='active').select_related(
        'student', 'class_enrolled'
    )
    return render(request, 'payments/tuition_form.html', {'enrollments': enrollments})


@login_required
def tuition_detail(request, tuition_id):
    tuition = get_object_or_404(Tuition, id=tuition_id)
    payment_histories = tuition.payment_histories.all()
    return render(request, 'payments/tuition_detail.html', {
        'tuition': tuition,
        'payment_histories': payment_histories
    })


@login_required
def mark_paid(request, tuition_id):
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Không có quyền'}, status=403)
    
    tuition = get_object_or_404(Tuition, id=tuition_id)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', '')
        
        tuition.mark_as_paid(payment_method)
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'error': 'Invalid method'}, status=405)


@login_required
def get_enrollment_tuitions(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    tuitions = enrollment.tuitions.all()
    
    data = [{
        'id': t.id,
        'month': t.month,
        'course_name': t.course_name,
        'amount': str(t.amount),
        'due_date': t.due_date.strftime('%Y-%m-%d'),
        'paid': t.paid
    } for t in tuitions]
    
    return JsonResponse({'tuitions': data})


@login_required
def payment_history(request):
    if request.user.role != 'admin':
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')
    
    histories = PaymentHistory.objects.all().select_related(
        'tuition__enrollment__student',
        'tuition__enrollment__class_enrolled'
    )[:100]
    
    return render(request, 'payments/payment_history.html', {'histories': histories})


@login_required
def my_tuitions(request):
    if request.user.role != 'parent':
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')
    
    from students.models import Student
    from classes.models import ParentStudent
    
    parent_students = ParentStudent.objects.filter(parent=request.user).select_related('student')
    student_ids = [ps.student.id for ps in parent_students]
    
    enrollments = Enrollment.objects.filter(
        student_id__in=student_ids,
        status='active'
    ).select_related('class_enrolled__subject', 'student')
    
    tuitions = Tuition.objects.filter(
        enrollment__in=enrollments
    ).select_related('enrollment__student', 'enrollment__class_enrolled__subject')
    
    return render(request, 'payments/my_tuitions.html', {'tuitions': tuitions})
