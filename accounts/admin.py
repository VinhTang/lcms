from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["domain", "get_full_name", "email", "role", "is_active"]
    list_filter = ["role", "is_active"]
    search_fields = ["domain", "first_name", "last_name", "email"]
    ordering = ["-date_joined"]

    fieldsets = BaseUserAdmin.fieldsets + (
        ("Thông tin bổ sung", {"fields": ("domain", "gender", "phone", "role")}),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Thông tin bổ sung", {"fields": ("gender", "phone", "role")}),
    )

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username
    get_full_name.short_description = "Họ tên"
