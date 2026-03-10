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
    
    # 1. Filters logic
    search = request.GET.get('search', '')
    if search:
        tuitions = tuitions.filter(
            models.Q(enrollment__student__full_name__icontains=search) |
            models.Q(enrollment__student__domain__icontains=search) |
            models.Q(enrollment__class_enrolled__class_code__icontains=search) |
            models.Q(enrollment__class_enrolled__class_name__icontains=search) |
            models.Q(month__icontains=search)
        )
    
    class_id = request.GET.get('class_id', '')
    if class_id:
        tuitions = tuitions.filter(enrollment__class_enrolled_id=class_id)
        
    status_filter = request.GET.get('status', '')
    if status_filter == 'paid':
        tuitions = tuitions.filter(paid=True)
    elif status_filter == 'unpaid':
        tuitions = tuitions.filter(paid=False)
        
    date_from = request.GET.get('date_from', '')
    if date_from:
        tuitions = tuitions.filter(due_date__gte=date_from)
        
    date_to = request.GET.get('date_to', '')
    if date_to:
        tuitions = tuitions.filter(due_date__lte=date_to)
        
    month_filter = request.GET.get('month', '')
    if month_filter:
        tuitions = tuitions.filter(month=month_filter)

    # 2. Get data for dropdowns
    classes = Class.objects.filter(is_active=True).order_by('class_code')
    classes_options = [{'id': c.id, 'label': f"{c.class_code} - {c.class_name}"} for c in classes]
    
    # 3. Pagination
    per_page = request.GET.get('per_page', 20)
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 20
    
    paginator = Paginator(tuitions, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 4. Handle query parameters for pagination links
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    extra_query = f"&{query_params.urlencode()}" if query_params else ""

    selected_class_obj = None
    if class_id:
        selected_class_obj = Class.objects.filter(id=class_id).first()
    
    return render(request, 'payments/tuition_list.html', {
        'page_obj': page_obj,
        'search': search,
        'status_filter': status_filter,
        'selected_class': int(class_id) if class_id else '',
        'selected_class_label': f"{selected_class_obj.class_code} - {selected_class_obj.class_name}" if selected_class_obj else "Tất cả lớp",
        'date_from': date_from,
        'date_to': date_to,
        'month_filter': month_filter,
        'classes': classes_options,
        'per_page': per_page,
        'extra_query': extra_query,
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
        
        if request.headers.get('HX-Request'):
            referer = request.META.get('HTTP_REFERER', '/')
            response = JsonResponse({'status': 'success'})
            response['HX-Redirect'] = referer
            return response
            
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'error': 'Invalid method'}, status=405)


@login_required
def tuition_mark_paid_modal(request, tuition_id):
    if request.user.role != 'admin':
        return redirect('dashboard')
    
    tuition = get_object_or_404(Tuition, id=tuition_id)
    return render(request, 'payments/partials/mark_paid_modal.html', {'tuition': tuition})


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

@login_required
def get_student_info_partial(request):
    enrollment_id = request.GET.get('enrollment')
    if not enrollment_id:
        return render(request, 'payments/partials/student_info.html', {'student': None})
    
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    return render(request, 'payments/partials/student_info.html', {'student': enrollment.student})
