from django.contrib import admin
from .models import ClassSession, Attendance, AttendanceEditLog


@admin.register(ClassSession)
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = ["class_enrolled", "teacher", "scheduled_date", "scheduled_start", "scheduled_end", "status", "actual_start", "actual_end"]
    list_filter = ["status", "scheduled_date", "class_enrolled"]
    search_fields = ["class_enrolled__class_code", "class_enrolled__class_name", "teacher__first_name", "teacher__last_name"]
    ordering = ["-scheduled_date", "-scheduled_start"]


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ["enrollment", "class_session", "status", "marked_by", "marked_at"]
    list_filter = ["status", "class_session__class_enrolled"]
    search_fields = ["enrollment__student__full_name", "class_session__class_enrolled__class_code"]
    readonly_fields = ["marked_at"]


@admin.register(AttendanceEditLog)
class AttendanceEditLogAdmin(admin.ModelAdmin):
    list_display = ["attendance", "old_status", "new_status", "edited_by", "reason", "edited_at"]
    list_filter = ["edited_at"]
    search_fields = ["attendance__enrollment__student__full_name", "reason"]
    readonly_fields = ["edited_at"]
