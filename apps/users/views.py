from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models
from django.views.decorators.http import require_http_methods
from accounts.models import User


@login_required
def user_list(request):
    if request.user.role != 'admin':
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')
    
    users = User.objects.all()
    
    search = request.GET.get('search', '')
    if search:
        users = users.filter(
            models.Q(first_name__icontains=search) |
            models.Q(last_name__icontains=search) |
            models.Q(email__icontains=search) |
            models.Q(domain__icontains=search)
        )
    
    role_filter = request.GET.get('role', '')
    if role_filter:
        users = users.filter(role=role_filter)
    
    paginator = Paginator(users, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'users/list.html', {
        'page_obj': page_obj,
        'search': search,
        'role_filter': role_filter,
    })


@login_required
def user_create(request):
    if request.user.role != 'admin':
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        gender = request.POST.get('gender', '')
        role = request.POST.get('role', 'teacher')
        
        password = request.POST.get('password', '').strip()
        if not password:
            password = 'Lcms@123'
        
        if not first_name or not last_name:
            messages.error(request, 'Họ và tên không được để trống.')
            return redirect('users:create')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email đã được sử dụng.')
            return redirect('users:create')
        
        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            gender=gender,
            role=role,
            password=password
        )
        
        messages.success(request, f'Đã tạo người dùng {user.get_full_name()} thành công.')
        return redirect('users:list')
    
    return render(request, 'users/form.html')


@login_required
def user_edit(request, user_id):
    if request.user.role != 'admin':
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.email = request.POST.get('email', '').strip()
        user.phone = request.POST.get('phone', '').strip()
        user.gender = request.POST.get('gender', '')
        user.role = request.POST.get('role', 'teacher')
        
        password = request.POST.get('password', '')
        if password:
            user.set_password(password)
        
        user.save()
        
        messages.success(request, f'Đã cập nhật người dùng {user.get_full_name()} thành công.')
        return redirect('users:list')
    
    return render(request, 'users/form.html', {'edit_user': user})


@login_required
def user_delete(request, user_id):
    if request.user.role != 'admin':
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.user.id == user.id:
        messages.error(request, 'Bạn không thể xóa chính mình.')
        return redirect('users:list')
    
    if request.method == 'POST':
        username = user.get_full_name()
        user.delete()
        messages.success(request, f'Đã xóa người dùng {username}.')
        return redirect('users:list')
    
    return render(request, 'users/confirm_delete.html', {'delete_user': user})
