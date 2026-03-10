from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.apps import apps
from operator import attrgetter
from django.db import models
from django.views.decorators.http import require_http_methods
from accounts.models import User
from classes.models import Class
from attendance.models import ClassSession


@login_required
def user_list(request):
    if request.user.role != 'admin':
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')
    
    users = User.objects.filter(is_deleted=False)
    
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
        
    per_page = request.GET.get('per_page', 20)
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 20
    
    paginator = Paginator(users, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    extra_query = ''
    if search: extra_query += f'&search={search}'
    if role_filter: extra_query += f'&role={role_filter}'
    extra_query += f'&per_page={per_page}'
    
    return render(request, 'users/list.html', {
        'page_obj': page_obj,
        'search': search,
        'role_filter': role_filter,
        'per_page': per_page,
        'extra_query': extra_query,
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
        user.is_deleted = True
        user.is_active = False 
        user.save()
        messages.success(request, f'Đã xóa người dùng {username} ra khỏi hệ thống.')
        return redirect('users:list')
    
    return render(request, 'users/confirm_delete.html', {'delete_user': user})

@login_required
@require_http_methods(["POST"])
def user_toggle_lock(request, user_id):
    if request.user.role != 'admin':
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')
    
    user = get_object_or_404(User, id=user_id, is_deleted=False)
    
    if request.user.id == user.id:
        messages.error(request, 'Bạn không thể tự khóa/mở khóa chính mình.')
        return redirect('users:list')
        
    user.is_active = not user.is_active
    user.save()
    
    status_label = "mở khóa" if user.is_active else "khóa"
    messages.success(request, f'Đã {status_label} người dùng {user.get_full_name()}.')
    return redirect('users:list')

@login_required
def activity_logs(request):
    if request.user.role != 'admin':
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')
        
    histories = []
    from django.db.models import Q
    
    action_filter = request.GET.get('action', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    actor_name = request.GET.get('actor', '')
    
    # Fetch top 100 latest items from each tracked model
    for model in apps.get_models():
        if hasattr(model, 'history') and hasattr(model.history, 'all'):
            qs = model.history.all().select_related('history_user')
            
            if action_filter:
                qs = qs.filter(history_type=action_filter)
            if date_from:
                qs = qs.filter(history_date__gte=date_from)
            if date_to:
                qs = qs.filter(history_date__lte=date_to + " 23:59:59")
            if actor_name:
                qs = qs.filter(
                    Q(history_user__username__icontains=actor_name) |
                    Q(history_user__first_name__icontains=actor_name) |
                    Q(history_user__last_name__icontains=actor_name)
                )
                
            logs = qs.order_by('-history_date')[:100]
            clean_name = str(model._meta.verbose_name).title()
            for log in logs:
                log.model_name = clean_name
            histories.extend(logs)
        
    # Sort merged lists from all models manually in-memory
    histories.sort(key=lambda x: getattr(x, 'history_date', None), reverse=True)
    
    per_page = request.GET.get('per_page', 50)
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 50
        
    paginator = Paginator(histories, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate diffs only for the current page to avoid excessive queries
    for log in page_obj.object_list:
        log.changes = []
        if log.history_type == '~':
            try:
                prev = getattr(log, 'prev_record', None)
                if prev:
                    try:
                        delta = log.diff_against(prev)
                        for change in delta.changes:
                            if change.field not in ['history_id', 'history_user', 'history_date', 'history_type', 'history_change_reason', 'deleted_at', 'restored_at']:
                                log.changes.append(change)
                    except Exception:
                        pass
            except Exception:
                pass
    
    extra_query = f'&per_page={per_page}'
    if action_filter:
        extra_query += f'&action={action_filter}'
    if date_from:
        extra_query += f'&date_from={date_from}'
    if date_to:
        extra_query += f'&date_to={date_to}'
    if actor_name:
        extra_query += f'&actor={actor_name}'
    
    return render(request, 'users/activity_logs.html', {
        'page_obj': page_obj,
        'per_page': per_page,
        'extra_query': extra_query,
        'action_filter': action_filter,
        'date_from': date_from,
        'date_to': date_to,
        'actor': actor_name,
    })

@login_required
def object_history(request, app_label, model_name, object_id):
    if request.user.role not in ['admin', 'teacher', 'assistant']:
        messages.error(request, 'Bạn không có quyền xem thông tin này.')
        return redirect('dashboard')
        
    model = apps.get_model(app_label, model_name)
    instance = get_object_or_404(model, pk=object_id)
    
    if not hasattr(instance, 'history'):
        histories = []
    else:
        histories = list(instance.history.all().select_related('history_user').order_by('-history_date'))
        
        # Calculate diffs
        for i, log in enumerate(histories):
            log.changes = []
            if log.history_type == '~' and i + 1 < len(histories):
                prev_log = histories[i + 1]
                delta = log.diff_against(prev_log)
                for change in delta.changes:
                    # Ignore internal simple_history tracking fields if any
                    if change.field not in ['history_id', 'history_user', 'history_date', 'history_type', 'history_change_reason']:
                        log.changes.append(change)
        
    per_page = 5
    paginator = Paginator(histories, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'partials/object_history_modal.html', {
        'page_obj': page_obj,
        'app_label': app_label,
        'model_name': model_name,
        'object_id': object_id,
        'instance': instance,
    })
@login_required
def user_detail(request, user_id):
    if request.user.role not in ['admin', 'teacher', 'assistant']:
        messages.error(request, 'Bạn không có quyền xem thông tin này.')
        return redirect('dashboard')
        
    user_obj = get_object_or_404(User, id=user_id, is_deleted=False)
    
    context = {
        'user_obj': user_obj,
    }
    
    # If the user is a teacher, fetch teaching related data
    if user_obj.role == 'teacher':
        # --- Active Classes ---
        active_classes = Class.objects.filter(
            teacher=user_obj, 
            status='active',
            is_active=True
        ).select_related('subject').order_by('-start_date')
        
        # --- Completed Classes ---
        comp_search = request.GET.get('search_completed', '')
        completed_classes_qs = Class.objects.filter(
            teacher=user_obj, 
            status='completed',
            is_active=True
        ).select_related('subject').order_by('-end_date')
        
        if comp_search:
            completed_classes_qs = completed_classes_qs.filter(
                models.Q(class_code__icontains=comp_search) |
                models.Q(class_name__icontains=comp_search)
            )
            
        paginator_comp = Paginator(completed_classes_qs, 5)
        page_comp = request.GET.get('page_completed', 1)
        completed_classes = paginator_comp.get_page(page_comp)
        
        # --- Session Logs ---
        sess_search = request.GET.get('search_sessions', '')
        session_logs_qs = ClassSession.objects.filter(
            class_enrolled__teacher=user_obj
        ).select_related('class_enrolled__subject').order_by('-scheduled_date', '-scheduled_start')
        
        if sess_search:
            session_logs_qs = session_logs_qs.filter(
                models.Q(class_enrolled__class_code__icontains=sess_search) |
                models.Q(class_enrolled__class_name__icontains=sess_search)
            )
            
        paginator_sess = Paginator(session_logs_qs, 5)
        page_sess = request.GET.get('page_sessions', 1)
        session_logs = paginator_sess.get_page(page_sess)
        
        context.update({
            'active_classes': active_classes,
            'completed_classes': completed_classes,
            'session_logs': session_logs,
            'sess_search': sess_search,
            'comp_search': comp_search,
        })
        
        # Handle HTMX partial requests
        if request.headers.get('HX-Request'):
            if 'search_sessions' in request.GET or 'page_sessions' in request.GET:
                return render(request, 'users/partials/session_logs_table.html', context)
            if 'search_completed' in request.GET or 'page_completed' in request.GET:
                return render(request, 'users/partials/completed_classes_table.html', context)
        
    return render(request, 'users/user_detail.html', context)
