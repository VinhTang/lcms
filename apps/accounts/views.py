from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    
    if request.method == "POST":
        login_input = request.POST.get("login")
        password = request.POST.get("password")
        
        # Pass directly to authenticate - the custom EmailDomainBackend handles resolving email vs domain
        user = authenticate(request, username=login_input, password=password)
        
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Tên đăng nhập hoặc mật khẩu không đúng")
    
    return render(request, "accounts/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role", "teacher")
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email đã được sử dụng")
            return redirect("register")
        
        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            role=role
        )
        
        login(request, user)
        return redirect("dashboard")
    
    return render(request, "accounts/register.html")


@login_required
def dashboard(request):
    context = {}
    if request.user.role == 'admin':
        from .models import User
        from students.models import Student
        from classes.models import Class
        from payments.models import Tuition
        
        context['total_users'] = User.objects.count()
        context['total_students'] = Student.objects.count()
        context['total_classes'] = Class.objects.count()
        context['unpaid_tuition'] = Tuition.objects.filter(paid=False).count()
        
    elif request.user.role in ['teacher', 'assistant']:
        from classes.models import Class, Enrollment
        from attendance.models import ClassSession
        
        my_classes = Class.objects.filter(teacher=request.user) if request.user.role == 'teacher' else Class.objects.filter(assistant=request.user)
        context['my_classes_count'] = my_classes.count()
        context['sessions_count'] = ClassSession.objects.filter(class_enrolled__in=my_classes, status='ended').count()
        context['my_students_count'] = Enrollment.objects.filter(class_enrolled__in=my_classes).values('student').distinct().count()
        
    elif request.user.role == 'parent':
        from payments.models import Tuition
        
        my_children = request.user.children.all()
        context['my_children_count'] = my_children.count()
        context['unpaid_tuition'] = Tuition.objects.filter(enrollment__student__in=my_children, paid=False).count()
        context['paid_tuition'] = Tuition.objects.filter(enrollment__student__in=my_children, paid=True).count()

    return render(request, "accounts/dashboard.html", context)
