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
        
        # Try to find user by email or username
        user = None
        if "@" in login_input:
            try:
                user_obj = User.objects.get(email=login_input)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        else:
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
    return render(request, "accounts/dashboard.html")
