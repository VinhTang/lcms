from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ["domain", "full_name", "gender", "status", "emergency_call", "created_at"]
    list_filter = ["status", "gender"]
    search_fields = ["domain", "full_name", "emergency_call"]
    ordering = ["-created_at"]
    readonly_fields = ["domain", "created_at", "updated_at"]
    
    actions = ["soft_delete_selected", "restore_selected"]

    def get_queryset(self, request):
        return super().get_queryset(request).filter(status__in=["active", "inactive"])

    def soft_delete_selected(self, request, queryset):
        for obj in queryset:
            obj.soft_delete()
    soft_delete_selected.short_description = "Xóa mềm các học sinh đã chọn"

    def restore_selected(self, request, queryset):
        for obj in queryset:
            obj.restore()
    restore_selected.short_description = "Khôi phục các học sinh đã chọn"
